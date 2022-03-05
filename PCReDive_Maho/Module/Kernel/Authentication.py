async def IsAdmin(message, command):
  if message.author.guild_permissions.administrator:  
    return True
  else:
    await message.channel.send(command+ ' 您的權限不足!')
    return False

async def IsCaptain(message, command, connection, server_id, member_id):
  cursor = connection.cursor(prepared=True)
  sql = "SELECT group_serial FROM princess_connect.members WHERE server_id = ? and member_id = ? and is_captain = '1' LIMIT 0, 1"
  data = (server_id, member_id)
  cursor.execute(sql, data)
  row = cursor.fetchone()
  cursor.close
  if row:
    return row
  else:
    await message.send(command+ ' 您的權限不足!')

async def IsController(message, command, connection, server_id):
  group_serial = 0
  main_week = 0
  now_week = None
  week_offset = 0
  cursor = connection.cursor(prepared=True)
  sql = "SELECT now_week, now_week_1, now_week_2, now_week_3, now_week_4, now_week_5, week_offset, group_serial, controller_role_id FROM princess_connect.group WHERE server_id = ? order by group_serial"
  data = (server_id,)
  cursor.execute(sql, data) # 認證身分
  row = cursor.fetchone()
  while row and group_serial == 0:
    for role in message.author.roles:
      if role.id == row[8]:
        main_week = row[0]
        now_week = [row[1], row[2], row[3], row[4], row[5]]
        week_offset = row[6]
        group_serial = row[7]
        # TODO 如果一個人多個戰隊的控刀手權限，目前僅會執行編號最小的戰隊
        break
    row = cursor.fetchone()

  try:
    cursor.fetchall()  # fetch (and discard) remaining rows
  except mysql.connector.errors.InterfaceError as ie:
      if ie.msg == 'No result set to fetch from.':
          # no problem, we were just at the end of the result set
          pass
      else:
          raise
  cursor.close
  if group_serial == 0: # 如果是控刀手
    await message.channel.send(command + ' 發生錯誤，您沒有控刀手權限!')

  return ( main_week, now_week, week_offset, group_serial )

def IsExistGroup(message, connection, server_id, group_serial):
  cursor = connection.cursor(prepared=True)
  sql = "SELECT * FROM princess_connect.group WHERE server_id = ? and group_serial = ? limit 0, 1"
  data = (server_id, group_serial)
  cursor.execute(sql, data)
  row = cursor.fetchone()
  cursor.close
  return row


async def IsSignChannel(message, connection, group_serial):
  # 是否在所屬戰隊的頻道中
  server_id = message.guild.id
  cursor = connection.cursor(prepared=True)
  sql = "SELECT sign_channel_id FROM princess_connect.group WHERE server_id = ? and group_serial = ? limit 0, 1"
  data = (server_id, group_serial)
  cursor.execute(sql, data)
  row = cursor.fetchone()
  cursor.close
  if row:
    if row[0] == None:
      await message.send('請戰隊隊長設定報刀頻道!')
      return False
    elif row[0] == message.channel.id:
      return True
    else:
      await message.send('請在戰隊內報刀頻道使用!')
      return False
  else:
    await message.send('發生錯誤，該戰隊編號不存在!')
    return False
  
  