from discord_slash.utils.manage_commands import create_option, create_choice
import Discord_client
import Module.DB_control
import Module.check_boss
import Module.check_week
import Module.Update

@Discord_client.slash.slash( 
             name="p" ,
             description="預約打王",
             options= [
                 create_option(
                     name="週目",
                     description="填入要預約的週目",
                     option_type=4,
                     required=True
                 ),
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
             connector={"週目": "week","boss": "boss","備註": "comment"}
             )
async def proposal_knife(ctx, week, boss, comment):
  connection = await Module.DB_control.OpenConnection(ctx)
  if connection:
    cursor = connection.cursor(prepared=True)
    sql = "SELECT now_week, now_boss, week_offset, group_serial FROM princess_connect.group WHERE server_id = ? and sign_channel_id = ? order by group_serial limit 0, 1"
    data = (ctx.guild.id, ctx.channel.id)
    cursor.execute(sql, data) # 認證身分
    row = cursor.fetchone()
    cursor.close
    if row:
      group_serial = row[3]
      if Module.check_week.Check_week((row[0], row[1], row[2]), week):
        if Module.check_boss.Check_boss((row[0], row[1], row[2]),week, boss):
          # 新增刀
          cursor = connection.cursor(prepared=True)
          sql = "INSERT INTO princess_connect.knifes (server_id, group_serial, week, boss, member_id, comment) VALUES (?, ?, ?, ?, ?, ?)"
          data = (ctx.guild.id, group_serial, week, boss, ctx.author.id, comment)
          cursor.execute(sql, data)
          cursor.close
          connection.commit()
          await ctx.send('第' + str(week) + '週目' + str(boss) + '王，備註:' + comment + '，報刀成功!')
          await Module.Update.Update(ctx, ctx.guild.id, group_serial) # 更新刀表
        else:
          await ctx.send('該王不存在喔!')
      else:
        await ctx.send('該週目不存在喔!')
    else:
      await ctx.send('這裡不是報刀頻道喔!')
    await Module.DB_control.CloseConnection(connection, ctx)