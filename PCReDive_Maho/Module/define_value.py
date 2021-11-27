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

# BOSS[week][boss] 血量  
BOSS_HP=[\
  [600,800,1000,1200,1500],\
  [600,800,1000,1200,1500],\
  [1200,1400,1700,1900,2200],\
  [1900,2000,2300,2500,2700],\
  [8500,9000,9500,10000,11000]]

CD_TIME = 10 # !n 的冷卻時間
NCD_TIME = 60 # !cn 的冷卻時間