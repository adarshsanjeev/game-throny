from typing import List, Tuple

class Player(object):
    def __init__(self, attack=0):
        self.attack = attack

    def __add__(self, other: 'Player') -> 'Coalition':
        return Coalition([self, other])

class Coalition(Player):
    def __init__(self, players):
        super().__init__()
        self.players = players

    def __getattribute__(self, item):
        aggregates = ['attack']
        if item in aggregates:
            attrs = self.aggregate_attr()
            return attrs[item]
        else:
            return object.__getattribute__(self, item)

    def aggregate_attr(self):
        aggregates = ['attack']
        attrs = {}
        for i in aggregates:
            attrs[i] = sum([x.__dict__[i] for x in self.players])
        return attrs

class Game(object):
    def __init__(self, players = 2):
        self.players = [Player() for i in range(players)]
        self.coalitions = None

    def step(self):
        """
        One time step of the game
        :return:
        """
        self.form_coalitions()
        self.battle()
        self.check_state()

    def battle(self)-> List(Player):
        """
        Simulates a battle
        :return: list(Player) Losers
        """
        pass

    def form_coalitions(self):
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
    game = Game(2)
    while True:
        state = game.step()
        visualize(game)
        if state == "win":
            break