﻿# 將成員加入戰隊
# 新增資料庫 table:members
# server_id、member_id、group_serial、knifes(該帳號一天有幾刀)、period(偏好時段)

import datetime
import Module.Kernel.Discord_client
from discord_slash.utils.manage_commands import create_option
import Module.Kernel.DB_control
import Module.Kernel.Authentication
import Module.Kernel.Name_manager
import Module.Kernel.info_update

@Module.Kernel.Discord_client.slash.subcommand( base="captain",
                                  name="delete_member" ,
                                  description="移除戰隊成員",
                                  options=[
                                    create_option(
                                      name="成員序號",
                                      description="請查看資訊頻道，輸入要移除的成員序號",
                                      option_type=4,
                                      required=True
                                    )
                                  ],
                                  connector={ 
                                    "成員序號": "index"
                                  }
                                )
async def delete_member(ctx, index):
  if index > 0:
    connection = await Module.Kernel.DB_control.OpenConnection(ctx)
    if connection:
      row = await Module.Kernel.Authentication.IsCaptain(ctx ,'/captain delete_member', connection, ctx.guild.id, ctx.author.id)
      if row:
        group_serial = row[0]
        if await Module.Kernel.Authentication.IsSignChannel(ctx,connection,group_serial):
          # 檢查成員是否已存在戰隊中
          cursor = connection.cursor(prepared=True)
          sql = "SELECT a.serial_number, a.member_id, a.period, a.sockpuppet, a.last_sl_time, b.normal, b.reserved \
          FROM princess_connect.members a \
          LEFT JOIN princess_connect.knife_summary b ON a.serial_number = b.serial_number and day = ?\
          WHERE server_id = ?  and group_serial = ?\
          ORDER BY a.serial_number, a.sockpuppet limit ?,1"
          data = (Module.Kernel.get_closest_end_time.get_closest_end_time(datetime.datetime.now()) - datetime.timedelta(days=1), ctx.guild.id, group_serial, index-1)
          cursor.execute(sql, data)
          row = cursor.fetchone()
          if row:
            # 移除成員
            member_id = row[1]
            sql = "Delete from princess_connect.members where server_id=? and member_id=? and group_serial=?"
            data = (ctx.guild.id, member_id, group_serial)
            cursor.execute(sql, data)
            connection.commit() # 資料庫存檔

            member = ctx.author.guild.get_member(member_id)
            if member:
              # 移除身分組
              sql = "SELECT fighting_role_id FROM princess_connect.group WHERE server_id=? and group_serial=? LIMIT 0, 1"
              data = (ctx.guild.id, group_serial)
              cursor.execute(sql, data)
              row = cursor.fetchone()
              if row:            
                role = ctx.guild.get_role(row[0])
                if role:
                  await member.remove_roles(role)

            nick_name = await Module.Kernel.Name_manager.get_nick_name(ctx.guild.id, member_id)
            await Module.Kernel.info_update.info_update(ctx ,ctx.guild.id, group_serial)
            await ctx.send( nick_name + ' 已從第' + str(group_serial) + '戰隊移除。')
          else:
            await ctx.send( '該序號不存在。')

          cursor.close
          await Module.Kernel.DB_control.CloseConnection(connection, ctx)
  else:
    await ctx.send( '成員序號必須大於0')
