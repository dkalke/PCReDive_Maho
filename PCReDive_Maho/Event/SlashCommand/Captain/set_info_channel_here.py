import Module.Kernel.Discord_client
import Module.Kernel.DB_control
import Module.Kernel.Authentication
import Module.Kernel.info_update

@Module.Kernel.Discord_client.slash.subcommand( base="captain",
                                  name="set_info_channel_here" ,
                                  description="將目前位置做為資訊頻道"
                                )
async def set_info_channel_here(ctx):
  connection = await Module.Kernel.DB_control.OpenConnection(ctx)
  if connection:
    row = await Module.Kernel.Authentication.IsCaptain(ctx, '/captain set_info_channel_here', connection, ctx.guild.id, ctx.author.id)
    if row:
      group_serial = int(row[0])
      info_message = await ctx.send('資訊是吧，了解!')

      # 寫入資料庫
      cursor = connection.cursor(prepared=True)
      sql = "UPDATE princess_connect.group SET info_channel_id = ?, info_message_id = ? WHERE server_id = ? and group_serial = ? "
      data = (ctx.channel.id, info_message.id, ctx.guild.id, group_serial)
      cursor.execute(sql, data)
      cursor.close
      connection.commit()
      await Module.Kernel.info_update.info_update(ctx ,ctx.guild.id, group_serial)
            
    await Module.Kernel.DB_control.CloseConnection(connection, ctx)