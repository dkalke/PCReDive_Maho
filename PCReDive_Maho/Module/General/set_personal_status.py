import datetime

import Module.Kernel.DB_control
import Module.Kernel.week_stage
import Module.Kernel.info_update
import Module.Kernel.get_closest_end_time
import Module.Kernel.check_add_or_del_role


async def set_personal_status(send_obj, server_id, sign_channel_id, member_id, normal, reversed):
  connection = await Module.Kernel.DB_control.OpenConnection(send_obj)
  if connection:
    cursor = connection.cursor(prepared=True)
    sql = "SELECT now_week, now_week_1, now_week_2, now_week_3, now_week_4, now_week_5, week_offset, group_serial, fighting_role_id FROM princess_connect.group WHERE server_id = ? and sign_channel_id = ? order by group_serial limit 0, 1"
    data = (server_id, sign_channel_id)
    cursor.execute(sql, data) # 認證身分
    row = cursor.fetchone()
    if row:
      group_serial = row[7]
      fighting_role_id = row[8]
      # 取得正在使用的帳號
      sql = "SELECT serial_number FROM princess_connect.members WHERE now_using = '1' and server_id = ? and group_serial = ? and member_id = ? LIMIT 0, 1"
      data = (server_id, group_serial, member_id)
      cursor.execute(sql, data)
      row = cursor.fetchone()
      if row:
        base_date = Module.Kernel.get_closest_end_time.get_closest_end_time(datetime.datetime.now()) - datetime.timedelta(days = 1)
        sql = "INSERT INTO princess_connect.knife_summary VALUES (?, ?, ?, ?) ON DUPLICATE KEY UPDATE normal = ?, reserved = ?"
        data = (row[0], base_date, normal, reversed, normal, reversed)
        cursor.execute(sql, data)
        connection.commit() # 資料庫存檔

        await Module.Kernel.check_add_or_del_role.check_add_or_del_role(send_obj, cursor, server_id, group_serial, member_id, base_date, fighting_role_id) # 設定身分組

        await send_obj.send('更新完成，正刀剩餘:{}，補償剩餘:{}!'.format(normal, reversed))
        await Module.Kernel.info_update.info_update(send_obj ,server_id, group_serial)
      else:
        await send_obj.send('找不到你的資料，請通知戰隊隊長協助加入戰隊名單!')
    else:
      await send_obj.send('這裡不是報刀頻道喔!')

    cursor.close
    await Module.Kernel.DB_control.CloseConnection(connection, send_obj)
