import datetime

import Module.Kernel.DB_control
import Module.Kernel.Update
import Module.Kernel.Offset_manager
import Module.Kernel.define_value


#!反悔 [boss]
async def previous_boss(send_obj, server_id, sign_channel_id, member_id, message_create_time, boss):
  # check頻道，並找出所屬組別
  connection = await Module.Kernel.DB_control.OpenConnection(send_obj)
  if connection:
    cursor = connection.cursor(prepared=True)
    sql = "SELECT now_week, now_week_1, now_week_2, now_week_3, now_week_4, now_week_5, boss_change_1, boss_change_2, boss_change_3, boss_change_4, boss_change_5, group_serial FROM princess_connect.group WHERE server_id = ? and sign_channel_id = ? order by group_serial limit 0, 1"
    data = (server_id, sign_channel_id)
    cursor.execute(sql, data) # 認證身分
    row = cursor.fetchone()
    cursor.close()
    if row:
      # CD檢查
      main_week = row[0]
      now_week=[row[1], row[2], row[3], row[4], row[5]]
      boss_change = [row[6], row[7], row[8], row[9], row[10]]
      group_serial = row[11]
      
      # UTC+0   UTC+8   =>   UTC+8      
      if boss_change[boss-1] <= message_create_time + datetime.timedelta(hours = 8):
        if message_create_time + datetime.timedelta(hours = 8) <= boss_change[boss-1] + datetime.timedelta(seconds = Module.Kernel.define_value.NCD_TIME): 
          # 更新該王週目與主週目
          # 注意，為避免濫用此功能，使用/cn後，會將/n的時間加上60秒，可達到以下效果
          # 1. 避免/n /cn 重複來回使用
          # 2. 避免60秒內 連續使用/cn
          # 3. 僅能使用/cn回退一個週目
          now_week[boss-1] = now_week[boss-1]-1
          new_main_week = min(now_week)
          cursor = connection.cursor(prepared=True)
          sql = ""
          if boss==1:
            sql = "UPDATE princess_connect.group SET now_week_1=?, now_week=?, boss_change_1=?  WHERE server_id = ? and sign_channel_id = ?"
          elif boss==2:
            sql = "UPDATE princess_connect.group SET now_week_2=?, now_week=?, boss_change_2=? WHERE server_id = ? and sign_channel_id = ?"
          elif boss==3:
            sql = "UPDATE princess_connect.group SET now_week_3=?, now_week=?, boss_change_3=? WHERE server_id = ? and sign_channel_id = ?"
          elif boss==4:
            sql = "UPDATE princess_connect.group SET now_week_4=?, now_week=?, boss_change_4=? WHERE server_id = ? and sign_channel_id = ?"
          elif boss==5:
            sql = "UPDATE princess_connect.group SET now_week_5=?, now_week=?, boss_change_5=? WHERE server_id = ? and sign_channel_id = ?"
          data = (now_week[boss-1], new_main_week, (boss_change[boss-1] + datetime.timedelta(seconds = Module.Kernel.define_value.NCD_TIME)).strftime("%Y-%m-%d %H:%M:%S"), server_id, sign_channel_id)
          cursor.execute(sql, data)
          cursor.close
          connection.commit()

          await send_obj.send(str(boss) + '王已退回' + str(now_week[boss-1]) + '週目，請務必提醒受影響成員，以免誤入錯誤週目!')
          Module.Kernel.Offset_manager.AutoOffset(connection, server_id, group_serial) # 自動周目控制
          await Module.Kernel.Update.Update(send_obj, server_id, group_serial) # 更新刀表
        else:
          await send_obj.send(str(boss) + '王已超過可反悔時間，請聯繫控刀手!\n下次可用時間:' + str(boss_change[boss-1] + datetime.timedelta(seconds = Module.Kernel.define_value.NCD_TIME + Module.Kernel.define_value.CD_TIME )) + '。' )
      else:
        await send_obj.send('只能反悔一週，如有需要請聯繫控刀手!')
    else:
      await send_obj.send('這裡不是報刀頻道喔!')

    await Module.Kernel.DB_control.CloseConnection(connection, send_obj)
