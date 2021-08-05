from discord_slash.utils.manage_commands import create_option, create_choice
import Discord_client
import Module.DB_control
import Module.Authentication
import Module.Offset_manager
import Module.Update


# !設定 [週目] [幾王]
@Discord_client.slash.subcommand( base="controller", 
                                  name="set_progress", 
                                  description="強制切換至指定週目與boss",
                                  options=[
                                    create_option(
                                      name="週目",
                                      description="第幾週?",
                                      option_type=4,
                                      required=True
                                    ),
                                    create_option(
                                      name="boss",
                                      description="哪隻boss?",
                                      option_type=4,
                                      required=True,
                                      choices=[
                                        create_choice(name="1王", value=1),
                                        create_choice(name="2王", value=2),
                                        create_choice(name="3王", value=3),
                                        create_choice(name="4王", value=4),
                                        create_choice(name="5王", value=5),
                                      ]
                                    )
                                  ],
                                  connector={"週目":"week" ,"boss": "boss"}
                                )
async def set_progress(ctx, week, boss):
  # check身分，並找出所屬組別
  connection = await Module.DB_control.OpenConnection(ctx)
  if connection:
    ( now_week, now_boss, week_offset, group_serial ) = await Module.Authentication.IsController(ctx ,'/controller set_progress', connection, ctx.guild.id)
    if not group_serial == 0: # 如果是是控刀手
      if week > 0:
        cursor = connection.cursor(prepared=True)
        sql = "UPDATE princess_connect.group SET now_week=?, now_boss=? WHERE server_id = ? and group_serial=? order by group_serial"
        data = (week, boss, ctx.guild.id, group_serial)
        cursor.execute(sql, data)
        cursor.close
        connection.commit()
        await ctx.send('已切換至' + str(week) + '週目' + str(boss) + '王!')
        Module.Offset_manager.AutoOffset(connection, ctx.guild.id, group_serial)
        await Module.Update.Update(ctx, ctx.guild.id, group_serial) # 更新刀表
      else:
        await ctx.send('週目必須要大於0!')

    await Module.DB_control.CloseConnection(connection, ctx)