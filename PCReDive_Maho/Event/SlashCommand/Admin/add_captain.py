import datetime
import Module.Kernel.Discord_client
from discord_slash.utils.manage_commands import create_option
import Module.Kernel.DB_control
import Module.Kernel.Authentication
import Module.Kernel.info_update

@Module.Kernel.Discord_client.slash.subcommand( base="admin",
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
    if await Module.Kernel.Authentication.IsAdmin(ctx ,'/add_captain'):
      connection = await Module.Kernel.DB_control.OpenConnection(ctx)
      if connection:
        # 尋找戰隊有無存在
        row = Module.Kernel.Authentication.IsExistGroup(ctx,connection, ctx.guild.id, group_serial)
        fighting_role_id = row[0]
        cursor = connection.cursor(prepared=True)
        if row: 
          user_db_id = None
          # 檢查成員是否有在該戰隊成員表內
          sql = "SELECT serial_number FROM princess_connect.members WHERE server_id=? and member_id=? and group_serial=? and sockpuppet='0'"
          data = (ctx.guild.id, member.id, group_serial)
          cursor.execute(sql, data)
          row = cursor.fetchone()
          if not row:# 若無則新增
            sql = "INSERT INTO princess_connect.members (server_id, group_serial, member_id) VALUES (?, ?, ?) RETURNING serial_number"
            data = (ctx.guild.id, group_serial, member.id)
            cursor.execute(sql, data)
            row = cursor.fetchone()
            user_db_id = row[0]
          else:
            user_db_id = row[0]

          # 檢查是否為其他戰隊隊長
          sql = "SELECT count(*) FROM princess_connect.members WHERE server_id=? and member_id=? and is_captain = '1'"
          data = (ctx.guild.id, member.id)
          cursor.execute(sql, data)
          row = cursor.fetchone()
          if row[0] == 0:
            # 啟用隊長權限
            sql = "UPDATE princess_connect.members SET is_captain = '1' where serial_number = ?"
            data = (user_db_id, )
            cursor.execute(sql, data)
            cursor.close
            connection.commit() # 資料庫存檔

            # 加入身分組
            role = ctx.guild.get_role(fighting_role_id)
            if role:
              await member.add_roles(role)

            await ctx.send( member.name + ' 已新增為第' + str(group_serial) + '戰隊隊長。')
            await Module.Kernel.info_update.info_update(ctx ,ctx.guild.id, group_serial)
          else:
            await ctx.send( member.name + ' 目前已有戰隊隊長身分，不可重複指派。')
        else:
          await ctx.send('第' + str(group_serial) + '戰隊不存在!')    
        await Module.Kernel.DB_control.CloseConnection(connection, ctx)
  else:
    await ctx.send('戰隊編號只能是正整數。')