import Name_manager
async def show_knifes(connection, ctx, group_serial, week, boss):
  knifes = ''
  cursor = connection.cursor(prepared=True)
  sql = "SELECT member_id FROM princess_connect.knifes WHERE server_id = ? and group_serial = ? and week=? and boss=?"
  data = (ctx.guild.id, group_serial, week ,boss)
  cursor.execute(sql, data)
  row = cursor.fetchone()
  while row:
    mention = await Name_manager.get_mention(ctx, row[0])
    knifes = knifes + mention  + ' '
    row = cursor.fetchone()
  cursor.close()
  return knifes
