"""
每30分鐘上傳伺服器使用人數至TopGG server
"""

import os
from discord.ext import tasks
import dbl
from Discord_client import client

@tasks.loop(minutes=30)
async def update_stats():
  try:
    await client.dblpy.post_guild_count()
    print('Posted server count=' + str(client.dblpy.guild_count()))
  except Exception as e:
    print('Failed to post server count\n{}: {}'.format(type(e).__name__, e))

def init():
  dbl_token = os.getenv('TOPGG_TOKEN')  # set this to your bot's top.gg token
  client.dblpy = dbl.DBLClient(client, dbl_token)
  update_stats.start()