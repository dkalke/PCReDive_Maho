from discord_slash.utils.manage_commands import create_option, create_choice
import Discord_client
import Module.DB_control
import Module.Authentication
import Module.Offset_manager
import Module.Update


# !設定 [週目] [幾王]
@Discord_client.slash.subcommand( base="controller", 
                                  name="set_progress", 
                                  description="強制切換至指定boss的週目",
                                  options=[
                                    create_option(
                                      name="boss",
                                      description="哪隻boss?",
                                      option_type=4,
                                      required=True,
                                      choices=[
                                        create_choice(name="1", value=1),
                                        create_choice(name="2", value=2),
                                        create_choice(name="3", value=3),
                                        create_choice(name="4", value=4),
                                        create_choice(name="5", value=5),
                                      ]
                                    ),
                                    create_option(
                                      name="週目",
                                      description="第幾週?",
                                      option_type=4,
                                      required=True
                                    )
                                  ],
                                  connector={"boss": "boss", "週目":"week"}
                                )
async def set_progress(ctx, boss, week):
  # check身分，並找出所屬組別
  connection = await Module.DB_control.OpenConnection(ctx)
  if connection:
    ( main_week, now_week, week_offset, group_serial ) = await Module.Authentication.IsController(ctx ,'/controller set_progress', connection, ctx.guild.id)
    if not group_serial == 0: # 如果是是控刀手
      if week > 0:
        cursor = connection.cursor(prepared=True)
        sql = ""
        now_week[boss-1] = week
        main_week = min(now_week)
        if boss == 1:
          sql = "UPDATE princess_connect.group SET now_week=?, now_week_1=? WHERE server_id = ? and group_serial=? order by group_serial"
        elif boss == 2:
          sql = "UPDATE princess_connect.group SET now_week=?, now_week_2=? WHERE server_id = ? and group_serial=? order by group_serial"
        elif boss == 3:
          sql = "UPDATE princess_connect.group SET now_week=?, now_week_3=? WHERE server_id = ? and group_serial=? order by group_serial"
        elif boss == 4:
          sql = "UPDATE princess_connect.group SET now_week=?, now_week_4=? WHERE server_id = ? and group_serial=? order by group_serial"
        elif boss == 5:
          sql = "UPDATE princess_connect.group SET now_week=?, now_week_5=? WHERE server_id = ? and group_serial=? order by group_serial"
        data = (main_week, week, ctx.guild.id, group_serial)
        cursor.execute(sql, data)
        cursor.close
        connection.commit()
        await ctx.send('已切換' + str(boss) + '王至'+ str(week) + '週目!')
        Module.Offset_manager.AutoOffset(connection, ctx.guild.id, group_serial)
        await Module.Update.Update(ctx, ctx.guild.id, group_serial) # 更新刀表
      else:
        await ctx.send('週目必須要大於0!')

    await Module.DB_control.CloseConnection(connection, ctx)