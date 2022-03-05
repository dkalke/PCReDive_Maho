import os
from discord.ext import tasks
import topgg

import Module.Kernel.Discord_client

dbl_token = os.getenv('TOPGG_TOKEN')  # set this to your bot's top.gg token
Module.Kernel.Discord_client.client.topggpy = topgg.DBLClient(Module.Kernel.Discord_client.client, dbl_token)

# 每30分鐘上傳伺服器使用人數至TopGG server
@tasks.loop(minutes=30)
async def update_stats():
  try:
    await Module.Kernel.Discord_client.topggpy.post_guild_count()
    print(f"Posted server count ({Module.Kernel.Discord_client.topggpy.guild_count})")
  except Exception as e:
    print(f"Failed to post server count\n{e.__class__.__name__}: {e}")