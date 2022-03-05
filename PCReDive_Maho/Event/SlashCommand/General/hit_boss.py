import Module.Kernel.Discord_client
import Module.Kernel.DB_control
import Module.Kernel.Name_manager

@Module.Kernel.Discord_client.slash.slash( 
             name="hb" ,
             description="tag現在要打王的人",
             )
async def hit_boss(ctx):
  # check頻道，並找出所屬組別
  connection = await Module.Kernel.DB_control.OpenConnection(ctx)
  if connection:
    cursor = connection.cursor(prepared=True)
    sql = "SELECT now_week, now_boss, group_serial FROM princess_connect.group WHERE server_id = ? and sign_channel_id = ? order by group_serial limit 0, 1"
    data = (ctx.guild.id, ctx.channel.id)
    cursor.execute(sql, data) # 認證身分
    row = cursor.fetchone()
    cursor.close()
    if row:
      now_week = row[0]
      now_boss = row[1]
      group_serial = row[2]
      knifes = ''
      cursor = connection.cursor(prepared=True)
      sql = "SELECT member_id FROM princess_connect.knifes WHERE server_id = ? and group_serial = ? and week=? and boss=?"
      data = (ctx.guild.id, group_serial, now_week ,now_boss)
      cursor.execute(sql, data)
      row = cursor.fetchone()
      while row:
        mention = await Name_manager.get_mention(ctx, row[0])
        knifes = knifes + mention  + ' '
        row = cursor.fetchone()
      cursor.close()

      if knifes == '':
        await ctx.send('目前' + str(now_week) + '週' + str(now_boss) + '王沒人報刀喔，看在真步的面子上，快來報刀!')
      else:
        await ctx.send(knifes + str(now_week) + '週' + str(now_boss) + '王到囉!')
    else:
      await ctx.send('這裡不是報刀頻道喔!')

    await Module.Kernel.DB_control.CloseConnection(connection, ctx)