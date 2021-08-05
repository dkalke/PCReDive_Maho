from discord_slash.utils.manage_commands import create_option, create_choice
import Discord_client
import Module.DB_control

@Discord_client.slash.slash( 
             name="kp" ,
             description="報保留刀",
             options= [
                 create_option(
                     name="boss",
                     description="填入要打的王",
                     option_type=4,
                     required=True,
                     choices=[
                         create_choice(name="1", value=1),create_choice(name="2", value=2),create_choice(name="3", value=3),
                         create_choice(name="4", value=4),create_choice(name="5", value=5)
                     ]
                 ),
                 create_option(
                     name="備註",
                     description="備註（預計傷害）",
                     option_type=3,
                     required=True
                 )
             ],
             connector={"boss": "boss","備註": "remark"}
             )
async def keepKnife(ctx, boss, remark):
  connection = await Module.DB_control.OpenConnection(ctx)
  if connection:
    cursor = connection.cursor(prepared=True)
    sql = "SELECT group_serial FROM princess_connect.group WHERE server_id = ? and sign_channel_id = ? order by group_serial limit 0, 1"
    data = (ctx.guild.id, ctx.channel.id)
    cursor.execute(sql, data) # 認證身分
    row = cursor.fetchone()
    cursor.close
    if row:
      group_serial = row[0]
      if boss > 0 and boss < 6:
        # 寫入保留刀表
        cursor = connection.cursor(prepared=True)
        sql = "INSERT INTO princess_connect.keep_knifes (server_id, group_serial, member_id, boss, comment) VALUES (?, ?, ?, ?, ?)"
        data = (ctx.guild.id, group_serial, ctx.author.id, boss, remark)
        cursor.execute(sql, data)
        cursor.close()
        connection.commit()
        await ctx.send(str(boss) + '王，備註:' + remark + '，**保留刀**報刀成功!')
        await Module.Update.Update(ctx, ctx.guild.id, group_serial) # 更新刀表
      else:
        await ctx.send('該王不存在喔!')
    else:
      await ctx.send('這裡不是報刀頻道喔!')
    await Module.DB_control.CloseConnection(connection, ctx)