import discord
from Discord_client import client



# 機器人上線事件
@client.event
async def on_ready():
  await client.change_presence(activity=discord.Activity(type=discord.ActivityType.watching, name="!h 查看更多資訊!"))
  print('We have logged in as {0.user}'.format(client))