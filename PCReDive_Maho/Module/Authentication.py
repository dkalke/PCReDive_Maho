async def IsAdmin(message, command):
  if message.author.guild_permissions.administrator:  
    return True
  else:
    await message.channel.send(command+ ' 您的權限不足!')
    return False

async def IsCaptain(message, command, connection, server_id, member_id):
  cursor = connection.cursor(prepared=True)
  sql = "SELECT group_serial FROM princess_connect.group_captain WHERE server_id = ? and member_id = ?  LIMIT 0, 1"
  data = (server_id, member_id)
  cursor.execute(sql, data)
  row = cursor.fetchone()
  cursor.close
  if row:
    return row
  else:
    await message.channel.send(command+ ' 您的權限不足!')

async def IsController(message, command, connection, server_id):
  group_serial = 0
  now_week = 0
  now_boss = 0
  week_offset = 0
  cursor = connection.cursor(prepared=True)
  sql = "SELECT now_week, now_boss, week_offset, group_serial, controller_role_id FROM princess_connect.group WHERE server_id = ? order by group_serial"
  data = (server_id,)
  cursor.execute(sql, data) # 認證身分
  row = cursor.fetchone()
  while row and group_serial == 0:
    for role in message.author.roles:
      if role.id == row[4]:
        now_week = row[0]
        now_boss = row[1]
        week_offset = row[2]
        group_serial = row[3]
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

  return ( now_week, now_boss, week_offset, group_serial )

def IsExistGroup(message, connection, server_id, group_serial):
  cursor = connection.cursor(prepared=True)
  sql = "SELECT * FROM princess_connect.group WHERE server_id = ? and group_serial = ? limit 0, 1"
  data = (server_id, group_serial)
  cursor.execute(sql, data)
  row = cursor.fetchone()
  cursor.close
  return row
