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
        cursor = connection.cursor(prepared=True)
        # 尋找戰隊有無存在
        row = Module.Authentication.IsExistGroup(ctx,connection, ctx.guild.id, group_serial)
        if row: 
          # 停用隊長權限
          sql = "UPDATE princess_connect.members SET is_captain = '0' where server_id = ? and group_serial = ? and member_id = ?"
          data = (ctx.guild.id, group_serial, member.id)
          cursor.execute(sql, data)
          cursor.close
          connection.commit() # 資料庫存檔
          await ctx.send('已移除 ' + member.name + ' 第' + str(group_serial) + '戰隊隊長身分。')
        else:
          await ctx.send('第' + str(group_serial) + '戰隊不存在!')    
        await Module.DB_control.CloseConnection(connection, ctx)
  else:
    await ctx.send('戰隊編號只能是正整數。')