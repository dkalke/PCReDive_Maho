import gc
from discord.ext import tasks
import Module.Kernel.Discord_client

# 每6小時清空暫存的DC暱稱資料
@tasks.loop(hours=6)
async def clear_list():
  global people_list
  # 重設雜湊表
  people_list = dict()
  gc.collect()
  print('已重置雜湊表')

# 獲取使用者nick(若無則為本名)
async def get_nick_name(server_id, member_id):
  # 新增一個映射表來加速 str(server_id)+str(member_id)
  key = str(server_id) + str(member_id)

  if key in people_list:
    return people_list[key]
  else:
    try:
      user = await Module.Kernel.Discord_client.bot.get_guild(server_id).fetch_member(member_id)
      if user.nick == None:
        people_list[key] = str(user.name)
        return user.name
      else:
        people_list[key] = str(user.nick)
        return user.nick
    except:
      print("get_nick_name查無此人!")
      return "[N/A]"
        

async def get_mention(server_id, member_id):
  try:
    user = await Module.Kernel.Discord_client.bot.get_guild(server_id).fetch_member(member_id)
    return user.mention
  except:
        print("get_mention查無此人!")
        return "[N/A]"

people_list = dict() # 放nickname