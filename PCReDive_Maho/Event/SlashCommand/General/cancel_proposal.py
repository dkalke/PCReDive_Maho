from discord_slash.utils.manage_commands import create_option, create_choice
import Discord_client
import Module.DB_control
import Module.check_boss
import Module.check_week

@Discord_client.slash.slash( 
             name="cp" ,
             description="取消預約",
             options= [
                 create_option(
                     name="週目",
                     description="填入要取消的週目",
                     option_type=4,
                     required=True
                 ),
                 create_option(
                     name="boss",
                     description="填入要取消的王",
                     option_type=4,
                     required=True,
                     choices=[
                         create_choice(name="1", value=1),create_choice(name="2", value=2),create_choice(name="3", value=3),
                         create_choice(name="4", value=4),create_choice(name="5", value=5)
                     ]
                 ),
                 create_option(
                     name="序列",
                     description="填入在刀表上要取消的序列",
                     option_type=4,
                     required=True
                 )
             ],
             connector={"週目": "week","boss": "boss","序列": "index"}
             )
async def cancelBoss(ctx, week, boss, index):
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
        if Module.check_boss.Check_boss((row[0], row[1], row[2]), week,boss):
          # 尋找要刪除刀的序號
          delete_index = 0 # 這個好像沒用到？
          cursor = connection.cursor(prepared=True)
          sql = "SELECT serial_number,member_id from princess_connect.knifes where server_id=? and group_serial=? and week=? and boss=? order by serial_number limit ?,1"
          data = (ctx.guild.id, group_serial, week, boss,index-1)
          cursor.execute(sql, data)
          row = cursor.fetchone()
          cursor.close()
          if row:
            if ctx.author.id == row[1]:
              cursor = connection.cursor(prepared=True)
              sql = "DELETE from princess_connect.knifes where serial_number=?"
              data = (row[0],)
              row = cursor.execute(sql, data)
              cursor.close()
              connection.commit()
              await ctx.send('取消成功!')
              await Module.Update.Update(ctx, ctx.guild.id, group_serial) # 更新刀表
            else:
              await ctx.send('您並非該刀主人喔!')
          else:
            await ctx.send('該刀不存在喔!')
        else:
          await ctx.send('該王不存在喔!')
      else:
        await ctx.send('該週目不存在喔!')
    else:
      await ctx.send('這裡不是報刀頻道喔!')
    await Module.DB_control.CloseConnection(connection, ctx)