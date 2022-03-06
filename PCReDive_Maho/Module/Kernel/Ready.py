import discord
import datetime
import calendar
import apscheduler.schedulers.asyncio 

import Module.Kernel.Discord_client
import Module.Kernel.auto_clear
import Module.Kernel.define_value
import Module.Kernel.TopGG
import Module.Kernel.Name_manager

# 機器人上線事件
@Module.Kernel.Discord_client.bot.event
async def on_ready():
  await Module.Kernel.Discord_client.bot.change_presence(activity=discord.Activity(type=discord.ActivityType.watching, name="輸入!h 查看更多資訊!"))
  print('We have logged in as {0.user}'.format(Module.Kernel.Discord_client.bot))

  Module.Kernel.TopGG.update_stats.start() # 定期執行TOPGG，回傳狀態(30分鐘)
  Module.Kernel.Name_manager.clear_list.start() # 定期重置成員暱稱雜湊表(6小時)
  sched = apscheduler.schedulers.asyncio.AsyncIOScheduler(timezone='Asia/Taipei')  
  task_manager(sched) # 初次啟動及每月月初執行，取得開戰日期(當月倒數第5日)、清除日期(當月倒數第7日)、下次執行時間(次月第1日)
  sched.start()
  
def task_manager(sched):
  # 當月開戰日期
  now_date = datetime.datetime.now()# 當前時間
  month_end_date = datetime.datetime(now_date.year, now_date.month, calendar.monthrange(now_date.year, now_date.month)[1])
  start_date = month_end_date - datetime.timedelta(days = 4)
  print('當月開戰時間為' + str(start_date))
  Module.Kernel.define_value.this_year = start_date.year
  Module.Kernel.define_value.this_month = start_date.month
  Module.Kernel.define_value.this_day = start_date.day
  Module.Kernel.define_value.BATTLE_DAY=[\
  datetime.datetime(year= Module.Kernel.define_value.this_year, month= Module.Kernel.define_value.this_month, day= Module.Kernel.define_value.this_day, hour=5, minute=0, second=0),\
  datetime.datetime(year= Module.Kernel.define_value.this_year, month= Module.Kernel.define_value.this_month, day= Module.Kernel.define_value.this_day, hour=5, minute=0, second=0) + datetime.timedelta(days=1),\
  datetime.datetime(year= Module.Kernel.define_value.this_year, month= Module.Kernel.define_value.this_month, day= Module.Kernel.define_value.this_day, hour=5, minute=0, second=0) + datetime.timedelta(days=2),\
  datetime.datetime(year= Module.Kernel.define_value.this_year, month= Module.Kernel.define_value.this_month, day= Module.Kernel.define_value.this_day, hour=5, minute=0, second=0) + datetime.timedelta(days=3),\
  datetime.datetime(year= Module.Kernel.define_value.this_year, month= Module.Kernel.define_value.this_month, day= Module.Kernel.define_value.this_day, hour=5, minute=0, second=0) + datetime.timedelta(days=4),\
  datetime.datetime(year= Module.Kernel.define_value.this_year, month= Module.Kernel.define_value.this_month, day= Module.Kernel.define_value.this_day, hour=0, minute=0, second=0) + datetime.timedelta(days=5)]

  # 取得當月清除日期，排定時間自動清理刀表以及移除無用資訊(無法存取的伺服器)
  clear_date = month_end_date - datetime.timedelta(days = 6) 
  if now_date < clear_date:
    sched.add_job(Module.Kernel.auto_clear.auto_clear, 'date', run_date = clear_date, args=[]) # 排定日期
    print('當月重製時間為' + str(clear_date))
  else:
    print('當月重製時間已過')

  # 自身下次執行日期
  next_date = month_end_date + datetime.timedelta(days = 1)
  sched.add_job(task_manager, 'date', run_date = next_date, args=[sched]) # 排定日期
  print('下次排程時間為' + str(next_date))