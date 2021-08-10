import discord
from apscheduler.schedulers.asyncio import AsyncIOScheduler
import Discord_client
import Module.auto_clear


# 機器人上線事件
@Discord_client.client.event
async def on_ready():
  await Discord_client.client.change_presence(activity=discord.Activity(type=discord.ActivityType.watching, name="!h 查看更多資訊!"))
  print('We have logged in as {0.user}'.format(Discord_client.client))

  # 每月15號自動清理刀表，移除無用資訊(無法存取的伺服器)
  sched = AsyncIOScheduler()
  sched.add_job(Module.auto_clear.auto_clear, 'cron', year='*', month='*', day=15, hour=5, minute=0, second=0, args=[])
  sched.start()