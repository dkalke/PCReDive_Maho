import Module.Kernel.DB_control
import Module.Kernel.Name_manager
import Module.Kernel.info_update


async def leave(send_obj, server_id, sign_channel_id, member_id):
  # check頻道，並找出所屬組別
  connection = await Module.Kernel.DB_control.OpenConnection(send_obj)
  if connection:
    # 尋找該頻道所屬戰隊
    cursor = connection.cursor(prepared=True)
    sql = "SELECT group_serial FROM princess_connect.group WHERE server_id = ? and sign_channel_id = ?"
    data = (server_id, sign_channel_id)
    cursor.execute(sql, data)
    row = cursor.fetchone()
    if row:
      group_serial = row[0]
      # 檢查是否已經是該戰隊成員
      sql = "SELECT 1 FROM princess_connect.members WHERE server_id = ? and group_serial=? and member_id = ? and sockpuppet = '0'"
      data = (server_id, group_serial, member_id)
      cursor.execute(sql, data)
      row = cursor.fetchone()
      nick_name = await Module.Kernel.Name_manager.get_nick_name(server_id, member_id)
      if row:
        # 自成員名單中移除，一併並刪除分身
        sql = "DELETE FROM princess_connect.members where server_id = ? and group_serial = ? and member_id =?"
        data = (server_id, group_serial, member_id)
        cursor.execute(sql, data)
        
        connection.commit() # 資料庫存檔
        await send_obj.send( nick_name + ' 已退出第' + str(group_serial) + '戰隊。')
        await Module.Kernel.info_update.info_update(send_obj ,server_id, group_serial)
      else:
        await send_obj.send( nick_name + ' 你不是第' + str(group_serial) + '戰隊成員喔。')
    cursor.close
    await Module.Kernel.DB_control.CloseConnection(connection, send_obj)
