import datetime
import Discord_client
import Module.DB_control
import Module.Update
import Name_manager
import Module.Offset_manager

#!取消保留刀 [第幾刀]
@Discord_client.slash.slash( 
             name="n" ,
             description="王死拉，下面一位!",
             )
async def next_boss(ctx):
  # check頻道，並找出所屬組別
  connection = await Module.DB_control.OpenConnection(ctx)
  if connection:
    cursor = connection.cursor(prepared=True)
    sql = "SELECT now_week, now_boss, boss_change, group_serial FROM princess_connect.group WHERE server_id = ? and sign_channel_id = ? order by group_serial limit 0, 1"
    data = (ctx.guild.id, ctx.channel.id)
    cursor.execute(sql, data) # 認證身分
    row = cursor.fetchone()
    cursor.close()
    if row:
      # CD檢查
      group_serial = row[3]
      boss_change = row[2]
      # UTC+0   UTC+8   =>   UTC+8
      if ( ctx.created_at + datetime.timedelta(hours = 8) - boss_change ).seconds >= 30: 
        now_week = row[0]
        now_boss = row[1]
        # 更新週目/boss
        if now_boss == 5:
          now_week = now_week + 1
          now_boss = 1
        else:
          now_boss = now_boss + 1

        # 更新資料表
        cursor = connection.cursor(prepared=True)
        sql = "UPDATE princess_connect.group SET now_week=?, now_boss=?, boss_change=? WHERE server_id = ? and sign_channel_id = ?"
        data = (now_week, now_boss, (ctx.created_at + datetime.timedelta(hours = 8)).strftime("%Y-%m-%d %H:%M:%S"), ctx.guild.id, ctx.channel.id)
        cursor.execute(sql, data)
        cursor.close
        connection.commit()


        #tag成員
        knifes = ''
        cursor = connection.cursor(prepared=True)
        sql = "SELECT member_id FROM princess_connect.knifes WHERE server_id = ? and group_serial = ? and week=? and boss=?"
        data = (ctx.guild.id, group_serial, now_week ,now_boss)
        cursor.execute(sql, data)
        row = cursor.fetchone()
        while row:
          mention = await Name_manager.get_mention(ctx, row[0])
          knifes = knifes + mention  + ' '
          row = cursor.fetchone()
        cursor.close()

        if knifes == '':
          await ctx.send('目前' + str(now_week) + '週' + str(now_boss) + '王沒人報刀喔，看在真步的面子上，快來報刀!')
        else:
          await ctx.send(knifes + str(now_week) + '週' + str(now_boss) + '王到囉!')


        # 更新刀表
        if now_boss == 1:
          Module.Offset_manager.AutoOffset(connection, ctx.guild.id, group_serial) # 自動周目控制
        await Module.Update.Update(ctx, ctx.guild.id, group_serial) # 更新刀表
      else:
        await ctx.send('目前CD中，上次使用時間:' + str(boss_change) + '。' )
    else:
      await ctx.send('這裡不是報刀頻道喔!')

    await Module.DB_control.CloseConnection(connection, ctx)