from discord_slash.utils.manage_commands import create_option, create_choice
import Module.Kernel.Discord_client
import Module.Kernel.DB_control
import Module.Kernel.Authentication
import Module.Kernel.Offset_manager
import Module.Kernel.Update


# !設定 [週目] [幾王]
@Module.Kernel.Discord_client.slash.subcommand( base="controller", 
                                  name="set_progress", 
                                  description="強制切換至指定boss的週目",
                                  options=[
                                    create_option(
                                      name="1王週目",
                                      description="1王要設定成第幾週?",
                                      option_type=4,
                                      required=True
                                    ),
                                    create_option(
                                      name="2王週目",
                                      description="2王要設定成第幾週?",
                                      option_type=4,
                                      required=True
                                    ),
                                    create_option(
                                      name="3王週目",
                                      description="3王要設定成第幾週?",
                                      option_type=4,
                                      required=True
                                    ),
                                    create_option(
                                      name="4王週目",
                                      description="4王要設定成第幾週?",
                                      option_type=4,
                                      required=True
                                    ),
                                    create_option(
                                      name="5王週目",
                                      description="5王要設定成第幾週?",
                                      option_type=4,
                                      required=True
                                    ),
                                  ],
                                  connector={"1王週目":"week1", "2王週目":"week2", "3王週目":"week3", "4王週目":"week4", "5王週目":"week5"}
                                )
async def set_progress(ctx, week1, week2, week3, week4, week5):
  # check身分，並找出所屬組別
  connection = await Module.Kernel.DB_control.OpenConnection(ctx)
  if connection:
    ( main_week, now_week, week_offset, group_serial ) = await Module.Kernel.Authentication.IsController(ctx ,'/controller set_progress', connection, ctx.guild.id)
    if not group_serial == 0: # 如果是是控刀手
      if week1 > 0 and week2 > 0 and week3 > 0 and week4 > 0 and week5 > 0:
        cursor = connection.cursor(prepared=True)
        sql = ""
        sql = "UPDATE princess_connect.group SET now_week=?, now_week_1=?, now_week_2=?, now_week_3=?, now_week_4=?, now_week_5=? WHERE server_id = ? and group_serial=? order by group_serial"
        
        data = (min(week1, week2, week3, week4, week5), week1, week2, week3, week4, week5, ctx.guild.id, group_serial)
        cursor.execute(sql, data)
        cursor.close
        connection.commit()
        await ctx.send('週目已切換，詳細資訊如下:\n' + 
                       '1王:**'+ str(week1) + '**週目!\n' + 
                       '2王:**'+ str(week2) + '**週目!\n' + 
                       '3王:**'+ str(week3) + '**週目!\n' + 
                       '4王:**'+ str(week4) + '**週目!\n' + 
                       '5王:**'+ str(week5) + '**週目!\n')
        Module.Kernel.Offset_manager.AutoOffset(connection, ctx.guild.id, group_serial)
        await Module.Kernel.Update.Update(ctx, ctx.guild.id, group_serial) # 更新刀表
      else:
        await ctx.send('週目必須要大於0!')

    await Module.Kernel.DB_control.CloseConnection(connection, ctx)