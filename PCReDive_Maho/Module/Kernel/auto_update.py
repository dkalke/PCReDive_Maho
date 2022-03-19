import Module.Kernel.Discord_client

async def auto_update():
  # 更新刀表與剩餘刀數表
  connection = await Module.Kernel.DB_control.OpenConnection(None)
  if connection:
    # 定期更新所有戰隊刀表與剩餘刀數表
    cursor = connection.cursor(prepared=True)
    sql = "SELECT server_id, group_serial, sign_channel_id FROM princess_connect.group"
    cursor.execute(sql)
    rows = cursor.fetchall()  
    for row in rows:
      server_id = row[0]
      group_serial = row[1]
      sign_channel_id = row[2]

      guild = Module.Kernel.Discord_client.bot.get_guild(server_id)
      if not guild == None:
        message_obj = None  # 取得報刀頻道
        try:
          sign_channel_obj = guild.get_channel(sign_channel_id) # 錯誤訊息都會發到報刀頻道
          await Module.Kernel.Update.Update(sign_channel_obj, server_id, group_serial) # 更新刀表
          await Module.Kernel.info_update.info_update(sign_channel_obj ,server_id, group_serial) # 更新資訊表
        except:
          print('伺服器:' + str(server_id) + ', 編號' + str(group_serial) + '頻道:' + str(sign_channel_id) + '報刀頻道不存在!')
      else: # 不存在的戰隊資料
        pass

    cursor.close
    await Module.Kernel.DB_control.CloseConnection(connection, None)
    print('5AM updated.')
