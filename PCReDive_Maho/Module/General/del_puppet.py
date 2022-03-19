import datetime

import Module.Kernel.DB_control
import Module.Kernel.info_update
import Module.Kernel.get_closest_end_time


async def del_puppet(send_obj, server_id, sign_channel_id, member_id, index):
  # 序號不可小於0
  if index > 0:
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
        # 檢查成員是否存在
        sql = "SELECT 1 FROM princess_connect.members WHERE server_id = ? and group_serial = ? and member_id = ? limit 0, 1"
        data = (server_id, group_serial, member_id)
        cursor.execute(sql, data)
        row = cursor.fetchone()
        if row:
          # 檢查成員是否存在
          sql = "SELECT 1 FROM princess_connect.members WHERE server_id = ? and group_serial = ? and member_id = ? and sockpuppet = ? limit 0, 1"
          data = (server_id, group_serial, member_id, index)
          cursor.execute(sql, data)
          row = cursor.fetchone()
          if row:
            # 刪除帳務資訊
            sql = "Delete FROM princess_connect.members WHERE server_id = ? and group_serial = ? AND member_id = ? AND sockpuppet = ?"
            data = (server_id, group_serial, member_id, index)
            cursor.execute(sql, data)

            # 切換帳號
            # 先關閉持有的所有帳號，再開啟要使用的帳號
            # 關閉
            sql = "UPDATE princess_connect.members SET now_using = '0' WHERE server_id = ? and group_serial = ? AND member_id = ?"
            data = (server_id, group_serial, member_id)
            cursor.execute(sql, data)

            # 開啟本尊
            sql = "UPDATE princess_connect.members SET now_using = '1' WHERE server_id = ? and group_serial = ? AND member_id = ? AND sockpuppet = '0' "
            data = (server_id, group_serial, member_id)
            cursor.execute(sql, data)

            connection.commit() # 資料庫存檔

            # 設定身分組
            base_date = Module.Kernel.get_closest_end_time.get_closest_end_time(datetime.datetime.now()) - datetime.timedelta(days = 1)
            await Module.Kernel.check_add_or_del_role.check_add_or_del_role(send_obj, cursor, server_id, group_serial, member_id, base_date, fighting_role_id)
              
            await send_obj.send('您已刪除分身{}，為您切換至本尊'.format(index))
            await Module.Kernel.info_update.info_update(send_obj ,server_id, group_serial)
          else:
            await send_obj.send('發生錯誤，你沒有該編號的分身，請查看剩餘刀數表。')
        else:
          await send_obj.send('該成員不在此戰隊中')
      else:
        await send_obj.send('這裡不是報刀頻道喔，請在所屬戰隊報刀頻道使用!')
      cursor.close
      await Module.Kernel.DB_control.CloseConnection(connection, send_obj)
  else:
    if index == 0:
      await send_obj.send('錯誤，[分身序號]不可為0，0代表本尊!')
    else:
      await send_obj.send('錯誤，[分身序號]只能是正整數!')
  