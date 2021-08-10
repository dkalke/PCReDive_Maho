from discord_slash.utils.manage_commands import create_option
import Discord_client
import Module.DB_control
import Module.Update

#!取消保留刀 [第幾刀]
@Discord_client.slash.slash( 
             name="ckp" ,
             description="取消自己在保留區的刀",
             options= [
                 create_option(
                     name="序號",
                     description="請查看刀表，填入該刀在保留區中的序號",
                     option_type=4,
                     required=True
                 )
             ],
             connector={"序號": "index"}
             )
async def cancel_keep_proposal(ctx, index):
  connection = await Module.DB_control.OpenConnection(ctx)
  if connection:
    cursor = connection.cursor(prepared=True)
    sql = "SELECT  now_week, now_boss, week_offset, group_serial FROM princess_connect.group WHERE server_id = ? and sign_channel_id = ? order by group_serial limit 0, 1"
    data = (ctx.guild.id, ctx.channel.id)
    cursor.execute(sql, data) # 認證身分
    row = cursor.fetchone()
    cursor.close
    if row:
      group_serial = row[3]
      if index > 0:
        # 尋找要刪除刀的序號
        cursor = connection.cursor(prepared=True)
        sql = "SELECT serial_number,member_id from princess_connect.keep_knifes where server_id=? and group_serial=? order by boss limit ?,1"
        data = (ctx.guild.id, group_serial, index-1)
        cursor.execute(sql, data)
        row = cursor.fetchone()
        cursor.close()
        if row:
          if ctx.author.id == row[1]:
            cursor = connection.cursor(prepared=True)
            sql = "DELETE from princess_connect.keep_knifes where serial_number=?"
            data = (row[0],)
            row = cursor.execute(sql, data)
            cursor.close()
            connection.commit()
            await ctx.send('取消保留刀成功!')
            await Module.Update.Update(ctx, ctx.guild.id, group_serial) # 更新刀表
          else:
            await ctx.send('您並非該刀主人喔!')
        else:
          await ctx.send('該刀不存在喔!')   
      else:
        await ctx.send('序號必須大於0!')
    else:
      await ctx.send('這裡不是報刀頻道喔!')
    await Module.DB_control.CloseConnection(connection, ctx)