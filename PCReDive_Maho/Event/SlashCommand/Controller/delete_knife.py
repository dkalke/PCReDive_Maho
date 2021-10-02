from discord_slash.utils.manage_commands import create_option, create_choice
import Discord_client
import Module.DB_control
import Module.Authentication
import Module.check_week
import Module.check_boss
import Module.Update

# !刪除 [週目] [幾王] [第幾刀]
@Discord_client.slash.subcommand( base="controller", 
                                  name="delete_knife", 
                                  description="強制刪除刀表上的某一刀",
                                  options=[
                                    create_option(
                                      name="週目",
                                      description="目標週目",
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
                                      name="序號",
                                      description="該週目boss刀表上的第幾刀",
                                      option_type=4,
                                      required=True
                                    )
                                  ],
                                  connector={"週目": "week", "boss": "boss", "序號": "knife"}
                                )
async def delete_knife(ctx, week, boss, knife):
  # check身分，並找出所屬組別
  connection = await Module.DB_control.OpenConnection(ctx)
  if connection:
    ( main_week, now_week, week_offset, group_serial ) = await Module.Authentication.IsController(ctx ,'/controller delete_knife', connection, ctx.guild.id)
    if not group_serial == 0: # 如果是是控刀手
      if Module.check_week.Check_week((main_week, week_offset), week):
        if Module.check_boss.Check_boss(now_week, week,boss):
          # 尋找要刪除刀的序號
          cursor = connection.cursor(prepared=True)
          sql = "SELECT serial_number,server_id, group_serial, boss, member_id, comment from princess_connect.knifes where server_id=? and group_serial=? and week=? and boss=? order by serial_number limit ?,1"
          data = (ctx.guild.id, group_serial, week, boss, knife-1)
          cursor.execute(sql, data)
          row = cursor.fetchone()
          cursor.close()
          if row:
            # 刪除刀表
            cursor = connection.cursor(prepared=True)
            sql = "DELETE from princess_connect.knifes where serial_number=?"
            data = (row[0],)
            cursor.execute(sql, data)
            cursor.close()
            connection.commit()
            await ctx.send('刪除成功!')
            await Module.Update.Update(ctx, ctx.guild.id, group_serial) # 更新刀表
          else:
            await ctx.send('該刀不存在喔!')
        else:
          await ctx.send('該王不存在喔!')
      else:
        await ctx.send('該週目不存在喔!')

    await Module.DB_control.CloseConnection(connection, ctx)