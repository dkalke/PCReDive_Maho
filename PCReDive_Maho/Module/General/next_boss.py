import datetime

import Module.Kernel.DB_control
import Module.Kernel.week_stage
import Module.Kernel.define_value
import Module.Kernel.show_knifes
import Module.Kernel.Offset_manager
import Module.Kernel.Update


#!取消保留刀 [第幾刀]
async def next_boss(send_obj, server_id, sign_channel_id, member_id, message_create_time, boss):
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
      if ( not now_week[boss-1] >= main_week + 2 ) and (Module.Kernel.week_stage.week_stage(now_week[boss-1]) == Module.Kernel.week_stage.week_stage(main_week)):
        if message_create_time + datetime.timedelta(hours = 8) >= boss_change[boss-1] + datetime.timedelta(seconds = Module.Kernel.define_value.CD_TIME): 
          # 更新該王週目
          now_week[boss-1] = now_week[boss-1]+1
          cursor = connection.cursor(prepared=True)
          sql = ""
          if boss==1:
            sql = "UPDATE princess_connect.group SET now_week_1=?, boss_change_1=? WHERE server_id = ? and sign_channel_id = ?"
          elif boss==2:
            sql = "UPDATE princess_connect.group SET now_week_2=?, boss_change_2=? WHERE server_id = ? and sign_channel_id = ?"
          elif boss==3:
            sql = "UPDATE princess_connect.group SET now_week_3=?, boss_change_3=? WHERE server_id = ? and sign_channel_id = ?"
          elif boss==4:
            sql = "UPDATE princess_connect.group SET now_week_4=?, boss_change_4=? WHERE server_id = ? and sign_channel_id = ?"
          elif boss==5:
            sql = "UPDATE princess_connect.group SET now_week_5=?, boss_change_5=? WHERE server_id = ? and sign_channel_id = ?"
          data = (now_week[boss-1], (message_create_time + datetime.timedelta(hours = 8)).strftime("%Y-%m-%d %H:%M:%S"), server_id, sign_channel_id)
          cursor.execute(sql, data)
          cursor.close
          connection.commit()

          msg = ["","","","",""]
          # 檢查main week是否需要更動
          new_main_week = min(now_week)
          if new_main_week > main_week:
            knifes = await Module.Kernel.show_knifes.show_knifes(connection, server_id, group_serial, now_week[boss-1] ,boss)
            
            if knifes == '':
              msg[boss-1] = '目前' + str(now_week[boss-1]) + '週' + str(boss) + '王沒人報刀喔，看在真步的面子上，快來報刀!\n'
            else:
              msg[boss-1] = knifes + str(now_week[boss-1]) + '週' + str(boss) + '王到囉!\n'

            # 去除當前的boss
            boss_index=list(range(1,6))
            boss_index.remove(boss)


            #如果其他王week位處main_week+2，一併tag上來
            for index in boss_index:
              if new_main_week == Module.Kernel.define_value.Stage.one.value or \
                new_main_week == Module.Kernel.define_value.Stage.two.value or \
                new_main_week == Module.Kernel.define_value.Stage.three.value or \
                new_main_week == Module.Kernel.define_value.Stage.four.value or \
                new_main_week == Module.Kernel.define_value.Stage.five.value or \
                (now_week[index-1] == main_week+2 and Module.Kernel.week_stage.week_stage(now_week[index-1])== Module.Kernel.week_stage.week_stage(new_main_week)): 
                knifes = await Module.Kernel.show_knifes.show_knifes(connection, server_id, group_serial, now_week[index-1] ,index)

                if knifes == '':
                  msg[index-1] = '目前' + str(now_week[index-1]) + '週' + str(index) + '王沒人報刀喔，看在真步的面子上，快來報刀!\n'
                else:
                  msg[index-1] = knifes + str(now_week[index-1]) + '週' + str(index) + '王到囉!\n'
              else:
                pass

            #更新主週目
            cursor = connection.cursor(prepared=True)
            sql = "UPDATE princess_connect.group SET now_week=? WHERE server_id = ? and sign_channel_id = ?"
            data = (new_main_week, server_id, sign_channel_id)
            cursor.execute(sql, data)
            cursor.close
            connection.commit()

            # 自動周目控制
            Module.Kernel.Offset_manager.AutoOffset(connection, server_id, group_serial) 
          else:
            if (now_week[boss-1] < main_week+2) and (Module.Kernel.week_stage.week_stage(now_week[boss-1]) == Module.Kernel.week_stage.week_stage(main_week)): # 檢查週目是否超出可出刀週目
              knifes = await Module.Kernel.show_knifes.show_knifes(connection, server_id, group_serial, now_week[boss-1] ,boss)

              if knifes == '':
                msg[boss-1] = '目前' + str(now_week[boss-1]) + '週' + str(boss) + '王沒人報刀喔，看在真步的面子上，快來報刀!'
              else:
                msg[boss-1] = knifes + str(now_week[boss-1]) + '週' + str(boss) + '王到囉!'

            else:
              msg[boss-1] = str(now_week[boss-1] - 1) +'週' + str(boss) + '王已討伐，等待其他boss中。'

          await send_obj.send(msg[0]+msg[1]+msg[2]+msg[3]+msg[4])

          await Module.Kernel.Update.Update(send_obj, server_id, group_serial) # 更新刀表
        else:
          await send_obj.send(str(boss) + '王目前CD中，上次使用時間:' + str(boss_change[boss-1]) + '。' )
      else:
        await send_obj.send('當前主週目為' + str(main_week) + '，還打不到' + str(now_week[boss-1]) + '週' + str(boss) + '王喔!')
    else:
      await send_obj.send('這裡不是報刀頻道喔!')

    await Module.Kernel.DB_control.CloseConnection(connection, send_obj)