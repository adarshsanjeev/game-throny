import random

plain = [
    {
        'id': x,
        'attack': 10,
        'gold': 10
    } for x in range(4)
]

randomatt = [
    {
        'id': x,
        'attack': random.randint(0, 30),
        'gold': 10
    } for x in range(4)
]
