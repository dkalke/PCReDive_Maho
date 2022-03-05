import datetime
import Module.Kernel.Discord_client
from discord_slash.utils.manage_commands import create_option
import Module.Kernel.DB_control
import Module.Kernel.Authentication

@Module.Kernel.Discord_client.slash.subcommand( base="admin",
                                  name="create_group" ,
                                  description="新增一個戰隊。",
                                  options=[
                                    create_option(
                                      name="戰隊編號",
                                      description="輸入想要的戰隊編號。",
                                      option_type=4,
                                      required=True
                                    )
                                  ],
                                  connector={"戰隊編號": "group_serial"}
                                )
async def create_group(ctx, group_serial):
  if group_serial > 0:
    if await Module.Authentication.IsAdmin(ctx , '/create_group'):
      connection = await Module.DB_control.OpenConnection(ctx)
      if connection:
        # 尋找戰隊有無存在
        row = Module.Authentication.IsExistGroup(ctx,connection, ctx.guild.id, group_serial)
                
        # 查無該戰隊資料，新增一筆，預設1週目1王，除當前週目外，可往後預約4週目
        if not row: 
          cursor = connection.cursor(prepared=True)
          sql = "INSERT INTO princess_connect.group (server_id, group_serial, now_boss, now_week, now_week_1, now_week_2, now_week_3, now_week_4, now_week_5 ,week_offset, week_offset_1, week_offset_2, week_offset_3, week_offset_4, week_offset_5, boss_change) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)"
          data = (ctx.guild.id, group_serial, 1, 1, 1, 1, 1, 1, 1, 4, 4, 4, 4, 4, 4, datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")) #
          cursor.execute(sql, data)
          cursor.close
          connection.commit() # 資料庫存檔
          await ctx.send('已新增第' + str(group_serial) + '戰隊!')
        else:
          await ctx.send('第' + str(group_serial) + '戰隊已存在!')
        await Module.Kernel.DB_control.CloseConnection(connection, ctx)
  else:
    await ctx.send('戰隊編號只能是正整數。')