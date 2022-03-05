﻿from discord_slash.utils.manage_commands import create_option, create_choice
import Module.Kernel.Discord_client
import Module.Kernel.DB_control
import Module.Kernel.Authentication
import Module.Kernel.Update

#!幫報保留刀 [幾王] [註解] [mention]
@Module.Kernel.Discord_client.slash.subcommand( base="controller", 
                                  name="keep_knife", 
                                  description="幫成員報一個保留刀",
                                  options=[
                                    create_option(
                                      name="備註",
                                      description="備註（預計傷害）",
                                      option_type=3,
                                      required=True
                                    ),
                                    create_option(
                                      name="成員",
                                      description="mention要幫忙報保留刀的成員。",
                                      option_type=6,
                                      required=True
                                    )
                                  ],
                                  connector={"備註": "comment","成員": "member"}
                                )
async def keep_knife(ctx, comment, member):
  # check身分，並找出所屬組別
  connection = await Module.Kernel.DB_control.OpenConnection(ctx)
  if connection:
    ( main_week, now_week, week_offset, group_serial ) = await Module.Kernel.Authentication.IsController(ctx ,'/controller keep_knife', connection, ctx.guild.id)
    if not group_serial == 0: # 如果是是控刀手
      # 寫入保留刀表
      cursor = connection.cursor(prepared=True)
      sql = "INSERT INTO princess_connect.keep_knifes (server_id, group_serial, member_id, comment) VALUES (?, ?, ?, ?)"
      data = (ctx.guild.id, group_serial, member.id, comment)
      cursor.execute(sql, data)
      cursor.close()
      connection.commit()
      await ctx.send('備註:' + comment + '，**保留刀**報刀成功!')
      await Module.Kernel.Update.Update(ctx, ctx.guild.id, group_serial) # 更新刀表

    await Module.Kernel.DB_control.CloseConnection(connection, ctx)