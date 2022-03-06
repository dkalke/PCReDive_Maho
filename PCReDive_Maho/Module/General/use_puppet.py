import Module.Kernel.DB_control


#!取消保留刀 [第幾刀]
async def use_puppet(send_obj, server_id, sign_channel_id, member_id, index):
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
      # 檢查成員是否存在，並取得最大隻的分身編號
      cursor = connection.cursor(prepared=True)
      sql = "SELECT MAX(sockpuppet) FROM princess_connect.members WHERE server_id=? and group_serial = ? and member_id=?"
      data = (server_id, group_serial, member_id)
      cursor.execute(sql, data)
      row = cursor.fetchone()
      cursor.close
      if row[0] != None:
        max_sockpuppet = int(row[0])
        if 0 <= index and index <= max_sockpuppet:
          # 先關閉持有的所有帳號，再開啟要使用的帳號
          # 關閉
          cursor = connection.cursor(prepared=True)
          sql = "UPDATE princess_connect.members SET now_using = '0' WHERE server_id = ? and group_serial = ? AND member_id = ?"
          data = (server_id, group_serial, member_id)
          cursor.execute(sql, data)
          cursor.close

          # 開啟
          cursor = connection.cursor(prepared=True)
          sql = "UPDATE princess_connect.members SET now_using = '1' WHERE server_id = ? and group_serial = ? AND member_id = ? AND sockpuppet = ? "
          data = (server_id, group_serial, member_id, index)
          cursor.execute(sql, data)
          cursor.close

          connection.commit() # 資料庫存檔
              
          if index == 0:
            await send_obj.send('為您切換至本尊')
          else:
            await send_obj.send('為您切換至分身{}'.format(index))
        else:
          await send_obj.send('你沒有這隻分身喔')
      else:
        await send_obj.send('該成員不在此戰隊中')
    else:
      pass #非指定頻道 不反應
    await Module.Kernel.DB_control.CloseConnection(connection, send_obj)
