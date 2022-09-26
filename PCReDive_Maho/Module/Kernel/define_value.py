import datetime
from enum import Enum

MAX_DAMAGE = 1000000000

class Period(Enum):
  UNKNOW = 0 # 未定
  EARLY_MORNING = 1 # 05-08
  DAY = 2 # 08-16
  NIGHT = 3 # 16-24
  LAST_NIGHT = 4 # 00-05
  ALL = 5 # 00-24


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
  [2200,2300,2700,2900,3100],\
  [9500,10000,11000,12000,13000]]

# 戰隊戰日期
this_year = None
this_month = None
this_day = None
BATTLE_DAY= None

CD_TIME = 10 # !n 的冷卻時間
NCD_TIME = 60 # !cn 的冷卻時間