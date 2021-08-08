import Discord_client
import Module.DB_control
import Module.Offset_manager
import Module.Update


async def auto_clear():
  print("AA")
  connection = await Module.DB_control.OpenConnection(None)
  print("AAA")
  if connection:
    cursor = connection.cursor(prepared=True)

    # 刪除保留刀表
    sql = "DELETE FROM princess_connect.keep_knifes"
    cursor.execute(sql)

    # 刪除刀表
    sql = "DELETE FROM princess_connect.knifes"
    cursor.execute(sql)

    # 重設boss次序
    sql = "UPDATE princess_connect.group SET now_week='1', now_boss='1'"
    cursor.execute(sql)

    connection.commit()

    # 更新所有戰隊刀表
    sql = "SELECT server_id, group_serial, table_channel_id FROM princess_connect.group"
    cursor.execute(sql)
    rows = cursor.fetchall()  
    for row in rows:
      server_id = row[0]
      group_serial = row[1]
      table_channel_id = row[2]

      # 取得刀表頻道
      guild = Discord_client.client.get_guild(server_id)
      if not guild == None:
        channel = guild.get_channel(table_channel_id)
        message_obj = await channel.send(content='已完成月中重置流程，刀表已清除!')
        Module.Offset_manager.AutoOffset(connection, server_id, group_serial) # 自動周目控制
        await Module.Update.Update(message_obj, server_id, group_serial) # 更新刀表
        print('伺服器:' + str(server_id) + ', 編號' + str(group_serial) + '頻道:' + str(table_channel_id) + '清除完成!')
      else: # 清除不存在的戰隊資料
        sql = "DELETE FROM princess_connect.group where server_id = ? and group_serial = ?"
        data = (server_id, group_serial)
        cursor.execute(sql, data)

        sql = "DELETE FROM princess_connect.group_captain where server_id = ? and group_serial = ?"
        data = (server_id, group_serial)
        cursor.execute(sql, data)
        print('伺服器:' + str(server_id) + ', 編號' + str(group_serial) + '頻道:' + str(table_channel_id) + '已從資料庫移除')

    connection.commit()
    cursor.close
    await Module.DB_control.CloseConnection(connection, None)
    print('已經清除所有刀表')