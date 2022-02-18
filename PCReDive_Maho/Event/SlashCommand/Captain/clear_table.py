import Discord_client
import Module.DB_control
import Module.Authentication

@Discord_client.slash.subcommand( base="captain",
                                  name="clear_table" ,
                                  description="清除刀表",                                 
                                )
async def clear_table(ctx):
  connection = await Module.DB_control.OpenConnection(ctx)
  if connection:
    row = await Module.Authentication.IsCaptain(ctx ,'/captain clear_table', connection, ctx.guild.id, ctx.author.id)
    if row:
      group_serial = row[0]
      if await Module.Authentication.IsSignChannel(ctx,connection,group_serial):
        # 刪除保留刀表
        cursor = connection.cursor(prepared=True)
        sql = "DELETE FROM princess_connect.keep_knifes WHERE server_id = ? and group_serial = ?"
        data = (ctx.guild.id, group_serial)
        cursor.execute(sql, data)
        cursor.close

        # 刪除刀表
        cursor = connection.cursor(prepared=True)
        sql = "DELETE FROM princess_connect.knifes WHERE server_id = ? and group_serial = ?"
        data = (ctx.guild.id, group_serial)
        cursor.execute(sql, data) 
        cursor.close

        # 重設boss次序
        cursor = connection.cursor(prepared=True)
        sql = "UPDATE princess_connect.group SET now_week='1', now_week_1='1', now_week_2='1', now_week_3='1', now_week_4='1', now_week_5='1', now_boss='1' WHERE server_id = ? and group_serial=?"
        data = (ctx.guild.id, group_serial)
        cursor.execute(sql, data)
        cursor.close
        connection.commit()
        await ctx.send('第'+ str(group_serial) +'戰隊刀表被真步吃光光拉!')
        Module.Offset_manager.AutoOffset(connection, ctx.guild.id, group_serial) # 自動周目控制
        await Module.Update.Update(ctx, ctx.guild.id, group_serial) # 更新刀表

    await Module.DB_control.CloseConnection(connection, ctx)