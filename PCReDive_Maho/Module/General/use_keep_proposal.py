import datetime

import Module.Kernel.DB_control
import Module.Kernel.check_week
import Module.Kernel.check_boss
import Module.Kernel.Update


async def use_keep_proposal(send_obj, server_id, sign_channel_id, member_id, index, week, boss):        
  if index > 0:
    connection = await Module.Kernel.DB_control.OpenConnection(send_obj)
    if connection:
      cursor = connection.cursor(prepared=True)
      sql = "SELECT  now_week, now_week_1, now_week_2, now_week_3, now_week_4, now_week_5, week_offset, group_serial FROM princess_connect.group WHERE server_id = ? and sign_channel_id = ? order by group_serial limit 0, 1"
      data = (server_id, sign_channel_id)
      cursor.execute(sql, data) # 認證身分
      row = cursor.fetchone()
      cursor.close
      if row:
        group_serial = row[7]
        if Module.Kernel.check_week.Check_week((row[0], row[6]), week):
          if Module.Kernel.check_boss.Check_boss((row[1], row[2], row[3], row[4], row[5]),week, boss):  
            # 尋找指定刀資訊
            cursor = connection.cursor(prepared=True)
            sql = "SELECT serial_number, member_id, comment from princess_connect.keep_knifes where server_id=? and group_serial=? order by serial_number limit ?,1"
            data = (server_id, group_serial, index-1)
            cursor.execute(sql, data)
            row = cursor.fetchone()
            cursor.close()
            if row:
              if member_id == row[1]:
                # 新增刀
                cursor = connection.cursor(prepared=True)
                sql = "INSERT INTO princess_connect.knifes (server_id, group_serial, week, boss, member_id, comment, timestamp) VALUES (?, ?, ?, ?, ?, ?, ?)"
                data = (server_id, group_serial, week, boss, row[1], row[2] ,datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
                cursor.execute(sql, data)
                cursor.close

                # 刪除刀
                cursor = connection.cursor(prepared=True)
                sql = "DELETE from princess_connect.keep_knifes where serial_number=?"
                data = (row[0],)
                cursor.execute(sql, data)
                cursor.close()

                connection.commit()
                await send_obj.send('第' + str(week) + '週目' + str(boss) + '王，備註:' + row[2] + '，報刀成功!')
                await Module.Kernel.Update.Update(send_obj, server_id, group_serial) # 更新刀表
              else:
                await send_obj.send('您並非該刀主人喔!')
            else:
              await send_obj.send('該刀不存在喔!')   
          else:
            await send_obj.send('該王不存在喔!')
        else:
          await send_obj.send('該週目不存在喔!')
      else:
        pass #非指定頻道 不反應
      await Module.Kernel.DB_control.CloseConnection(connection, send_obj)
  else:
    await ctx.send('序號必須大於0!')