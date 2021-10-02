from discord_slash.utils.manage_commands import create_option, create_choice
import Discord_client
import Module.DB_control
import Module.check_boss
import Module.check_week

@Discord_client.slash.slash( 
             name="ukp" ,
             description="使用保留刀",
             options= [
                create_option(
                     name="序號",
                     description="請查看保留區，填入該刀在保留區中的序號",
                     option_type=4,
                     required=True
                 ),
                 create_option(
                     name="週目",
                     description="要用在哪一週目?",
                     option_type=4,
                     required=True
                 ),
                 create_option(
                     name="boss",
                     description="要打哪一隻王?",
                     option_type=4,
                     required=True,
                     choices=[
                         create_choice(name="1", value=1),create_choice(name="2", value=2),create_choice(name="3", value=3),
                         create_choice(name="4", value=4),create_choice(name="5", value=5)
                     ]
                 )
             ],
             connector={"序號": "index", "週目": "week", "boss": "boss"}
             )
async def use_keep_proposal(ctx, index, week, boss):
  connection = await Module.DB_control.OpenConnection(ctx)
  if connection:
    cursor = connection.cursor(prepared=True)
    sql = "SELECT  now_week, now_week_1, now_week_2, now_week_3, now_week_4, now_week_5, week_offset, group_serial FROM princess_connect.group WHERE server_id = ? and sign_channel_id = ? order by group_serial limit 0, 1"
    data = (ctx.guild.id, ctx.channel.id)
    cursor.execute(sql, data) # 認證身分
    row = cursor.fetchone()
    cursor.close
    if row:
      group_serial = row[7]
      if Module.check_week.Check_week((row[0], row[6]), week):
        if Module.check_boss.Check_boss((row[1], row[2], row[3], row[4], row[5]), week, boss):  
          if index > 0:
            cursor = connection.cursor(prepared=True)
            sql = "SELECT serial_number, member_id, comment from princess_connect.keep_knifes where server_id=? and group_serial=? order by boss limit ?,1"
            data = (ctx.guild.id, group_serial, index-1)
            cursor.execute(sql, data)
            row = cursor.fetchone()
            cursor.close()
            if row:
              if ctx.author.id == row[1]:
                # 新增刀
                cursor = connection.cursor(prepared=True)
                sql = "INSERT INTO princess_connect.knifes (server_id, group_serial, week, boss, member_id, comment) VALUES (?, ?, ?, ?, ?, ?)"
                data = (ctx.guild.id, group_serial, week, boss, row[1], row[2])
                cursor.execute(sql, data)
                cursor.close

                # 刪除刀
                cursor = connection.cursor(prepared=True)
                sql = "DELETE from princess_connect.keep_knifes where serial_number=?"
                data = (row[0],)
                cursor.execute(sql, data)
                cursor.close()

                connection.commit()
                await ctx.channel.send('第' + str(week) + '週目' + str(boss) + '王，備註:' + row[2] + '，報刀成功!')
                await Module.Update.Update(ctx, ctx.guild.id, group_serial) # 更新刀表
              else:
                await ctx.channel.send('您並非該刀主人喔!')
            else:
              await ctx.channel.send('該刀不存在喔!')
          else:
            await ctx.send('序號必須大於0!')
        else:
          await ctx.channel.send('該王不存在喔!')
      else:
        await ctx.channel.send('該週目不存在喔!')
    else:
      await ctx.send('這裡不是報刀頻道喔!')
    await Module.DB_control.CloseConnection(connection, ctx)