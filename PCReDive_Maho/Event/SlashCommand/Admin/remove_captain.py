import datetime
import Discord_client
from discord_slash.utils.manage_commands import create_option
import Module.DB_control
import Module.Authentication

@Discord_client.slash.subcommand( base="admin",
                                  name="remove_captain" ,
                                  description="移除成員的戰隊隊長身分",
                                  options=[
                                    create_option(  
                                      name="戰隊編號",
                                      description="指定戰隊編號",
                                      option_type=4,
                                      required=True
                                    ),
                                    create_option(
                                      name="隊長",
                                      description="mention要移除的隊長",
                                      option_type=6,
                                      required=True
                                    ),
                                  ],
                                  connector={ 
                                    "戰隊編號": "group_serial",
                                    "隊長": "member",
                                  }
                                )
async def delete_group(ctx, group_serial, member):
  if group_serial > 0:
    if await Module.Authentication.IsAdmin(ctx ,'/remove_captain'):
      connection = await Module.DB_control.OpenConnection(ctx)
      if connection:
        # 尋找戰隊有無存在
        row = Module.Authentication.IsExistGroup(ctx,connection, ctx.guild.id, group_serial)
        if row: 
          # 檢查成員是否為該戰隊隊長
          cursor = connection.cursor(prepared=True)
          sql = "SELECT * FROM princess_connect.group_captain WHERE server_id=? and group_serial=? and member_id=? LIMIT 0, 1"
          data = (ctx.guild.id, group_serial, member.id)
          cursor.execute(sql, data)
          row = cursor.fetchone()
          cursor.close
          if row:
            # 刪除隊長名單
            cursor = connection.cursor(prepared=True)
            sql = "DELETE FROM princess_connect.group_captain WHERE server_id=? and group_serial=? and member_id=?"
            data = (ctx.guild.id, group_serial, member.id)
            cursor.execute(sql, data)
            cursor.close
            connection.commit() # 資料庫存檔
            await ctx.send('已移除 ' + member.name + ' 第' + str(group_serial) + '戰隊隊長身分。')
          else:
            await ctx.send('移除失敗， ' + member.name + ' 不具有第' + str(group_serial) + '戰隊隊長身分。')
        else:
          await ctx.send('第' + str(group_serial) + '戰隊不存在!')    
        await Module.DB_control.CloseConnection(connection, ctx)
  else:
    await ctx.send('戰隊編號只能是正整數。')