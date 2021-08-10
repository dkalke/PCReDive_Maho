from discord_slash.utils.manage_commands import create_option
import Discord_client
import Module.DB_control
import Module.Authentication
import Module.info_update

@Discord_client.slash.subcommand( base="captain",
                                  name="set_member_knifes" ,
                                  description="設定成員刀數(一人持有在戰隊內持有多個遊戲帳號時使用)",
                                  options=[
                                    create_option(
                                      name="成員",
                                      description="mention要設定的成員",
                                      option_type=6,
                                      required=True,
                                    ),
                                    create_option(
                                      name="刀數",
                                      description="該成員可以出幾刀，請輸入3的倍數",
                                      option_type=4,
                                      required=True,
                                    )
                                  ],
                                  connector={"成員": "member","刀數": "knifes"}
                                )
async def set_member_knifes(ctx, member, knifes):
  if knifes % 3 == 0 and knifes / 3 > 0:
    connection = await Module.DB_control.OpenConnection(ctx)
    if connection:
      server_id = ctx.guild.id
      row = await Module.Authentication.IsCaptain(ctx ,'/captain set_member_knifes', connection, server_id, ctx.author.id)
      if row:
        group_serial = row[0]
        # 更新指定成員刀數
        # 檢查成員有無存在
        cursor = connection.cursor(prepared=True)
        sql = "select * from princess_connect.members WHERE server_id = ? and group_serial = ? and member_id = ? limit 0,1"
        data = (server_id, group_serial, member.id)
        cursor.execute(sql, data)
        row = cursor.fetchone()
        if row:
          cursor = connection.cursor(prepared=True)
          sql = "update princess_connect.members SET knifes=? WHERE server_id = ? and group_serial = ? and member_id = ?"
          data = (knifes, server_id, group_serial, member.id)
          cursor.execute(sql, data)
          connection.commit()
          await ctx.send('設定完成，該成員目前持有' + str(knifes) + '刀額度!')
          await Module.info_update.info_update(ctx, server_id, group_serial)
        else:
          await ctx.send('該成員不在第' + str(group_serial) + '戰隊中!')
     
      await Module.DB_control.CloseConnection(connection, ctx)
  else:
    await ctx.send('刀數有誤，至少為3且必須為3的倍數!')