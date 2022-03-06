import Module.Kernel.Name_manager
async def show_knifes(connection, server_id, group_serial, week, boss):
  knifes = ''
  cursor = connection.cursor(prepared=True)
  sql = "SELECT member_id FROM princess_connect.knifes WHERE server_id = ? and group_serial = ? and week=? and boss=?"
  data = (server_id, group_serial, week ,boss)
  cursor.execute(sql, data)
  row = cursor.fetchone()
  while row:
    mention = await Module.Kernel.Name_manager.get_mention(server_id, row[0])
    knifes = knifes + mention  + ' '
    row = cursor.fetchone()
  cursor.close()
  return knifes
