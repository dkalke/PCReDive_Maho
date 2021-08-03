from discord import Embed
import Discord_client
import Module.DB_control
import Module.Authentication

@Discord_client.slash.subcommand( base="captain", 
                                  name="set_table_channel_here", 
                                  description="將目前位置做為刀表頻道"
                                )
async def set_table_channel_here(ctx):
  connection = await Module.DB_control.OpenConnection(ctx)
  if connection:
    row = await Module.Authentication.IsCaptain(ctx, '/captain set_table_channel_here', connection, ctx.guild.id, ctx.author.id)
    if row:
      group_serial = int(row[0])
      cursor = connection.cursor(prepared=True)
      sql = "SELECT group_serial FROM princess_connect.group WHERE server_id = ? and table_channel_id = ? and group_serial <> ? limit 0, 1"
      data = (ctx.guild.id, ctx.channel.id, group_serial)
      cursor.execute(sql, data)
      row = cursor.fetchone()
      cursor.close
      if not row:
        cursor = connection.cursor(prepared=True)
        sql = "SELECT table_style FROM princess_connect.group WHERE server_id = ? and group_serial = ? limit 0, 1"
        data = (ctx.guild.id, group_serial)
        cursor.execute(sql, data)
        row = cursor.fetchone()
        cursor.close
        if row :
          if row[0] == 0:
            embed_msg = Embed(description="初始化刀表中!",color=0xD98B99)
            table_message = await ctx.send(embed = embed_msg)
            embed_msg = Embed(description="初始化暫存刀表中!",color=0xD9ACA3)
            knife_pool_message = await ctx.send(embed = embed_msg)
          else:
            msg = "初始化刀表中!"
            table_message = await ctx.send(msg)
            msg = "初始化暫存刀表中!"
            knife_pool_message = await ctx.send(msg)

          # 寫入資料庫
          cursor = connection.cursor(prepared=True)
          sql = "UPDATE princess_connect.group SET table_channel_id = ? ,table_message_id = ?, knife_pool_message_id=? WHERE server_id = ? and group_serial = ? "
          data = (ctx.channel.id, table_message.id, knife_pool_message.id, ctx.guild.id, group_serial)
          cursor.execute(sql, data)
          cursor.close
          connection.commit()
          await Module.Update.Update(ctx, ctx.guild.id, group_serial)
        else:
          await ctx.send('查無戰隊資料!') 
      else:
        await ctx.send('這裡是第'+ str(row[0]) +'戰隊的刀表頻道，請重新選擇!')

    await Module.DB_control.CloseConnection(connection, ctx)