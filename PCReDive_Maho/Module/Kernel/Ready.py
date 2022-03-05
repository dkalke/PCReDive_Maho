import dotenv
import discord
from apscheduler.schedulers.asyncio import AsyncIOScheduler

import Module.Kernel.Discord_client
import Module.Kernel.auto_clear

dotenv.load_dotenv()

# 機器人上線事件
@Module.Kernel.Discord_client.client.event
async def on_ready():
  await Module.Kernel.Discord_client.client.change_presence(activity=discord.Activity(type=discord.ActivityType.watching, name="!h 查看更多資訊!"))
  print('We have logged in as {0.user}'.format(Module.Kernel.Discord_client.client))

  # 每月15號自動清理刀表，移除無用資訊(無法存取的伺服器)
  sched = AsyncIOScheduler()
  sched.add_job(Module.Kernel.auto_clear.auto_clear, 'cron', year='*', month='*', day=21, hour=23, minute=59, second=59, args=[])
  sched.start()