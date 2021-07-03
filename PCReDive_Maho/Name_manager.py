"""
每6小時清空暫存的DC暱稱資料
"""

import gc
from discord.ext import tasks
from Discord_client import client



@tasks.loop(seconds=10)
async def clear_list():
  global people_list
  # 重設雜湊表
  people_list = dict()
  gc.collect()
  print('已重置雜湊表')

def init():
  clear_list.start()

people_list = dict() # 放nickname