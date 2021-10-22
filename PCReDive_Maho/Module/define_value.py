from enum import Enum

MAX_DAMAGE = 1000000000

class Period(Enum):
  UNKNOW = 0
  DAY = 1
  NIGHT = 2
  GRAVEYARD = 3
  ALL = 4


class Policy(Enum):
  NO = 0 # 不回報傷害 
  YES = 1 # 須回報傷害

