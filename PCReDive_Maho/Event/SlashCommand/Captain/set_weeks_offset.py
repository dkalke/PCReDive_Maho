from discord_slash.utils.manage_commands import create_option, create_choice
import Discord_client
import Module.DB_control
import Module.Authentication
import Module.Update
import Module.Offset_manager

level_options = [ create_choice(name="不提前", value=0),create_choice(name="1週目", value=1),create_choice(name="2週目", value=2),create_choice(name="3週目", value=3),create_choice(name="4週目", value=4),create_choice(name="5週目", value=5),
                  create_choice(name="6週目", value=6),create_choice(name="7週目", value=7),create_choice(name="8週目", value=8),create_choice(name="9週目", value=9),create_choice(name="10週目", value=10)
                ]

@Discord_client.slash.subcommand( base="captain",
                                  name="set_weeks_offset" ,
                                  description="設定各段可提前的週目數",
                                  options=[
                                    create_option(
                                      name="1階段",
                                      description="輸入1階段可提前週目數",
                                      option_type=4,
                                      required=True,
                                      choices=level_options
                                    ),
                                    create_option(
                                      name="2階段",
                                      description="輸入2階段可提前週目數",
                                      option_type=4,
                                      required=True,
                                      choices=level_options
                                    ),
                                    create_option(
                                      name="3階段",
                                      description="輸入3階段可提前週目數",
                                      option_type=4,
                                      required=True,
                                      choices=level_options
                                    ),
                                    create_option(
                                      name="4階段",
                                      description="輸入4階段可提前週目數",
                                      option_type=4,
                                      required=True,
                                      choices=level_options
                                    ),
                                    create_option(
                                      name="5階段",
                                      description="輸入5階段可提前週目數",
                                      option_type=4,
                                      required=True,
                                      choices=level_options
                                    )
                                  ],
                                  connector={"1階段": "level1","2階段": "level2","3階段": "level3","4階段": "level4","5階段": "level5"}
                                )
async def set_weeks_offset(ctx, level1, level2, level3, level4, level5):
  connection = await Module.DB_control.OpenConnection(ctx)
  if connection:
    row = await Module.Authentication.IsCaptain(ctx, "/captain set_weeks_offset", connection, ctx.guild.id, ctx.author.id)
    if row:
      group_serial = row[0]
      # 寫入資料庫
      cursor = connection.cursor(prepared=True)
      sql = "UPDATE princess_connect.group SET week_offset_1 = ?, week_offset_2 = ?,week_offset_3 = ?,week_offset_4 = ?,week_offset_5 = ? WHERE server_id = ? and group_serial = ? "
      data = (level1, level2, level3, level4, level5, ctx.guild.id, group_serial)
      cursor.execute(sql, data)
      cursor.close
      connection.commit()
      await ctx.send(f"第{group_serial}戰隊提前週目設置如下\n第1階段:提前{level1}週目\n第2階段:提前{level2}週目\n第3階段:提前{level3}週目\n第4階段:提前{level4}週目\n第5階段:提前{level5}週目")
      # 動態調整週目
      Module.Offset_manager.AutoOffset(connection, ctx.guild.id, group_serial)
      await Module.Update.Update(ctx, ctx.guild.id, group_serial)

    await Module.DB_control.CloseConnection(connection, ctx)