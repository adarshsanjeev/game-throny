import random

import strategies


def addHuman(obj):
    return obj + [
        {
            'id': obj[-1].id + 1,
            'attack': 10,
            'gold': 10,
            'strategy': 'human'
        }
    ]

plain = [
    {
        'id': x,
        'attack': 10,
        'gold': 10,
        'strategy': strategies.aggressive
    } for x in range(30)
]

randomattuniform = [
    {
        'id': x,
        'attack': random.randint(0, 30),
        'gold': 10,
        'strategy': random.choice((strategies.aggressive, strategies.defensive))
    } for x in range(4)
]

randomattbellcurve = [
    {
        'id': x,
        'attack': random.normalvariate(100, 15),
        'gold': 10,
        'strategy': random.choice((strategies.aggressive, strategies.defensive))
    } for x in range(1000)
]
