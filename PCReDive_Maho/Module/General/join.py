import datetime

import Module.Kernel.DB_control
import Module.Kernel.Name_manager
import Module.Kernel.define_value
import Module.Kernel.info_update


async def join(send_obj, server_id, sign_channel_id, member_id):
  # check頻道，並找出所屬組別
  connection = await Module.Kernel.DB_control.OpenConnection(send_obj)
  if connection:
    # 尋找該頻道所屬戰隊
    cursor = connection.cursor(prepared=True)
    sql = "SELECT group_serial, fighting_role_id FROM princess_connect.group WHERE server_id = ? and sign_channel_id = ?"
    data = (server_id, sign_channel_id)
    cursor.execute(sql, data)
    row = cursor.fetchone()
    if row:
      group_serial = row[0]
      fighting_role_id = row[1]
      # 檢查是否已經是該戰隊成員
      sql = "SELECT 1 FROM princess_connect.members WHERE server_id = ? and group_serial=? and member_id = ? and sockpuppet = '0'"
      data = (server_id, group_serial, member_id)
      cursor.execute(sql, data)
      row = cursor.fetchone()
      nick_name = await Module.Kernel.Name_manager.get_nick_name(server_id, member_id)
      if not row:
        # 寫入成員名單
        sql = "INSERT INTO princess_connect.members (server_id, group_serial, member_id, period, last_sl_time) VALUES (?, ?, ?, ?, ?)"
        data = (server_id, group_serial, member_id, Module.Kernel.define_value.Period.UNKNOW.value, datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
        cursor.execute(sql, data)

        # 加入身分組
        role = send_obj.guild.get_role(fighting_role_id)
        if role:
          await send_obj.author.add_roles(role)
        
        connection.commit() # 資料庫存檔
        await send_obj.send( nick_name + ' 已新增為第' + str(group_serial) + '戰隊成員。')
        await Module.Kernel.info_update.info_update(send_obj ,server_id, group_serial)
      else:
        await send_obj.send( nick_name + ' 目前已為第' + str(group_serial) + '戰隊成員。')
    cursor.close
    await Module.Kernel.DB_control.CloseConnection(connection, send_obj)
