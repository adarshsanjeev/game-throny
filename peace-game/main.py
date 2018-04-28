import copy
import random
from typing import List
from IPython import get_ipython
import ipdb
from tabulate import tabulate

MAX_PEACE_PERIOD = 3
PLAYERS = 5
STEPS = 10

ipython = get_ipython()

ipython.magic("%load_ext autoreload")
ipython.magic("%autoreload 2")

def simulate_move(game, intent):
    clone = copy.deepcopy(game)
    clone.battle([intent])
    return clone


class Player(object):
    def getScore(self, game):
        players = len(game.players)
        players_007 = len([i for i in game.players if i.attack > self.attack])
        coefficients = {
            'attack': lambda x:5,
            'gold': lambda x:10,
            # 'peace_dict': lambda x:len(x)
        }
        self_score = sum([coefficients[i](self.__dict__[i]) * self.__dict__[i] for i in coefficients], 0)
        return players + players_007 + self_score

    def utility(self, game, intent):
        a = self.getScore(game)
        print("updated")
        game_clone = simulate_move(game, intent)
        b = self.getScore(game_clone)
        ipdb.set_trace()

        return a-b
        # num players
        # no of player who can kill
        # your own stats
        # probability of being attacked

    def __init__(self, id, attack=0, gold=50):
        self.id = id
        self.attack = attack
        self.gold = gold
        self.status = "ALIVE"
        self.peace_dict = {}

    def get_intent(self, players):
        temp = list(self.peace_dict.keys()) + [self.id]
        players = [i for i in players if i.status == "ALIVE" ]
        possible_targets = list(filter(lambda x: x.id not in temp, players))
        print(self.id, "CAN TARGET" , possible_targets)
        if len(possible_targets) == 0:
            return None
        target = random.choice(possible_targets)
        if target.attack > self.attack:
            intent = "PEACE"
        else:
            intent = "BATTLE"
        return Intent(copy.copy(self), target, intent)

    def __repr__(self):
        return "Player %d" % (self.id)

    def __str__(self):
        return "Player %d: Attack: %f, Gold: %f, Status: %s, In peace with: %s" % (self.id, self.attack, self.gold, self.status, str(self.peace_dict))

    def request_peace(self, player):
        return True

    def __eq__(self, other):
        return self.id == other.id

    def set_peace(self, target, period=MAX_PEACE_PERIOD):
        self.peace_dict[target.id] = period

    def gain_gold(self, gold):
        self.gold += gold

    def suffer_loss(self, attack):
        self.attack -= attack

class HumanPlayer(Player):
    def get_intent(self):
        line = input().split(" ")
        intent = Intent(Player(self.id), Player(int(line[1])), line[0])
        if len(line) > 2:
            intent.gold = int(line[2])
        return intent

class Intent(object):
    def __init__(self, player, target, type, gold=0):
        self.player = player
        self.target = target
        self.type = type # Type is the type of move
        self.gold = gold

    def __str__(self):
        return "Player %d targets %d with intent %s with tribute %d" % (self.player.id, self.target.id, self.type, self.gold)


class Game(object):
    ATTACK_LOSS_FACTOR = 0.4
    GOLD_GAIN_FACTOR  = 0.6

    def __init__(self, players = 2):
        self.players = [Player(i+1, float(random.randint(10, 30)) ) for i in range(players)]
        self.winner = None

    def get_player(self, id):
        for player in self.players:
            if player.id==id:
                return player

    def validate_intents(self, intents):
        possible_targets = [i for i in self.players if i.status == "ALIVE" ]
        for intent in intents:
            p = possible_targets[possible_targets.index(intent.player)]
            if intent.gold > p.gold:
                print ("Not enough gold")
                return False
            if intent.player == intent.target:
                print ("Target is same as player")
                return False
            if intent.target not in possible_targets:
                print ("Not possible intent")
                return False
            if intent.type not in ["BATTLE", "PEACE", "FORTIFY"]:
                print ("Unknown intent")
                return False
        return True

    def step(self):
        """
        One time step of the game
        :return:
        """
        intents = []
        for x in self.players:
            if x.status == "ALIVE":
                intent = x.get_intent(self.players)
                if intent is not None:
                    intents += [intent]

        for intent in intents:
            print(intent)

        if self.validate_intents(intents) == False:
            print("Incorrect intents")
            return self.check_state()

        for intent in intents:
            if intent.type == "FORTIFY":
                player = self.players[self.players.index(intent.player)]
                if player.gold < 10:
                    print("Not enough gold")
                else:
                    player.gold -= 10
                    player.attack += 20

        self.battle(intents)
        self.handle_peace(intents)
        self.end_of_turn_calcs()
        return self.check_state()

    def end_of_turn_calcs(self):
        for player in self.players:
            players_to_remove = []
            for i in player.peace_dict:
                player.peace_dict[i] -= 1
                if player.peace_dict[i] == 0:
                    players_to_remove.append(i)
            for i in players_to_remove:
                player.peace_dict.pop(i)

    def battle(self, intents)-> List[Player]:
        """
        Simulates a battle
        :return: list(Player) Losers
        """

        for intent in intents:
            player = self.players[self.players.index(intent.player)]
            target = self.players[self.players.index(intent.target)]

            if intent.type == "BATTLE":
                if intent.player.attack > intent.target.attack:
                    target.status = "DEAD"
                    player.suffer_loss(intent.target.attack*self.ATTACK_LOSS_FACTOR)
                    player.gain_gold(intent.target.gold*self.GOLD_GAIN_FACTOR)
                else:
                    player.suffer_loss(intent.target.attack*self.ATTACK_LOSS_FACTOR)
                    target.suffer_loss(intent.player.attack*self.ATTACK_LOSS_FACTOR)

    def handle_peace(self, intents)-> List[Player]:
        """
        Simulates peace
        """

        for intent in intents:
            player = self.players[self.players.index(intent.player)]
            target = self.players[self.players.index(intent.target)]

            if intent.type == "PEACE":
                if target.request_peace(player) == True and player.gold >= intent.gold:
                    player.gold -= intent.gold
                    target.gold += intent.gold
                    player.set_peace(target)
                    target.set_peace(player)

    def check_state(self):
        num_alive = 0
        for player in self.players:
            if player.status=="ALIVE":
                num_alive += 1
                self.winner = player.id
        if num_alive <= 1:
            return "DONE"
        else:
            return "RUNNING"
        pass


def visualize(game):
    print(tabulate([vars(x) for x in game.players]))

if __name__ == '__main__':
    game = Game(PLAYERS)

    print("Initial")
    # visualize(game)
    for step in range(STEPS):
        state = game.step()
        print("Step "+str(step+1))
        visualize(game)
        if state == "DONE":
            if game.winner is None:
                print("All players died")
            else:
                print("The winner is: Player "+str(game.winner))
            break
