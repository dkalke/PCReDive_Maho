import datetime

from discord import Embed
import Module.Kernel.Discord_client
import Module.Kernel.Name_manager
import Module.Kernel.DB_control
import Module.Kernel.define_value
import Module.Kernel.get_closest_end_time
import Module.Kernel.half_string_to_full

async def info_update(send_obj ,server_id, group_serial):
  # 取得資訊訊息物件
  connection2 = await Module.Kernel.DB_control.OpenConnection(send_obj)
  if connection2.is_connected():
    connection = await Module.Kernel.DB_control.OpenConnection(send_obj)
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
          # 取得戰隊戰日期
          date_now = datetime.datetime.now()
          end_time = Module.Kernel.get_closest_end_time.get_closest_end_time(date_now) # 取得當日結束時間 29點00分
          start_time = end_time - datetime.timedelta(days=1)

          day_name = ''
          if start_time < Module.Kernel.define_value.BATTLE_DAY[0]:
            day_name = '(戰間期) - 系統時程\n刀表清除:\n{}\n戰隊戰開始:\n{}\n'.format(str(Module.Kernel.define_value.BATTLE_DAY[0] -  datetime.timedelta(days = 2) - datetime.timedelta(hours = 5)), str(Module.Kernel.define_value.BATTLE_DAY[0]))
          elif start_time == Module.Kernel.define_value.BATTLE_DAY[0]:
            day_name = '戰隊戰第1天'
          elif start_time == Module.Kernel.define_value.BATTLE_DAY[1]:
            day_name = '戰隊戰第2天'
          elif start_time == Module.Kernel.define_value.BATTLE_DAY[2]:
            day_name = '戰隊戰第3天'
          elif start_time == Module.Kernel.define_value.BATTLE_DAY[3]:
            day_name = '戰隊戰第4天'
          elif start_time == Module.Kernel.define_value.BATTLE_DAY[4]:
            day_name = '戰隊戰第5天'
          else:
            day_name = '(等待下月戰隊戰日期公佈中)'
          embed_msg = Embed(title='第' + str(group_serial) + '戰隊資訊', description=day_name ,color=0xD98B99)

          # 列出序號、成員名稱、剩餘刀數、出刀偏好
          cursor = connection.cursor(prepared=True)
          sql = "SELECT a.serial_number, a.member_id, a.period, a.sockpuppet, a.last_sl_time, b.normal, b.reserved\
                  FROM princess_connect.members a\
                  LEFT JOIN princess_connect.knife_summary b ON a.serial_number = b.serial_number and day = ?\
                  WHERE server_id = ?  and group_serial = ?\
                  ORDER BY a.serial_number, a.sockpuppet"
          data = (start_time, server_id, group_serial)
          cursor.execute(sql, data)
          row = cursor.fetchone()
          fighting_member_msg = ''
          competed_member_msg = ''
          member_index = 1
          competed_member_count = 0
          normal_total = 0 # 已出正刀數量合計
          reversed_total = 0 # 已出補償刀數量合計
          while row:
            serial_number = row[0]
            member_id = row[1]
            member_name = await Module.Kernel.Name_manager.get_nick_name(server_id, member_id)

            period = row[2]
            sockpuppet = row[3]
            # 是否有SL?
            have_sl = 'Y'
            if row[4] >= end_time:
              have_sl = 'N'

            normal = 3
            if row[5] != None:
              normal = row[5]
            reserved = 0
            if row[6] != None:
              reserved = row[6]
            if period == Module.Kernel.define_value.Period.UNKNOW.value:
              period = '不定'
            elif period == Module.Kernel.define_value.Period.EARLY_MORNING.value:
              period = '清晨'
            elif period == Module.Kernel.define_value.Period.DAY.value:
              period = '早班'
            elif period == Module.Kernel.define_value.Period.NIGHT.value:
              period = '晚班'
            elif period == Module.Kernel.define_value.Period.LAST_NIGHT.value:
              period = '深夜'
            elif period == Module.Kernel.define_value.Period.ALL.value:
              period = '全日'
            else:
              period = '錯誤'


            if normal == 0 and reserved == 0:
              competed_member_count += 1
              competed_member_msg = competed_member_msg + '（{}）　{}-{}\n'.format(Module.Kernel.half_string_to_full.half_string_to_full('{:>02d}'.format(member_index)), Module.Kernel.half_string_to_full.half_string_to_full(str(sockpuppet)), member_name) 
            else:
              normal_total += normal
              reversed_total += reserved
              fighting_member_msg = fighting_member_msg + '（{}）　{}　{}正{}補　{}　{}-{}\n'.format(Module.Kernel.half_string_to_full.half_string_to_full('{:>02d}'.format(member_index)), period, Module.Kernel.half_string_to_full.half_string_to_full(str(normal)), Module.Kernel.half_string_to_full.half_string_to_full(str(reserved)),Module.Kernel.half_string_to_full.half_string_to_full(have_sl), Module.Kernel.half_string_to_full.half_string_to_full(str(sockpuppet)), member_name) 

            member_index = member_index + 1
            row = cursor.fetchone()

          cursor.close

          if competed_member_msg == '':
            if member_index - 1 == 0:
              competed_member_msg += '尚無成員資訊!\n'
            else:
              competed_member_msg += '尚無出刀完成成員!\n'
          competed_member_msg = '（序號）　名稱\n-------------------------------------------\n' + competed_member_msg + '-------------------------------------------\n'
          competed_member_msg += '（總計）　{}人完刀{}人出刀中\n\n'.format(Module.Kernel.half_string_to_full.half_string_to_full(str(competed_member_count)), Module.Kernel.half_string_to_full.half_string_to_full(str(member_index -1 - competed_member_count)))

          if fighting_member_msg == '':
            if member_index - 1 == 0:
              fighting_member_msg += '尚無成員資訊!\n'
            else:
              fighting_member_msg += '本日成員全數出刀完成!\n'
          fighting_member_msg = '（序號）　偏好　剩餘刀數　Ｒ　名稱\n-------------------------------------------\n' + fighting_member_msg + '-------------------------------------------\n'
          fighting_member_msg = fighting_member_msg + '（總計）　　　　{}正{}補'.format(Module.Kernel.half_string_to_full.half_string_to_full(str(normal_total)), Module.Kernel.half_string_to_full.half_string_to_full(str(reversed_total)))

          embed_msg.add_field(name='成功人士', value=competed_member_msg , inline=False)
          embed_msg.add_field(name='\u200b', value='\u200b' , inline=False)
          embed_msg.add_field(name='出刀進行中', value=fighting_member_msg , inline=False)

          # 取得訊息物件
          try:
            guild = Module.Kernel.Discord_client.bot.get_guild(server_id)
            channel = guild.get_channel(info_channel_id)
            message_obj = await channel.fetch_message(info_message_id)
            await message_obj.edit(embed=embed_msg)
          except:
            await send_obj.send(content='資訊訊息已被移除，請重新設定資訊頻道!')
        else:
          await send_obj.send(content='請戰隊隊長設定資訊頻道!')

      else:
        await send_obj.send(content='查無戰隊資料!')

      await Module.Kernel.DB_control.CloseConnection(connection, send_obj)

    await Module.Kernel.DB_control.CloseConnection(connection2, send_obj)
