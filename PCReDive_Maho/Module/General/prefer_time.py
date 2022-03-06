import Module.Kernel.DB_control
import Module.Kernel.info_update

async def proposal_knife(send_obj, server_id, sign_channel_id, member_id, period):
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

      # 檢查使否屬於該戰隊
      cursor = connection.cursor(prepared=True)
      sql = "select * from princess_connect.members WHERE server_id = ? and group_serial = ? and member_id = ? limit 0,1"
      data = (server_id, group_serial, member_id)
      cursor.execute(sql, data)
      row = cursor.fetchone()
      if row:
        # 修改出刀偏好
        cursor = connection.cursor(prepared=True)
        sql = "update princess_connect.members SET period=? WHERE server_id = ? and group_serial = ? and member_id = ?"
        data = (period, server_id, group_serial, member_id)
        cursor.execute(sql, data)
        connection.commit()
        await Module.Kernel.info_update.info_update(send_obj ,server_id, group_serial)
        await send_obj.send('您在第' + str(group_serial) + '戰隊的出刀偏好時段已修改完成!')
      else:
        await send_obj.send('您不屬於第' + str(group_serial) + '戰隊喔!')
    else:
      await send_obj.send('這裡不是報刀頻道喔，請在所屬戰隊報刀頻道使用!')
    await Module.Kernel.DB_control.CloseConnection(connection, send_obj)
