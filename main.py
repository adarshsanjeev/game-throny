from typing import List, Tuple
STEPS = 10

class Player(object):
    def __init__(self, id, attack=0):
        self.id = id
        self.attack = attack
        self.status = "ALIVE"

    def __add__(self, other: 'Player') -> 'Coalition':
        # FIXME: If player becomes part of coalition, and another player wants to target that player, will have invalid id possibly
        return Coalition([self, other])

    def get_intent(self):
        # Auro, this function --------
        # TODO: add a brain here. change later.
        return Intent(self.id, (self.id+1)%3+1, "battle")

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

class Intent(object):
    def __init__(self, player, target, type):
        self.player = player
        self.target = target
        self.type = type # Type is the type of move

class Game(object):
    LOSS_FACTOR = 0.5

    def __init__(self, players = 2):
        self.players = [Player(i+1, 5) for i in range(players)]
        self.coalitions = None

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

        self.form_coalitions(intents) # Sends request to player to accept or reject
        self.battle(intents)
        self.check_state()

    def battle(self, intents)-> List[Player]:
        """
        Simulates a battle
        :return: list(Player) Losers
        """

        losers = []
        for intent in intents:
            if intent.type == "battle":
                player = self.get_player(intent.player)
                target = self.get_player(intent.target)
                if player.attack > target.attack:
                    target.status = "DEAD"
                    player.attack -= target.attack*LOSS_FACTOR

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

    for step in range(STEPS):
        state = game.step()
        print("Step "+str(step))
        visualize(game)
        if state == "win":
            break
