﻿from discord_slash.utils.manage_commands import create_option
import Module.Kernel.Discord_client
import Module.Kernel.DB_control
import Module.Kernel.Authentication
import Module.Kernel.Update

#!刪除保留刀 [第幾刀]
@Module.Kernel.Discord_client.slash.subcommand( base="controller", 
                                  name="delete_keep_knife", 
                                  description="強制刪除保留刀，將該刀從保留區移除",
                                  options=[
                                    create_option(
                                      name="序號",
                                      description="請查閱保留區並輸入要移除的序號",
                                      option_type=4,
                                      required=True
                                    )  
                                  ],
                                  connector={"序號": "index"}
                                )
async def delete_keep_knife(ctx, index):
  # check身分，並找出所屬組別
  connection = await Module.Kernel.DB_control.OpenConnection(ctx)
  if connection:
    ( main_week, now_week, week_offset, group_serial ) = await Module.Kernel.Authentication.IsController(ctx ,'/controller delete_keep_knife', connection, ctx.guild.id)
    if not group_serial == 0: # 如果是是控刀手
      if index > 0:
        # 尋找要刪除刀的序號
        cursor = connection.cursor(prepared=True)
        sql = "SELECT serial_number,member_id from princess_connect.keep_knifes where server_id=? and group_serial=? order by serial_number limit ?,1"
        data = (ctx.guild.id, group_serial, index-1)
        cursor.execute(sql, data)
        row = cursor.fetchone()
        cursor.close()
        if row:
          cursor = connection.cursor(prepared=True)
          sql = "DELETE from princess_connect.keep_knifes where serial_number=?"
          data = (row[0],)
          row = cursor.execute(sql, data)
          cursor.close()
          connection.commit()
          await ctx.send('刪除保留刀成功!')
          await Module.Kernel.Update.Update(ctx, ctx.guild.id, group_serial) # 更新刀表   
        else:
          await ctx.send('該保留刀不存在喔!') 
      else:
        await ctx.send('序號不可為負數!')

    await Module.Kernel.DB_control.CloseConnection(connection, ctx)