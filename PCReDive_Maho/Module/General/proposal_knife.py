import Module.Kernel.DB_control
import Module.Kernel.check_boss
import Module.Kernel.check_week
import Module.Kernel.Update

async def proposal_knife(send_obj, server_id, sign_channel_id, member_id, week, boss, comment):
  # check頻道，並找出所屬組別
  connection = await Module.Kernel.DB_control.OpenConnection(send_obj)
  if connection:
    cursor = connection.cursor(prepared=True)
    sql = "SELECT now_week, now_week_1, now_week_2, now_week_3, now_week_4, now_week_5, week_offset, group_serial FROM princess_connect.group WHERE server_id = ? and sign_channel_id = ? order by group_serial limit 0, 1"
    data = (server_id, sign_channel_id)
    cursor.execute(sql, data) # 認證身分
    row = cursor.fetchone()
    cursor.close
    if row:
      group_serial = row[7]
      if Module.Kernel.check_week.Check_week((row[0], row[6]), week):
        if Module.Kernel.check_boss.Check_boss((row[1], row[2], row[3], row[4], row[5]), week, boss):
          # 新增刀
          cursor = connection.cursor(prepared=True)
          # TODO 如果comment可以轉回純數值，考慮寫入estimated_damage，顯示於刀表?
          sql = "INSERT INTO princess_connect.knifes (server_id, group_serial, week, boss, member_id, comment) VALUES (?, ?, ?, ?, ?, ?)"
          data = (server_id, group_serial, week, boss, member_id, comment)
          cursor.execute(sql, data)
          cursor.close
          connection.commit()
          await send_obj.send('第' + str(week) + '週目' + str(boss) + '王，備註:' + comment + '，報刀成功!')
          await Module.Kernel.Update.Update(send_obj, server_id, group_serial) # 更新刀表
        else:
          await send_obj.send('該王不存在喔!')
      else:
        await send_obj.send('該週目不存在喔!')
    else:
      await send_obj.send('這裡不是報刀頻道喔!')
    await Module.Kernel.DB_control.CloseConnection(connection, send_obj)
