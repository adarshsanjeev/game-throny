# Game of Theories

## Implemented:
1. 3 players initialized with random attack, 50 gold each.
2. Each round, a player decides who to attack.
3. Source.attack > Target.attack:
  * Target dies
  * Source.attack -= Target.attack*LOSS_FACTOR
  * Source.gold += Target.gold*GOLD_FACTOR
4. Game ends when there's only one alive.

## TODO:
