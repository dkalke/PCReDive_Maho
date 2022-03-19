# 將成員加入戰隊
# 新增資料庫 table:members
# server_id、member_id、group_serial、knifes(該帳號一天有幾刀)、period(偏好時段)

import datetime
import Module.Kernel.Discord_client
from discord_slash.utils.manage_commands import create_option
import Module.Kernel.DB_control
import Module.Kernel.Authentication
import Module.Kernel.define_value
import Module.Kernel.info_update

@Module.Kernel.Discord_client.slash.subcommand( base="captain",
                                  name="add_member" ,
                                  description="新增戰隊成員",
                                  options=[
                                    create_option(
                                      name="戰隊成員",
                                      description="輸入要指派的戰隊編號。",
                                      option_type=6,
                                      required=True
                                    )
                                  ],
                                  connector={ 
                                    "戰隊成員": "member"
                                  }
                                )
async def add_captain(ctx, member):
  connection = await Module.Kernel.DB_control.OpenConnection(ctx)
  if connection:
    row = await Module.Kernel.Authentication.IsCaptain(ctx ,'/captain add_member', connection, ctx.guild.id, ctx.author.id)
    if row:
      group_serial = row[0]
      if await Module.Kernel.Authentication.IsSignChannel(ctx, connection, group_serial):# 是否位於報刀頻道
        # 檢查成員是否已存在戰隊中
        cursor = connection.cursor(prepared=True)
        sql = "SELECT 1 FROM princess_connect.members WHERE server_id=? and member_id=? and group_serial=? LIMIT 0, 1"
        data = (ctx.guild.id, member.id, group_serial)
        cursor.execute(sql, data)
        row = cursor.fetchone()
        if not row:
          # 寫入成員名單
          sql = "INSERT INTO princess_connect.members (server_id, group_serial, member_id, period, last_sl_time) VALUES (?, ?, ?, ?, ?)"
          data = (ctx.guild.id, group_serial, member.id, Module.Kernel.define_value.Period.UNKNOW.value, datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")) # 預設三刀
          cursor.execute(sql, data)
          connection.commit() # 資料庫存檔

          # 加入身分組
          sql = "SELECT fighting_role_id FROM princess_connect.group WHERE server_id=? and group_serial=? LIMIT 0, 1"
          data = (ctx.guild.id, group_serial)
          cursor.execute(sql, data)
          row = cursor.fetchone()
          if row:            
            role = ctx.guild.get_role(row[0])
            if role:
              await member.add_roles(role)

          await Module.Kernel.info_update.info_update(ctx ,ctx.guild.id, group_serial)
          await ctx.send( member.name + ' 已新增為第' + str(group_serial) + '戰隊成員。')
        else:
          await ctx.send( member.name + ' 目前已為第' + str(group_serial) + '戰隊成員。')
        cursor.close

      await Module.Kernel.DB_control.CloseConnection(connection, ctx)
