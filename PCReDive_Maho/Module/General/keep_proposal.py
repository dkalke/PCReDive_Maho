import Module.Kernel.DB_control
import Module.Kernel.Update

#!報保留刀 [備註]
async def keep_proposal(send_obj, server_id, sign_channel_id, member_id, comment):
  connection = await Module.Kernel.DB_control.OpenConnection(send_obj)
  if connection:
    cursor = connection.cursor(prepared=True)
    sql = "SELECT group_serial FROM princess_connect.group WHERE server_id = ? and sign_channel_id = ? order by group_serial limit 0, 1"
    data = (server_id, sign_channel_id)
    cursor.execute(sql, data) # 認證身分
    row = cursor.fetchone()
    cursor.close
    if row:
      group_serial = row[0]
      # 寫入保留刀表
      cursor = connection.cursor(prepared=True)
      sql = "INSERT INTO princess_connect.keep_knifes (server_id, group_serial, member_id, comment) VALUES (?, ?, ?, ?)"
      data = (server_id, group_serial, member_id, comment)
      cursor.execute(sql, data)
      cursor.close()
      connection.commit()
      await send_obj.send('備註:' + comment + '，**保留刀**報刀成功!')
      await Module.Kernel.Update.Update(send_obj, server_id, group_serial) # 更新刀表
    else:
      await send_obj.send('這裡不是報刀頻道喔!')
    await Module.Kernel.DB_control.CloseConnection(connection, send_obj)