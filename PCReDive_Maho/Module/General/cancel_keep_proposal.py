import Module.Kernel.DB_control
import Module.Kernel.Update

async def cancel_keep_proposal(send_obj, server_id, sign_channel_id, member_id, index):
  if index > 0:
    connection = await Module.Kernel.DB_control.OpenConnection(send_obj)
    if connection:
      cursor = connection.cursor(prepared=True)
      sql = "SELECT  now_week, week_offset, group_serial FROM princess_connect.group WHERE server_id = ? and sign_channel_id = ? order by group_serial limit 0, 1"
      data = (server_id, sign_channel_id)
      cursor.execute(sql, data) # 認證身分
      row = cursor.fetchone()
      cursor.close
      if row:
        group_serial = row[2]
      
        # 尋找要刪除刀的序號
        cursor = connection.cursor(prepared=True)
        sql = "SELECT serial_number,member_id from princess_connect.keep_knifes where server_id=? and group_serial=? order by serial_number limit ?,1"
        data = (server_id, group_serial, index-1)
        cursor.execute(sql, data)
        row = cursor.fetchone()
        cursor.close()
        if row:
          if member_id == row[1]:
            cursor = connection.cursor(prepared=True)
            sql = "DELETE from princess_connect.keep_knifes where serial_number=?"
            data = (row[0],)
            row = cursor.execute(sql, data)
            cursor.close()
            connection.commit()
            await send_obj.send('取消保留刀成功!')
            await Module.Kernel.Update.Update(send_obj, server_id, group_serial) # 更新刀表
          else:
            await send_obj.send('您並非該刀主人喔!')
        else:
          await send_obj.send('該刀不存在喔!')   
      else:
        await send_obj.send('這裡不是報刀頻道喔!')
      await Module.Kernel.DB_control.CloseConnection(connection, send_obj)

  else:
    await send_obj.send('序號必須大於0!')
