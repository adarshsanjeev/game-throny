import copy
from typing import List, Tuple

class Player(object):
    def __init__(self, id, attack=0, gold=0):
        self.id = id
        self.attack = attack
        self.gold = gold
        self.status = "alive"

    def __add__(self, other: 'Player') -> 'Coalition':
        # FIXME: If player becomes part of coalition, and another player wants to target that player, will have invalid id possibly
        return Coalition([self, other])

    def get_intent(self):
        # Auro, this function --------
        # TODO: add a brain here. change later.
        # current suicide function
        return Intent(self, self, "battle")

    def __str__(self):
        return "Player %d: Attack: %d, Gold: %d, Status: %s" % (self.id, self.attack. self.gold, self.status)


# class Coalition(Player):
#     def __init__(self, players):
#         super().__init__()
#         self.players = players
#
#     def __getattribute__(self, item):
#         aggregates = ['attack']
#         if item in aggregates:
#             attrs = self.aggregate_attr()
#             return attrs[item]
#         else:
#             return object.__getattribute__(self, item)
#
#     def aggregate_attr(self):
#         aggregates = ['attack']
#         attrs = {}
#         for i in aggregates:
#             attrs[i] = sum([x.__dict__[i] for x in self.players])
#         return attrs
#
#     def __str__(self):
#         return ";".join([i.__str__() for i in self.players])


class Intent(object):
    def __init__(self, player, target, type):
        self.player = player
        self.target = target
        self.type = type # Type is the type of move

    def __str__(self):
        return "Player %d targets %d with intent %s" % (self.player.id, self.target.id, self.type)


class Game(object):
    ATTACK_LOSS_FACTOR = 0.5
    GOLD_GAIN_FACTOR  = 0.5

    def __init__(self, players = 2):
        self.players = [Player(i+1, 5) for i in range(players)]
        self.coalitions = None

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
        self.check_state()

    def battle(self, intents)-> List[Player]:
        """
        Simulates a battle
        :return: list(Player) Losers
        """

        temp_players = copy.deepcopy(self.players)

        for intent in intents:
            if intent.type == "battle":
                if intent.player.attack > intent.target.attack:
                    intent.target.status = "dead"
                    intent.player.attack -= intent.target.attack*self.ATTACK_LOSS_FACTOR
                    intent.player.gold += intent.target.gold*self.GOLD_GAIN_FACTOR
                else:
                    intent.player.attack -= intent.target.attack*self.ATTACK_LOSS_FACTOR
                    intent.target.attack -= intent.player.attack*self.ATTACK_LOSS_FACTOR

    def form_coalitions(self, intents):
        """
        Simulates coalition forming of players. Updates self.players()
        :return:
        """
        pass

    def check_state(self):
        pass


def visualize(game):
    pass


if __name__ == '__main__':
    game = Game(3)
    #while True:
    for i in range(5):
        state = game.step()
        visualize(game)
        if state == "win":
            break
