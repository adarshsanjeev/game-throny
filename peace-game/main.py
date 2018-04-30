import copy
import random
from typing import List
#from IPython import get_ipython
from tabulate import tabulate

MAX_PEACE_PERIOD = 3
PLAYERS = 5
STEPS = 100
win = [0,0,0,0,0]

#ipython = get_ipython()

#ipython.magic("%load_ext autoreload")
#ipython.magic("%autoreload 2")

def simulate_move(game, intent):
    clone = copy.deepcopy(game)

    if intent.type == "FORTIFY":
        player = clone.players[clone.players.index(intent.player)]
        if player.gold > 10:
            player.gold -= 10
            player.attack += 50

    clone.battle([intent])
    clone.handle_peace([intent])
    return clone

class Player(object):
    def getScore(self, game):
        coeffs = [5, -1, -5, 1, 10]
        self_alive = (self.status=="ALIVE")
        alive_players = [i for i in game.players if i.status == "ALIVE"]
        players = len(alive_players)
        players_007 = len([i for i in alive_players if i.attack > self.attack and i!=self])
        fortified_check = 0
        for i in game.players:
            if i == self and i.attack > self.attack:
                fortified_check = 1
        coefficients = {
            'attack': lambda x:10,
            'gold': lambda x:0,
            # 'peace_dict': lambda x:len(x)
        }
        self_score = coeffs[0]*self_alive + coeffs[1]*players + coeffs[2]*players_007 + coeffs[3]*sum([coefficients[i](self.__dict__[i]) * self.__dict__[i] for i in coefficients], 0) + coeffs[4]*fortified_check
        return self_score

    def utility(self, game, intent):
        # num players
        # no of player who can kill
        # your own stats
        # probability of being attacked

        a = self.getScore(game)
        game_clone = simulate_move(game, intent)
        b = self.getScore(game_clone)
        return b-a

    def __init__(self, id, attack=0, gold=50):
        self.id = id
        self.attack = attack
        self.gold = gold
        self.status = "ALIVE"
        self.peace_dict = {}

    def get_intent(self, players):
        # print("############################################")
        # print("Thinking for player %d" % self.id)
        temp = list(self.peace_dict.keys()) + [self.id]
        players = [i for i in players if i.status == "ALIVE" ]
        possible_targets = list(filter(lambda x: x.id not in temp, players))
        if len(possible_targets) == 0:
            return Intent(self, self, "FORTIFY")
        highplayers = list(filter(lambda x: x.attack >= self.attack, possible_targets))
        lowplayers = list(filter(lambda x: x.attack < self.attack, possible_targets))
        # print("HIGH %s" % highplayers)
        # print("LOW %s" % lowplayers)
        max_util = self.utility(game, Intent(self, self, "FORTIFY"))
        max_intent = Intent(self, self, "FORTIFY")

        # print("HIGH")
        for player in highplayers:
            intent = Intent(copy.copy(self), copy.copy(player), "PEACE")
            new_util = self.utility(game, intent)
            # print(new_util)
            if new_util > max_util:
                max_util = new_util
                max_intent = intent

        # print("LOW")
        for player in lowplayers:
            intent = Intent(copy.copy(self), copy.copy(player), "BATTLE")
            new_util = self.utility(game, intent)
            # print(new_util)
            if new_util > max_util:
                max_util = new_util
                max_intent = intent

        # print("############################################")
        #print(max_intent, players)
        return max_intent

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

class RandomPlayer(Player):
    def get_intent(self, players):
        temp = list(self.peace_dict.keys()) + [self.id]
        players = [i for i in players if i.status == "ALIVE" ]
        possible_targets = list(filter(lambda x: x.id not in temp, players))
        if len(possible_targets) == 0:
            return None
        target = random.choice(possible_targets)
        if random.randint(0, 1)==0:
            intent = "PEACE"
        else:
            intent = "BATTLE"
        return Intent(copy.copy(self), target, intent)

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
        self.players = [Player(1)]
        self.players += [RandomPlayer(i+1, float(random.randint(10, 30)) ) for i in range(1, players)]
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
                # print ("Not enough gold")
                return False
            if intent.player == intent.target:
                # print ("Target is same as player")
                return False
            if intent.target not in possible_targets:
                # print ("Not possible intent")
                return False
            if intent.type not in ["BATTLE", "PEACE", "FORTIFY"]:
                # print ("Unknown intent")
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
            # print(intent)
            intent.target = copy.copy(intent.target)
            intent.player = copy.copy(intent.player)

        # if self.validate_intents(intents) == False:
        #     print("Incorrect intents")
        #     return self.check_state()

        for intent in intents:
            if intent.type == "FORTIFY":
                player = self.players[self.players.index(intent.player)]
                if player.gold < 10:
                    continue
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
        random.shuffle(intents)
        for intent in intents:
            player = self.players[self.players.index(intent.player)]
            target = self.players[self.players.index(intent.target)]

            if intent.type == "BATTLE":
                if intent.target.attack == "DEAD":
                    continue
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
        global win
        num_alive = 0
        for player in self.players:
            if player.status=="ALIVE":
                num_alive += 1
                self.winner = player.id
        #if self.winner == 1:
        if num_alive <= 1:
            win[self.winner-1] += 1
            return "DONE"
        else:
            return "RUNNING"
        pass

def visualize(game):
    print(tabulate([vars(x) for x in game.players]))

if __name__ == '__main__':
    for i in range(1000):
        game = Game(PLAYERS)

        #visualize(game)
        for step in range(STEPS):
            state = game.step()
            #visualize(game)
            #print("Step "+str(step+1))
            if state == "DONE":
                break
    print(win)
