import copy
import random

import initials
from IPython import get_ipython
from tabulate import tabulate

ipython = get_ipython()
ipython.magic("%load_ext autoreload")
ipython.magic("%autoreload 2")

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

    def __add__(self, other: 'Player') -> 'Coalition':
        # FIXME: If player becomes part of coalition, and another player wants to target that player, will have invalid id possibly
        player_list = []
        if type(self) == Coalition:
            player_list += self.players
        else:
            player_list += [self]
        if type(other) == Coalition:
            player_list += other.players
        else:
            player_list += [other]
        return Coalition(player_list)

    def get_intent(self, game):
        players = game.players
        # Auro, this function --------
        # TODO: add a brain here. change later.
        players = [i for i in players if i.status == "ALIVE"]
        self_copy = copy.copy(self)
        target = random.choice(list(filter(lambda x: x.status == "ALIVE", game.players)))
        return Intent(self_copy, target, "BATTLE", 0)

    def __repr__(self):
        return "Player %d" % (self.id)

    def __str__(self):
        return "Player %d: Attack: %d, Gold: %d, Status: %s \n In peace with: %s" % (
            self.id, self.attack, self.gold, self.status, str(self.peace_dict))

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

    def get_coal_intent(self, game):
        # random
        target = random.choice(list(filter(lambda x: x.status == "ALIVE", game.players)))
        return Intent(copy.copy(self), target, "COAL")


def deserialize_players(inp):
    return [Player(x['id'], attack=x['attack'], gold=x['gold']) for x in inp]


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
        if att == 0: att = 1
        for player in self.players:
            player.gold += gold * (player.attack / att)

    def suffer_loss(self, attack):
        att = self.attack
        if att == 0: att = 1
        loss_list = []
        for player in self.players:
            loss_list.append(attack * (player.attack / att))
        for i in range(len(self.players)):
            self.players[i].attack = max(0, self.players[i].attack - loss_list[i])


class Intent(object):
    def __init__(self, player, target, type, gold=0):
        self.player = player
        self.target = target
        self.type = type  # Type is the type of move
        self.gold = gold

    def __str__(self):
        return "Player %d targets %d with intent %s with tribute %d" % (
            self.player.id, self.target.id, self.type, self.gold)


class Game(object):
    ATTACK_LOSS_FACTOR = 0.4
    GOLD_GAIN_FACTOR = 0.6

    def __init__(self, players=initials.plain):
        self.players = players
        self.dead_players = []
        self.winner = None

    def get_player(self, id):
        for player in self.players:
            if player.id == id:
                return player

    def step(self):
        """
        One time step of the game
        :return:
        """
        self.form_coalitions()  # Sends request to player to accept or reject
        intents = []
        for x in self.players:
            if x.status == "ALIVE":
                intents += [x.get_intent(self)]

        """
        Add COAL intents here.
        Strategy 1: Random pairs
        """
        # @auro TODO: Aren't coal intents after battling?, not at the same time

        # coal_intents = [x.get_coal_intent(self) for x in filter(lambda x: x.status == "ALIVE", self.players)]

        # intents += coal_intents

        # self.form_coalitions(intents)  # Sends request to player to accept or reject
        self.battle(intents)
        # self.handle_peace(intents)
        self.end_of_turn_calcs()
        return self.check_state()

    def end_of_turn_calcs(self):
        def splitplayer(player):
            if type(player) == Player:
                return [player]
            else:
                list = []
                for x in player.players:
                    list.extend(splitplayer(x))
                return list

        #
        # for player in self.players:
        #     for i in player.peace_dict:
        #         player.peace_dict[i] -= 1
        #         if player.peace_dict[i] == 0:
        #             player.peace_dict.pop(i)
        for player in self.players:
            if player.id == -1:
                self.players.remove(player)
                self.players.extend(splitplayer(player))

        print(self.players)

    def battle(self, intents):
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
                    player.suffer_loss(intent.target.attack * self.ATTACK_LOSS_FACTOR)
                    player.gain_gold(intent.target.gold * self.GOLD_GAIN_FACTOR)
                else:
                    player.suffer_loss(intent.target.attack * self.ATTACK_LOSS_FACTOR)
                    target.suffer_loss(intent.player.attack * self.ATTACK_LOSS_FACTOR)

    def form_coal_intents(self):
        #     init_list = copy.deepcopy(self.players) #[1, 2, 3, 4, 5]
        #     init_list = random.shuffle(init_list)
        #     groups = []
        #     for i in range(int(len(init_list)/5)):
        #         acc = []
        #         for j in range(5):
        #             try:
        #                 acc.append(init_list[i+j])
        #             except:
        #                 break
        #         groups.append(acc)
        #
        #     self.players = [sum(x) for x in groups]
        #     final_list = init_list #[1, [2, 3], [4, 5]]
        #
        #     for coal in final_list:
        #         if len(coal) > 1:
        #             for i in range(0, len(coal)-1):
        #                 intents+=intent("COAL", i, coal[len(coal)]-1)
        pass

    # def form_coalitions(self, intents):
    def form_coalitions(self):
        """
        Simulates coalition forming of players. Updates self.players()
        :return:
        """
        if len(self.players) <= 10: return
        init_list = copy.deepcopy(self.players)
        random.shuffle(init_list)
        groups = []
        for i in range(int(len(init_list) / 5)):
            acc = []
            for j in range(5):
                try:
                    acc.append(init_list[i * 5 + j])
                except:
                    break
            groups.append(acc)
        self.players = [sum(x[1:], x[0]) if len(x) > 1 else x[0] for x in groups]

        # for intent in intents:
        #     player = self.players[self.players.index(intent.player)]
        #     target = self.players[self.players.index(intent.target)]
        #
        #     if intent.type == "COAL":
        #         if self.players.index(intent.player) == self.players.index(intent.target) or len(self.players) == 2:
        #             print("Can't coalesce into one")
        #             continue
        #         print(player, target, " wanna join")
        #         if target.request_coal(player) == True:
        #             self.players.remove(player)
        #             self.players.remove(target)
        #             self.players.append(player + target)
        #
        #         for player in self.players:
        #             print(player, " | ", end='')
        #         print(" is after the coalition")

    def check_state(self):
        num_alive = 0
        dead_players = list(filter(lambda x: x.status == "DEAD", self.players))
        alive_players = list(filter(lambda x: x.status == "ALIVE", self.players))
        self.winner = alive_players[0].id
        self.dead_players += dead_players
        self.players = alive_players
        if len(alive_players) <= 1:
            return "DONE"
        else:
            return "RUNNING"
        pass


def visualize(game):
    print(tabulate([vars(x) for x in game.players]))


if __name__ == '__main__':
    import argparse

    parser = argparse.ArgumentParser(description='Describe your game')
    parser.add_argument('playermodel', type=str,
                        help='Pick one of the predefined player models: ' + "\n".join(dir(initials)))
    parser.add_argument('strategymodel', type=str,
                        help='Pick one of the predefined strategy models')

    args = parser.parse_args()

    PLAYERS = deserialize_players(initials.__dict__[args.playermodel])

    game = Game(PLAYERS)

    print("Initial")
    visualize(game)
    for step in range(STEPS):
        state = game.step()
        print("Step " + str(step + 1))
        # visualize(game)
        if state == "DONE":
            if game.winner is None:
                print("All players died")
            else:
                print("The winner is: Player " + str(game.winner))
            break
