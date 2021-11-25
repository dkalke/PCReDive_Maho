from discord_slash.utils.manage_commands import create_option, create_choice
import Discord_client
import Module.DB_control
import Module.Authentication
import Module.check_week
import Module.check_boss
import Module.Update

# !幫報 [周目] [幾王] [註解] [mention]
@Discord_client.slash.subcommand( base="controller", 
                                  name="proposal_knife", 
                                  description="幫成員報刀",
                                  options=[
                                    create_option(
                                      name="週目",
                                      description="要報第幾週?",
                                      option_type=4,
                                      required=True
                                    ),
                                    create_option(
                                      name="boss",
                                      description="目標boss",
                                      option_type=4,
                                      required=True,
                                      choices=[
                                        create_choice(name="1王", value=1),
                                        create_choice(name="2王", value=2),
                                        create_choice(name="3王", value=3),
                                        create_choice(name="4王", value=4),
                                        create_choice(name="5王", value=5),
                                      ]
                                    ),
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
                                    ),
                                    create_option(
                                        name="預估傷害",
                                        description="單位為\'萬\'，預估能打出的傷害",
                                        option_type=4,
                                        required=False
                                    )
                                  ],
                                  connector={"週目":"week" ,"boss": "boss", "備註": "comment", "成員": "member", "預估傷害":"estimated_damage"}
                                )
async def proposal_knife(ctx, week, boss, comment, member, **kwargs):
  # check身分，並找出所屬組別
  connection = await Module.DB_control.OpenConnection(ctx)
  if connection:
    ( main_week, now_week, week_offset, group_serial ) = await Module.Authentication.IsController(ctx ,'/controller proposal_knife', connection, ctx.guild.id)
    if not group_serial == 0: # 如果是是控刀手
      if Module.check_week.Check_week((main_week, week_offset), week):
        if Module.check_boss.Check_boss(now_week, week, boss):
          try:
            estimated_damage = kwargs["estimated_damage"]
          except KeyError as e:
            estimated_damage = 0
          if not (Module.week_stage.week_stage(week) == 4 and estimated_damage == 0):
            # 新增進刀表
            cursor = connection.cursor(prepared=True)
            sql = "INSERT INTO princess_connect.knifes (server_id, group_serial, week, boss, member_id, comment, estimated_damage) VALUES (?, ?, ?, ?, ?, ?, ?)"
            data = (ctx.guild.id, group_serial, week, boss, member.id, comment, estimated_damage )
            cursor.execute(sql, data)
            cursor.close
            connection.commit()
            await ctx.send('幫報完成! 第' + str(week) + '週目' + str(boss) + '王，備註:' + comment + '。')
            await Module.Update.Update(ctx, ctx.guild.id, group_serial) # 更新刀表
          else:
            await ctx.send('發生錯誤，五階段報刀請填寫可選參數[預估傷害]，單位為萬!')
        else:
          await ctx.send('該王不存在喔!')
      else:
        await ctx.send('該週目不存在喔!')

    await Module.DB_control.CloseConnection(connection, ctx)