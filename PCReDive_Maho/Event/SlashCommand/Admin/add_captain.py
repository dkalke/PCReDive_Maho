import datetime
import Discord_client
from discord_slash.utils.manage_commands import create_option
import Module.DB_control
import Module.Authentication

@Discord_client.slash.subcommand( base="admin",
                                  name="add_captain" ,
                                  description="新增隊長到指定戰隊。",
                                  options=[
                                    create_option(
                                      name="戰隊編號",
                                      description="輸入要指派的戰隊編號。",
                                      option_type=4,
                                      required=True
                                    ),
                                    create_option(
                                      name="隊長",
                                      description="mention成員。",
                                      option_type=6,
                                      required=True
                                    ),
                                  ],
                                  connector={ 
                                    "戰隊編號": "group_serial",
                                    "隊長": "member",
                                  }
                                )
async def add_captain(ctx, group_serial, member):
  if group_serial > 0:
    if await Module.Authentication.IsAdmin(ctx ,'/add_captain'):
      connection = await Module.DB_control.OpenConnection(ctx)
      if connection:
        # 尋找戰隊有無存在
        row = Module.Authentication.IsExistGroup(ctx,connection, ctx.guild.id, group_serial)
        if row: 
          # 檢查成員有無再其他戰隊當隊長
          cursor = connection.cursor(prepared=True)
          sql = "SELECT * FROM princess_connect.group_captain WHERE server_id=? and member_id=? LIMIT 0, 1"
          data = (ctx.guild.id, member.id)
          cursor.execute(sql, data)
          row = cursor.fetchone()
          cursor.close
          if not row:
            # 寫入隊長名單
            cursor = connection.cursor(prepared=True)
            sql = "INSERT INTO princess_connect.group_captain (server_id, group_serial, member_id) VALUES (?, ?, ?)"
            data = (ctx.guild.id, group_serial, member.id)
            cursor.execute(sql, data)
            cursor.close
            connection.commit() # 資料庫存檔
            await ctx.send( member.name + ' 已為第' + str(group_serial) + '戰隊隊長。')
          else:
            await ctx.send('新增失敗， ' + member.name + ' 已為其他戰隊隊長。')
        else:
          await ctx.send('第' + str(group_serial) + '戰隊不存在!')    
        await Module.DB_control.CloseConnection(connection, ctx)
  else:
    await ctx.send('戰隊編號只能是正整數。')