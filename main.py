import copy
from typing import List, Tuple
import random

MAX_PEACE_PERIOD = 3
PLAYERS = 3
STEPS = 10

class Player(object):
    def __init__(self, id, attack=0, gold=50):
        self.id = id
        self.attack = attack
        self.gold = gold
        self.status = "ALIVE"
        self.peace_dict = {}

    def __add__(self, other: 'Player') -> 'Coalition':
        # FIXME: If player becomes part of coalition, and another player wants to target that player, will have invalid id possibly
        return Coalition([self, other])

    def get_intent(self, players, coalitions):
        # Auro, this function --------
        # TODO: add a brain here. change later.
        # current suicide function
        self_copy = copy.copy(self)
        if self.id == 1:
            return [Intent(self_copy, Player(2), "COAL")]
        return [Intent(self_copy, self_copy, "PEACE", 10)]

    def __repr__(self):
        return "Player %d" % (self.id)

    def __str__(self):
        return "Player %d: Attack: %d, Gold: %d, Status: %s \n In peace with: %s" % (self.id, self.attack. self.gold, self.status, str(self.peace_dict))

    def request_peace(self, player):
        return True

    def request_coal(self, player):
        return True

    def __eq__(self, other):
        return self.id == other.id

    def set_peace(self, target, period=MAX_PEACE_PERIOD):
        self.peace_dict[target.id] = period

    def gain_gold(self, gold):
        self.gold += gold

    def suffer_loss(self, attack):
        self.attack -= attack

class Coalition(Player):
    def __init__(self, players):
        super().__init__(-1)
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

    def __eq__(self, other):
        for p in self.players:
            if other == p:
                return True
        return False

    def set_peace(self, target, period=MAX_PEACE_PERIOD):
        if target.id == -1:
            for t in target.players:
                for player in self.players:
                    player.peace_dict[t.id] = period
        else:
            for player in self.players:
                player.peace_dict[target.id] = period

    def gain_gold(self, gold):
        att = self.attack
        for player in self.players:
            player.gold += gold*(player.attack/att)

    def suffer_loss(self, attack):
        att = self.attack
        loss_list = []
        for player in self.players:
            loss_list.append(attack * (player.attack/att))
        for i in range(len(self.players)):
            self.players[i].attack = max(0, self.players[i].attack-loss_list[i])


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
        intents = []
        for x in self.players:
            intents += x.get_intent(self.players, self.coalitions)
        for intent in intents:
            print(intent)

        self.form_coalitions(intents) # Sends request to player to accept or reject
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
        for player in self.players:
            if player.id == -1:
                self.players.remove(player)
                self.players += player.players

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

    def form_coalitions(self, intents):
        """
        Simulates coalition forming of players. Updates self.players()
        :return:
        """

        for intent in intents:
            player = self.players[self.players.index(intent.player)]
            target = self.players[self.players.index(intent.target)]

            if intent.type == "COAL":
                if target.request_coal(player) == True:
                    self.players.remove(player)
                    self.players.remove(target)
                    self.players.append(player+target)


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


if __name__ == '__main__':
    game = Game(PLAYERS)

    print("Initial")
    visualize(game)
    for step in range(STEPS):
        state = game.step()
        print("Step "+str(step+1))
        # visualize(game)
        if state == "DONE":
            print("The winner is: Player "+str(game.winner))
            break
