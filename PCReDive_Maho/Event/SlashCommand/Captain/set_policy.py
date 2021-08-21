from discord import Embed
from discord_slash.utils.manage_commands import create_option, create_choice
import Discord_client
import Module.DB_control
import Module.Authentication
import Module.define_value
import Module.Update
import Module.info_update

@Discord_client.slash.subcommand( base="captain",
                                  name="set_policy" ,
                                  description="設定戰隊政策，是否需要回報傷害",
                                  options=[
                                    create_option(
                                      name="政策",
                                      description="選擇政策",
                                      option_type=4,
                                      required=True,
                                      choices=[
                                        create_choice(name="不回報傷害(部分功能無法使用)", value=Module.define_value.Policy.NO.value),
                                        create_choice(name="需回報傷害", value=Module.define_value.Policy.YES.value)
                                      ]
                                    )
                                  ],
                                  connector={"政策": "policy"}
                                )
async def set_table_style(ctx, policy):
  connection = await Module.DB_control.OpenConnection(ctx)
  if connection:
    server_id = ctx.guild.id
    row = await Module.Authentication.IsCaptain(ctx ,'/captain set_policy', connection, server_id, ctx.author.id)
    if row:
      group_serial = int(row[0])
      # 寫入資料庫
      cursor = connection.cursor(prepared=True)
      sql = "UPDATE princess_connect.group SET policy = ? WHERE server_id = ? and group_serial = ? "
      data = (policy, ctx.guild.id, group_serial)
      cursor.execute(sql, data)
      cursor.close
      connection.commit()
      if policy == 0:
        await ctx.send('第' + str(group_serial) + '戰隊政策已設定為**不回報傷害**!')
      else:
        await ctx.send('第' + str(group_serial) + '戰隊政策已設定為**強制回報傷害**!')
      await Module.Update.Update(ctx, ctx.guild.id, group_serial)
      await Module.info_update.info_update(ctx, ctx.guild.id, group_serial)   
      
    await Module.DB_control.CloseConnection(connection, ctx)
