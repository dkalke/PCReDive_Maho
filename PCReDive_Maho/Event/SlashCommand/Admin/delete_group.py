import datetime
import Discord_client
from discord_slash.utils.manage_commands import create_option
import Module.DB_control
import Module.Authentication

@Discord_client.slash.subcommand( base="admin",
                                  name="delete_group" ,
                                  description="刪除一個戰隊。",
                                  options=[
                                    create_option(  
                                      name="戰隊編號",
                                      description="輸入想要刪除的戰隊編號。",
                                      option_type=4,
                                      required=True
                                    )
                                  ],
                                  connector={"戰隊編號": "group_serial"}
                                )
async def delete_group(ctx, group_serial):
  if group_serial > 0:
    if await Module.Authentication.IsAdmin(ctx ,'/delete_group'):
      # 尋找戰隊有無存在
      connection = await Module.DB_control.OpenConnection(ctx)
      if connection:
        row = Module.Authentication.IsExistGroup(ctx ,connection, ctx.guild.id, group_serial)
        if row: # 找到該戰隊資料，刪除之! (設有外鍵關聯，其餘相關資料將一併並刪除)
          # 刪除戰隊
          cursor = connection.cursor(prepared=True)
          sql = "DELETE FROM princess_connect.group WHERE server_id = ? and group_serial = ?"
          data = (ctx.guild.id, group_serial)
          cursor.execute(sql, data) 
          cursor.close
          connection.commit() # 資料庫存檔
          await ctx.send('已刪除第' + str(group_serial) + '戰隊!')
        else: 
          await ctx.send('第' + str(group_serial) + '戰隊不存在!')

        await Module.DB_control.CloseConnection(connection, ctx)
  else:
    await ctx.send('[編號] 只能是正整數!')