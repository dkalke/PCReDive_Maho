import Discord_client
import Module.DB_control
import Module.Authentication

@Discord_client.slash.subcommand( base="captain",
                                  name="set_sign_channel_here" ,
                                  description="將目前位置做為報刀頻道"
                                )
async def set_sign_channel_here(ctx):
  connection = await Module.DB_control.OpenConnection(ctx)
  if connection:
    row = await Module.Authentication.IsCaptain(ctx, '/captain set_sign_channel_here', connection, ctx.guild.id, ctx.author.id)
    if row:
      group_serial = int(row[0])
      cursor = connection.cursor(prepared=True)
      sql = "SELECT group_serial FROM princess_connect.group WHERE server_id = ? and sign_channel_id = ? and group_serial <> ? limit 0, 1"
      data = (ctx.guild.id, ctx.channel.id, group_serial)
      cursor.execute(sql, data)
      row = cursor.fetchone()
      cursor.close
      if not row:
        # 寫入資料庫
        cursor = connection.cursor(prepared=True)
        sql = "UPDATE princess_connect.group SET sign_channel_id = ? WHERE server_id = ? and group_serial = ? "
        data = (ctx.channel.id, ctx.guild.id, group_serial)
        cursor.execute(sql, data)
        cursor.close
        connection.commit()
        await ctx.send('報刀是吧，了解!')
      else:
        await ctx.send('這裡是第'+ str(row[0]) +'戰隊的報刀頻道，請重新選擇!')
            
    await Module.DB_control.CloseConnection(connection, ctx)