import Module.Kernel.Discord_client
from discord_slash.utils.manage_commands import create_option
import Module.Kernel.DB_control
import Module.Kernel.Authentication

@Module.Kernel.Discord_client.slash.subcommand( base="captain",
                                  name="set_fighting_role" ,
                                  description="設定戰鬥中身分組",
                                  options=[
                                    create_option(
                                      name="身分組",
                                      description="選擇一個身分組作為戰鬥中身分組，可用來一次性tag其餘尚未完刀的成員。",
                                      option_type=8,
                                      required=True
                                    )
                                  ],
                                  connector={ 
                                    "身分組": "role",
                                  }
                                )
async def set_fighting_role(ctx, role):
  connection = await Module.Kernel.DB_control.OpenConnection(ctx)
  if connection:
    row = await Module.Kernel.Authentication.IsCaptain(ctx ,'/captain set_fighting_role', connection, ctx.guild.id, ctx.author.id)
    if row:
      group_serial = int(row[0])
      if await Module.Kernel.Authentication.IsSignChannel(ctx,connection,group_serial):
        # 檢查有無重複
        cursor = connection.cursor(prepared=True)
        sql = "SELECT group_serial FROM princess_connect.group WHERE server_id=? and fighting_role_id =? LIMIT 0, 1"
        data = (ctx.guild.id, role.id)
        cursor.execute(sql, data)
        row = cursor.fetchone()
        cursor.close
        if not row:
          cursor = connection.cursor(prepared=True)
          sql = "UPDATE princess_connect.group SET fighting_role_id = ? WHERE server_id = ? and group_serial = ? "
          data = (role.id, ctx.guild.id, group_serial)
          cursor.execute(sql, data)
          cursor.close
          connection.commit()
          await ctx.send(role.mention + '已指派為第' + str(group_serial) + '戰隊戰鬥中身分組!')
        else:
          if not int(row[0]) == group_serial:
            await ctx.send('戰鬥中身分組與其他戰隊重複，請重新設定!')
          else: # 指派一樣的身分組，SQL不處理但再次顯示成功訊息
            await ctx.send(role.mention + '已指派為第' + str(group_serial) + '戰隊戰鬥中身分組!')
      
    await Module.Kernel.DB_control.CloseConnection(connection, ctx)