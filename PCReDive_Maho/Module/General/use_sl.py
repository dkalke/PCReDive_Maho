import datetime

import Module.Kernel.DB_control
import Module.Kernel.get_closest_end_time
import Module.Kernel.info_update


async def use_sl(send_obj, server_id, sign_channel_id, member_id):
  connection = await Module.Kernel.DB_control.OpenConnection(send_obj)
  if connection:
    cursor = connection.cursor(prepared=True)
    sql = "SELECT group_serial FROM princess_connect.group WHERE server_id = ? and sign_channel_id = ? order by group_serial limit 0, 1"
    data = (server_id, sign_channel_id)
    cursor.execute(sql, data) # 認證身分
    row = cursor.fetchone()
    if row:
      group_serial = row[0]

      # 檢查使否屬於該戰隊
      sql = "select last_sl_time from princess_connect.members WHERE server_id = ? and group_serial = ? and member_id = ? and now_using = '1' limit 0,1"
      data = (server_id, group_serial, member_id)
      cursor.execute(sql, data)
      row = cursor.fetchone()
      if row:
        # 修改SL時間
        closest_end_time = Module.Kernel.get_closest_end_time.get_closest_end_time(datetime.datetime.now())
        if row[0] < closest_end_time:
          sql = "update princess_connect.members SET last_sl_time=? WHERE server_id = ? and group_serial = ? and member_id = ? and now_using = '1'"
          data = (closest_end_time, server_id, group_serial, member_id)
          cursor.execute(sql, data)
          connection.commit()
          await send_obj.send('紀錄完成!')
          await Module.Kernel.info_update.info_update(send_obj ,server_id, group_serial)
        else:
          await send_obj.send('注意，今日已使用過SL，請勿退出遊戲!')
      else:
        await send_obj.send('您不屬於第' + str(group_serial) + '戰隊喔!')
    else:
      await send_obj.send('這裡不是報刀頻道喔，請在所屬戰隊報刀頻道使用!')
    cursor.close
    await Module.Kernel.DB_control.CloseConnection(connection, send_obj)
  