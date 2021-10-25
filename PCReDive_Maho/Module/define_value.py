from enum import Enum

MAX_DAMAGE = 1000000000

class Period(Enum):
  UNKNOW = 0 # 未定
  DAY = 1 # 08-16
  NIGHT = 2 # 16-24
  GRAVEYARD = 3 # 00-08
  ALL = 4 # 00-24


class Policy(Enum):
  NO = 0 # 不回報傷害 
  YES = 1 # 須回報傷害


class Stage(Enum):
  one = 1
  two = 4
  three = 11
  four = 31
  five = 41

