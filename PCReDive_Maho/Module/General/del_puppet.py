import Module.Kernel.DB_control
import Module.Kernel.info_update


async def del_puppet(send_obj, server_id, sign_channel_id, member_id):
  connection = await Module.Kernel.DB_control.OpenConnection(send_obj)
  if connection:
    cursor = connection.cursor(prepared=True)
    sql = "SELECT now_week, now_week_1, now_week_2, now_week_3, now_week_4, now_week_5, week_offset, group_serial FROM princess_connect.group WHERE server_id = ? and sign_channel_id = ? order by group_serial limit 0, 1"
    data = (server_id, sign_channel_id)
    cursor.execute(sql, data) # 認證身分
    row = cursor.fetchone()
    cursor.close
    if row:
      group_serial = row[7]
      # 檢查成員是否存, 並找出最大的puppet number
      sql = "SELECT MAX(sockpuppet) FROM princess_connect.members WHERE server_id=? and group_serial = ? and member_id=?"
      data = (server_id, group_serial, member_id)
      cursor.execute(sql, data)
      row = cursor.fetchone()
      cursor.close
      if not row[0] == None:
        sockpuppet = int(row[0])
        if sockpuppet != 0:
          # Delect 最大隻的 puppet
          # 刪除帳務資訊
          sockpuppet = int(row[0])
          cursor = connection.cursor(prepared=True)
          sql = "Delete FROM princess_connect.members WHERE server_id = ? and group_serial = ? AND member_id = ? AND sockpuppet = ?"
          data = (server_id, group_serial, member_id, sockpuppet)
          cursor.execute(sql, data)
          cursor.close

          # 切換帳號
          # 先關閉持有的所有帳號，再開啟要使用的帳號
          # 關閉
          cursor = connection.cursor(prepared=True)
          sql = "UPDATE princess_connect.members SET now_using = '0' WHERE server_id = ? and group_serial = ? AND member_id = ?"
          data = (server_id, group_serial, member_id)
          cursor.execute(sql, data)
          cursor.close

          # 開啟本尊
          cursor = connection.cursor(prepared=True)
          sql = "UPDATE princess_connect.members SET now_using = '1' WHERE server_id = ? and group_serial = ? AND member_id = ? AND sockpuppet = '0' "
          data = (server_id, group_serial, member_id)
          cursor.execute(sql, data)
          cursor.close

          connection.commit() # 資料庫存檔
              
          await send_obj.send('您已刪除分身{}，為您切換至本尊'.format(sockpuppet))
          await Module.Kernel.info_update.info_update(send_obj ,server_id, group_serial)
        else:
          await send_obj.send('您已無分身')
      else:
        await send_obj.send('該成員不在此戰隊中')
    else:
      await send_obj.send('這裡不是報刀頻道喔，請在所屬戰隊報刀頻道使用!')
    await Module.Kernel.DB_control.CloseConnection(connection, send_obj)
  