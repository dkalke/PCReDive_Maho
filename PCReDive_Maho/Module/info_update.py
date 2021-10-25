import datetime
from enum import Enum
from discord import Embed
import Discord_client
import Name_manager
import Module.DB_control
import Module.define_value

async def info_update(message ,server_id, group_serial):
  # 取得資訊訊息物件
  connection2 = await Module.DB_control.OpenConnection(message)
  if connection2.is_connected():
    connection = await Module.DB_control.OpenConnection(message)
    if connection.is_connected():
      cursor = connection.cursor(prepared=True)
      sql = "SELECT info_channel_id, info_message_id, policy FROM princess_connect.group WHERE server_id = ? and group_serial = ? LIMIT 0, 1"
      data = (server_id, group_serial)
      cursor.execute(sql, data)
      row = cursor.fetchone()
      cursor.close
      if row: # 戰隊存在
        info_channel_id = row[0]
        info_message_id = row[1]
        policy = row[2]

        if info_message_id :
          # 取得戰隊戰日期
          date_now = datetime.datetime.now()
          cursor = connection.cursor(prepared=True)
          sql = "SELECT day1, day2, day3, day4, day5, day6 FROM princess_connect.month LIMIT 0, 1"
          cursor.execute(sql)
          row = cursor.fetchone()
          day = [row[0], row[1], row[2], row[3], row[4], row[5]]
          day_name = ''
          cls_time_start = day[0]
          fetch_start = None
          fetch_end = None

          if date_now < day[0]:
            day_name = '(尚未開戰)'
          elif date_now < day[1]:
            day_name = '戰隊戰第1天'
            fetch_start = day[0]
            fetch_end = day[1]
          elif date_now < day[2]:
            day_name = '戰隊戰第2天'
            fetch_start = day[1]
            fetch_end = day[2]
          elif date_now < day[3]:
            day_name = '戰隊戰第3天'
            fetch_start = day[2]
            fetch_end = day[3]
          elif date_now < day[4]:
            day_name = '戰隊戰第4天'
            fetch_start = day[3]
            fetch_end = day[4]
          elif date_now < day[4]:
            day_name = '戰隊戰第5天'
            fetch_start = day[4]
            fetch_end = day[5]
          else:
            day_name = '(等待下月戰隊戰日期公佈中)'

          embed_msg = Embed(title='第' + str(group_serial) + '戰隊資訊', description=day_name ,color=0xD98B99)



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

            if period == Module.define_value.Period.UNKNOW.value:
              period = '不定'
            elif period == Module.define_value.Period.DAY.value:
              period = '早班'
            elif period == Module.define_value.Period.NIGHT.value:
              period = '晚班'
            elif period == Module.define_value.Period.GRAVEYARD.value:
              period = '夜班'
            elif period == Module.define_value.Period.ALL.value:
              period = '全日'
            else:
              period = '錯誤'

            knifes_msg = ''
            # 已出刀數計算，僅支援開啟回報傷害戰隊使用
            if policy == Module.define_value.Policy.YES.value and fetch_start and fetch_end :

              cursor2 = connection2.cursor(prepared=True)
              sql = "SELECT knife_type FROM princess_connect.knifes WHERE server_id = ? and group_serial = ? and member_id = ? and ? < done_time and done_time < ?"
              data = (server_id, group_serial, member_id, fetch_start, fetch_end)
              cursor2.execute(sql, data)
              in_row = cursor2.fetchone()
              done_knifes = 0
              while in_row:
                if in_row[0] == 1: # 正刀
                  done_knifes = done_knifes + 1 
                elif in_row[0] == 2: # 尾刀
                  done_knifes = done_knifes + 0.5
                elif in_row[0] == 3: # 補償刀
                  done_knifes = done_knifes + 0.5
                in_row = cursor2.fetchone()
              cursor2.close
              knifes_msg = '持有' + str(knifes) + '刀，剩餘' + '{:g}'.format(knifes - done_knifes) + '刀，'


            member_name = await Name_manager.get_nick_name(message, member_id)
            msg = msg + '{' + str(count) + '} ' + member_name + '\n'
            msg = msg+ '　' + knifes_msg + '出刀偏好:' + period + '\n'
            count = count + 1
            row = cursor.fetchone()

          cursor.close

          if msg == '':
            msg = '尚無成員資訊!'
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

    await Module.DB_control.CloseConnection(connection2, message)
