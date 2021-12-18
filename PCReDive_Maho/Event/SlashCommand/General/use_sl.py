import datetime
import Discord_client
import Module.info_update
import Module.get_closest_end_time

@Discord_client.slash.slash( 
             name="sl" ,
             description="使用SL",
             )
async def use_sl(ctx):
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

      # 檢查使否屬於該戰隊
      cursor = connection.cursor(prepared=True)
      sql = "select last_sl_time from princess_connect.members WHERE server_id = ? and group_serial = ? and member_id = ? limit 0,1"
      data = (ctx.guild.id, group_serial, ctx.author.id)
      cursor.execute(sql, data)
      row = cursor.fetchone()
      if row:
        # 修改SL時間
        closest_end_time = Module.get_closest_end_time.get_closest_day_end(datetime.datetime.now())
        if row[0] < closest_end_time:
          cursor = connection.cursor(prepared=True)
          sql = "update princess_connect.members SET last_sl_time=? WHERE server_id = ? and group_serial = ? and member_id = ?"
          data = (closest_end_time, ctx.guild.id, group_serial, ctx.author.id)
          cursor.execute(sql, data)
          connection.commit()
          await ctx.send('紀錄完成!')
          await Module.info_update.info_update(ctx ,ctx.guild.id, group_serial)
        else:
          await ctx.send('注意，今日已使用過SL，請勿退出遊戲!')
      else:
        await ctx.send('您不屬於第' + str(group_serial) + '戰隊喔!')
    else:
      await ctx.send('這裡不是報刀頻道喔，請在所屬戰隊報刀頻道使用!')
    await Module.DB_control.CloseConnection(connection, ctx)
  