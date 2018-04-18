import copy
import random
from typing import List

from tabulate import tabulate

MAX_PEACE_PERIOD = 3
PLAYERS = 5
STEPS = 10

class Player(object):
    def __init__(self, id, attack=0, gold=50):
        self.id = id
        self.attack = attack
        self.gold = gold
        self.status = "ALIVE"
        self.peace_dict = {}

    def get_intent(self, players):
        # Auro, this function --------
        # TODO: add a brain here. change later.
        self_copy = copy.copy(self)
        while True:
            x = Player(random.randint(1, PLAYERS))
            if x.status=="ALIVE":
                return [Intent(self_copy, Player(random.randint(1, PLAYERS)), "BATTLE", 0)]

    def __repr__(self):
        return "Player %d" % (self.id)

    #def __str__(self):
    #    return "Player %d: Attack: %d, Gold: %d, Status: %s \n In peace with: %s" % (self.id, self.attack. self.gold, self.status, str(self.peace_dict))

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

    def step(self):
        """
        One time step of the game
        :return:
        """
        intents = []
        for x in self.players:
            intents += x.get_intent(self.players)

        for intent in intents:
            print(intent)

        self.battle(intents)
        self.handle_peace(intents)
        self.end_of_turn_calcs()
        return self.check_state()

    def end_of_turn_calcs(self):

        for player in self.players:
            for i in player.peace_dict:
                player.peace_dict[i] -= 1
                if player.peace_dict[i] == 0:
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
    visualize(game)
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
