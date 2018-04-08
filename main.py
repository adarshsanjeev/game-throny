import copy
from typing import List, Tuple
import random

PLAYERS = 3
STEPS = 1

class Player(object):

    def __init__(self, id, attack=0, gold=50):
        self.id = id
        self.attack = attack
        self.gold = gold
        self.status = "ALIVE"

    def __add__(self, other: 'Player') -> 'Coalition':
        # FIXME: If player becomes part of coalition, and another player wants to target that player, will have invalid id possibly
        return Coalition([self, other])

    def get_intent(self):
        # Auro, this function --------
        # TODO: add a brain here. change later.
        # current suicide function
        self_copy = copy.copy(self)
        return Intent(self_copy, self_copy, "BATTLE")

    def __str__(self):
        return "Player %d: Attack: %d, Gold: %d, Status: %s" % (self.id, self.attack. self.gold, self.status)

    def __eq__(self, other):
        return self.id == other.id

class Coalition(Player):
    def __init__(self, players):
        super().__init__()
        self.players = players

    def __getattribute__(self, item):
        aggregates = ['attack', 'gold']
        if item in aggregates:
            attrs = self.aggregate_attr()
            return attrs[item]
        else:
            return object.__getattribute__(self, item)

    def aggregate_attr(self):
        aggregates = ['attack', 'gold']
        attrs = {}
        for i in aggregates:
            attrs[i] = sum([x.__dict__[i] for x in self.players])
        return attrs

    def __str__(self):
        return ";".join([i.__str__() for i in self.players])


class Intent(object):
    def __init__(self, player, target, type):
        self.player = player
        self.target = target
        self.type = type # Type is the type of move

    def __str__(self):
        return "Player %d targets %d with intent %s" % (self.player.id, self.target.id, self.type)


class Game(object):
    ATTACK_LOSS_FACTOR = 0.4
    GOLD_GAIN_FACTOR  = 0.6

    def __init__(self, players = 2):
        self.players = [Player(i+1, float(random.randint(10, 30)) ) for i in range(players)]
        self.coalitions = None
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

        intents = [x.get_intent() for x in self.players]
        for intent in intents:
            print(intent)

        self.form_coalitions(intents) # Sends request to player to accept or reject
        self.battle(intents)
        return self.check_state()

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
                    player.attack -= intent.target.attack*self.ATTACK_LOSS_FACTOR
                    player.gold += intent.target.gold*self.GOLD_GAIN_FACTOR
                else:
                    player.attack -= intent.target.attack*self.ATTACK_LOSS_FACTOR
                    target.attack -= intent.player.attack*self.ATTACK_LOSS_FACTOR

    def form_coalitions(self, intents):
        """
        Simulates coalition forming of players. Updates self.players()
        :return:
        """
        pass

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
    for player in game.players:
        print(vars(player))
    pass


if __name__ == '__main__':
    game = Game(PLAYERS)

    print("Initial")
    visualize(game)
    for step in range(STEPS):
        state = game.step()
        print("Step "+str(step+1))
        visualize(game)
        if state == "DONE":
            print("The winner is: Player "+str(game.winner))
            break
