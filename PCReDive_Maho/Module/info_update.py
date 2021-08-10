from enum import Enum
from discord import Embed
import Discord_client
import Name_manager
import Module.DB_control

class Period(Enum):
  UNKNOW = 0
  DAY = 1
  NIGHT = 2
  GRAVEYARD = 3
  ALL = 4

async def info_update(message ,server_id, group_serial):
  # 取得資訊訊息物件
  connection = await Module.DB_control.OpenConnection(message)
  if connection.is_connected():
    cursor = connection.cursor(prepared=True)
    sql = "SELECT info_channel_id, info_message_id FROM princess_connect.group WHERE server_id = ? and group_serial = ? LIMIT 0, 1"
    data = (server_id, group_serial)
    cursor.execute(sql, data)
    row = cursor.fetchone()
    cursor.close
    if row: # 戰隊存在
      info_channel_id = row[0]
      info_message_id = row[1]

      if info_message_id :

        embed_msg = Embed(title='第' + str(group_serial) + '戰隊資訊', color=0xD98B99)

        # 列出序號、成員名稱、剩餘刀數、出刀偏好
        cursor = connection.cursor(prepared=True)
        sql = "SELECT member_id, knifes, period FROM princess_connect.members WHERE server_id = ? and group_serial = ?"
        data = (server_id, group_serial)
        cursor.execute(sql, data)
        row = cursor.fetchone()
        msg = ''
        count = 1
        while row:
          member_id=row[0]
          knifes=row[1]
          period=row[2]

          if period == Period.UNKNOW.value:
            period = '不定'
          elif period == Period.DAY.value:
            period = '早班'
          elif period == Period.NIGHT.value:
            period = '晚班'
          elif period == Period.GRAVEYARD.value:
            period = '夜班'
          elif period == Period.ALL.value:
            period = '全日'
          else:
            period = '錯誤'

          member_name = await Name_manager.get_nick_name(message, member_id)
          msg = msg + '{' + str(count) + '} ' + member_name + '\n'
          msg = msg+ '　持有' + str(knifes) + '刀，剩餘' + str(knifes) + '刀，出刀偏好:' + period + '\n' # TODO 計算已出刀數
          count = count + 1
          row = cursor.fetchone()

        cursor.close

        if msg == '':
          msg = '尚無保留刀資訊!'
        else:
          pass
        embed_msg.add_field(name='\u200b', value=msg , inline=False)

        # 取得訊息物件
        try:
          guild = Discord_client.client.get_guild(server_id)
          channel = guild.get_channel(info_channel_id)
          message_obj = await channel.fetch_message(info_message_id)
          await message_obj.edit(embed=embed_msg)
        except:
          await message.channel.send(content='資訊訊息已被移除，請重新設定資訊頻道!')
      else:
        await message.channel.send(content='請戰隊隊長設定資訊頻道!')
    else:
      await message.channel.send(content='查無戰隊資料!')

    await Module.DB_control.CloseConnection(connection, message)
