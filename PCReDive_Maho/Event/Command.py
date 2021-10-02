import os
import datetime
import csv
import re
import mysql.connector
from mysql.connector import Error

import discord
from discord import Embed
from Discord_client import client
import Name_manager
import Module.DB_control
import Module.Authentication
import Module.Update
import Module.Offset_manager
import Module.check_week
import Module.check_boss
import Module.full_string_to_half_and_lower


def checktime(number): # 檢查是不是合法的時間
    return (number >= 0 and number <= 130) and \
           ((number // 100 == 0 and number % 100 <= 59 and number % 100 >= 0) or \
           (number // 100 == 1 and number % 100 <= 30 and number % 100 >= 0))

def transform_time(original_time): # 轉換秒數
    result = ""
    if original_time < 60:
        if original_time < 10:
            result += "00" + str(original_time)
        else:
            result += "0" + str(original_time)
    else:
        if 60 <= original_time < 70:
            result += str(original_time // 60) + "0" + str(original_time % 60)
        else:
            result += str(original_time // 60) + str(original_time % 60)
    return result



@client.event
async def on_message(message):
  # 防止機器人自問自答
  if message.author == client.user:
    return

  async def RemindUpdate(connection, server_id):
    cursor = connection.cursor(prepared=True)
    sql = "SELECT upload FROM princess_connect.group WHERE server_id = ? limit 0, 1"
    data = (server_id,)
    cursor.execute(sql, data)
    row = cursor.fetchone()
    cursor.close
    if row:
      if row[0] == 1:
        await message.channel.send('機器人指令有更新囉! 請重新輸入!h以便更新指令表!')
        sql = "UPDATE princess_connect.group SET upload=? WHERE server_id=?"
        data = (0, message.guild.id)
        cursor.execute(sql, data)
        cursor.close
        connection.commit()

    

  # --------------------------------------------------------------------指令部分------------------------------------------------------------------------------------------------------
  try:
    tokens = message.content.split()
    if len(tokens) > 0: # 邊界檢查
      tokens[0] = Module.full_string_to_half_and_lower.full_string_to_half_and_lower(tokens[0])

      if tokens[0][0] == '!': # 檢查有無更新訊息
        connection = await Module.DB_control.OpenConnection(message)
        if connection:
          await RemindUpdate(connection, message.guild.id)

      # --------------------------------------------------------------------分盟管理 僅限管理者使用------------------------------------------------------------------------------------------------------
      # 轉移至斜線指令

      # --------------------------------------------------------------------戰隊管理 僅限戰隊隊長使用------------------------------------------------------------------------------------------------------
      # 轉移至斜線指令
      
      # --------------------------------------------------------------------出刀管理 僅限控刀手使用------------------------------------------------------------------------------------------------------
      # 轉移至斜線指令
      
      # --------------------------------------------------------------------一般成員 僅限報刀頻道使用------------------------------------------------------------------------------------------------------          
      #報刀指令 !預約 [周目] [幾王] [註解]
      if tokens[0] == '!預約' or tokens[0] == '!预约' or tokens[0] == '!p':
        # check頻道，並找出所屬組別
        group_serial = 0
        
        connection = await Module.DB_control.OpenConnection(message)
        if connection:
          cursor = connection.cursor(prepared=True)
          sql = "SELECT now_week, now_week_1, now_week_2, now_week_3, now_week_4, now_week_5, week_offset, group_serial FROM princess_connect.group WHERE server_id = ? and sign_channel_id = ? order by group_serial limit 0, 1"
          data = (message.guild.id, message.channel.id)
          cursor.execute(sql, data) # 認證身分
          row = cursor.fetchone()
          cursor.close
          if row:
            group_serial = row[7]
            if len(tokens) == 4:
              if tokens[1].isdigit() and tokens[2].isdigit() :
                week = int(tokens[1])
                boss = int(tokens[2])
                comment = tokens[3]
                if Module.check_week.Check_week((row[0], row[6]), week):
                  if Module.check_boss.Check_boss((row[1], row[2], row[3], row[4], row[5]),week, boss):
                    # 新增刀
                    cursor = connection.cursor(prepared=True)
                    sql = "INSERT INTO princess_connect.knifes (server_id, group_serial, week, boss, member_id, comment, timestamp) VALUES (?, ?, ?, ?, ?, ?, ?)"
                    data = (message.guild.id, group_serial, week, boss, message.author.id, comment ,datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
                    cursor.execute(sql, data)
                    cursor.close
                    connection.commit()
                    await message.channel.send('第' + str(week) + '週目' + str(boss) + '王，備註:' + comment + '，報刀成功!')
                    await Module.Update.Update(message, message.guild.id, group_serial) # 更新刀表
                  else:
                    await message.channel.send('該王不存在喔!')
                else:
                  await message.channel.send('該週目不存在喔!')
              else:
                await message.channel.send('[週目] [王]請使用阿拉伯數字!')
            else:
              await message.channel.send('!預約 格式錯誤，應為 !預約 [週目] [王] [註解]')
          else:
            pass #非指定頻道 不反應
          await Module.DB_control.CloseConnection(connection, message)


      #!取消報刀  !取消預約 [周目] [幾王] [第幾刀]
      elif tokens[0] == '!取消預約' or tokens[0] == '!取消预约' or tokens[0] == '!cp':
        group_serial = 0
        connection = await Module.DB_control.OpenConnection(message)
        if connection:
          cursor = connection.cursor(prepared=True)
          sql = "SELECT now_week, now_week_1, now_week_2, now_week_3, now_week_4, now_week_5, week_offset, group_serial FROM princess_connect.group WHERE server_id = ? and sign_channel_id = ? order by group_serial limit 0, 1"
          data = (message.guild.id, message.channel.id)
          cursor.execute(sql, data) # 認證身分
          row = cursor.fetchone()
          cursor.close
          if row:
            group_serial = row[7]
            if len(tokens) == 4:
              if tokens[1].isdigit() and tokens[2].isdigit() and tokens[3].isdigit():
                week = int(tokens[1])
                boss = int(tokens[2])
                index = int(tokens[3]) # TODO check index 不可為負數
                if Module.check_week.Check_week((row[0], row[6]), week):
                  if Module.check_boss.Check_boss((row[1], row[2], row[3], row[4], row[5]), week, boss):
                    # 尋找要刪除刀的序號
                    delete_index = 0
                    cursor = connection.cursor(prepared=True)
                    sql = "SELECT serial_number,member_id from princess_connect.knifes where server_id=? and group_serial=? and week=? and boss=? order by serial_number limit ?,1"
                    data = (message.guild.id, group_serial, week, boss,index-1)
                    cursor.execute(sql, data)
                    row = cursor.fetchone()
                    cursor.close()
                    if row:
                      if message.author.id == row[1]:
                        cursor = connection.cursor(prepared=True)
                        sql = "DELETE from princess_connect.knifes where serial_number=?"
                        data = (row[0],)
                        row = cursor.execute(sql, data)
                        cursor.close()
                        connection.commit()
                        await message.channel.send('取消成功!')
                        await Module.Update.Update(message, message.guild.id, group_serial) # 更新刀表
                      else:
                        await message.channel.send('您並非該刀主人喔!')
                    else:
                      await message.channel.send('該刀不存在喔!')
                  else:
                    await message.channel.send('該王不存在喔!')
                else:
                  await message.channel.send('該週目不存在喔!')
              else:
                await message.channel.send('[週目] [王] [第幾刀]請使用阿拉伯數字!')
            else:
              await message.channel.send('!取消預約 格式錯誤，應為 !取消預約 [週目] [王] [第幾刀]')
          else:
            pass #非指定頻道 不反應
          await Module.DB_control.CloseConnection(connection, message)
        
      
      elif tokens[0] == '!報保留刀' or tokens[0] == '!报保留刀' or tokens[0] == '!kp':
        # check頻道，並找出所屬組別
        group_serial = 0
        connection = await Module.DB_control.OpenConnection(message)
        if connection:
          cursor = connection.cursor(prepared=True)
          sql = "SELECT group_serial FROM princess_connect.group WHERE server_id = ? and sign_channel_id = ? order by group_serial limit 0, 1"
          data = (message.guild.id, message.channel.id)
          cursor.execute(sql, data) # 認證身分
          row = cursor.fetchone()
          cursor.close
          if row:
            group_serial = row[0]
            if len(tokens) == 3:
              if tokens[1].isdigit():
                if int(tokens[1]) > 0 and int(tokens[1]) < 6:
                  # 寫入保留刀表
                  cursor = connection.cursor(prepared=True)
                  sql = "INSERT INTO princess_connect.keep_knifes (server_id, group_serial, member_id, boss, comment) VALUES (?, ?, ?, ?, ?)"
                  data = (message.guild.id, group_serial, message.author.id, int(tokens[1]), tokens[2])
                  cursor.execute(sql, data)
                  cursor.close()
                  connection.commit()
                  await message.channel.send(tokens[1] + '王，備註:' + tokens[2] + '，**保留刀**報刀成功!')
                  await Module.Update.Update(message, message.guild.id, group_serial) # 更新刀表
                else:
                  await message.channel.send('該王不存在喔!')
              else:
                await message.channel.send('[幾王]請使用阿拉伯數字!')
            else:
              await message.channel.send('!報保留刀 格式錯誤，應為 !報保留刀 [王] [註解]')
          else:
            pass #非指定頻道 不反應
          await Module.DB_control.CloseConnection(connection, message)
        
      #!使用保留刀 [第幾刀] [週目] [boss]
      elif tokens[0] == '!使用保留刀' or tokens[0] == '!使用保留刀' or tokens[0] == '!ukp':
        group_serial = 0
        connection = await Module.DB_control.OpenConnection(message)
        if connection:
          cursor = connection.cursor(prepared=True)
          sql = "SELECT  now_week, now_week_1, now_week_2, now_week_3, now_week_4, now_week_5, week_offset, group_serial FROM princess_connect.group WHERE server_id = ? and sign_channel_id = ? order by group_serial limit 0, 1"
          data = (message.guild.id, message.channel.id)
          cursor.execute(sql, data) # 認證身分
          row = cursor.fetchone()
          cursor.close
          if row:
            group_serial = row[7]
            if len(tokens) == 4:
              if tokens[1].isdigit() and tokens[2].isdigit() and tokens[3].isdigit():
                index = int(tokens[1]) # TODO check index 不可為負數
                week = int(tokens[2])
                boss = int(tokens[3])
                if Module.check_week.Check_week((row[0], row[6]), week):
                  if Module.check_boss.Check_boss((row[1], row[2], row[3], row[4], row[5]),week, boss):  
                    cursor = connection.cursor(prepared=True)
                    sql = "SELECT serial_number, member_id, comment from princess_connect.keep_knifes where server_id=? and group_serial=? order by boss limit ?,1"
                    data = (message.guild.id, group_serial, index-1)
                    cursor.execute(sql, data)
                    row = cursor.fetchone()
                    cursor.close()
                    if row:
                      if message.author.id == row[1]:
                        # 新增刀
                        cursor = connection.cursor(prepared=True)
                        sql = "INSERT INTO princess_connect.knifes (server_id, group_serial, week, boss, member_id, comment, timestamp) VALUES (?, ?, ?, ?, ?, ?, ?)"
                        data = (message.guild.id, group_serial, week, boss, row[1], row[2] ,datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
                        cursor.execute(sql, data)
                        cursor.close

                        # 刪除刀
                        cursor = connection.cursor(prepared=True)
                        sql = "DELETE from princess_connect.keep_knifes where serial_number=?"
                        data = (row[0],)
                        cursor.execute(sql, data)
                        cursor.close()

                        connection.commit()
                        await message.channel.send('第' + str(week) + '週目' + str(boss) + '王，備註:' + row[2] + '，報刀成功!')
                        await Module.Update.Update(message, message.guild.id, group_serial) # 更新刀表
                      else:
                        await message.channel.send('您並非該刀主人喔!')
                    else:
                      await message.channel.send('該刀不存在喔!')   
                  else:
                    await message.channel.send('該王不存在喔!')
                else:
                  await message.channel.send('該週目不存在喔!')
              else:
                await message.channel.send('[第幾刀] [週目] [boss]請使用阿拉伯數字!')
            else:
              await message.channel.send('!使用保留刀 格式錯誤，應為 !使用保留刀 [第幾刀] [週目] [boss]')
          else:
            pass #非指定頻道 不反應
          await Module.DB_control.CloseConnection(connection, message)


      #!取消保留刀 [第幾刀]
      elif tokens[0] == '!取消保留刀' or tokens[0] == '!取消保留刀' or tokens[0] == '!ckp':
        group_serial = 0
        connection = await Module.DB_control.OpenConnection(message)
        if connection:
          cursor = connection.cursor(prepared=True)
          sql = "SELECT  now_week, now_boss, week_offset, group_serial FROM princess_connect.group WHERE server_id = ? and sign_channel_id = ? order by group_serial limit 0, 1"
          data = (message.guild.id, message.channel.id)
          cursor.execute(sql, data) # 認證身分
          row = cursor.fetchone()
          cursor.close
          if row:
            group_serial = row[3]
            if len(tokens) == 2:
              if tokens[1].isdigit():
                index = int(tokens[1]) # TODO check index 不可為負數

                # 尋找要刪除刀的序號
                cursor = connection.cursor(prepared=True)
                sql = "SELECT serial_number,member_id from princess_connect.keep_knifes where server_id=? and group_serial=? order by boss limit ?,1"
                data = (message.guild.id, group_serial, index-1)
                cursor.execute(sql, data)
                row = cursor.fetchone()
                cursor.close()
                if row:
                  if message.author.id == row[1]:
                    cursor = connection.cursor(prepared=True)
                    sql = "DELETE from princess_connect.keep_knifes where serial_number=?"
                    data = (row[0],)
                    row = cursor.execute(sql, data)
                    cursor.close()
                    connection.commit()
                    await message.channel.send('取消保留刀成功!')
                    await Module.Update.Update(message, message.guild.id, group_serial) # 更新刀表
                  else:
                    await message.channel.send('您並非該刀主人喔!')
                else:
                  await message.channel.send('該刀不存在喔!')   
              else:
                await message.channel.send('[第幾刀]請使用阿拉伯數字!')
            else:
              await message.channel.send('!取消保留刀 格式錯誤，應為 !取消保留刀 [第幾刀]')
          else:
            pass #非指定頻道 不反應
          await Module.DB_control.CloseConnection(connection, message)

      elif tokens[0] == '!目前進度' or tokens[0] == '!目前进度' or tokens[0] == '!ns':
        if len(tokens) == 1:
          # check頻道，並找出所屬組別
          group_serial = 0
          connection = await Module.DB_control.OpenConnection(message)
          if connection:
            cursor = connection.cursor(prepared=True)
            sql = "SELECT now_week, now_boss, group_serial FROM princess_connect.group WHERE server_id = ? and sign_channel_id = ? order by group_serial limit 0, 1"
            data = (message.guild.id, message.channel.id)
            cursor.execute(sql, data) # 認證身分
            row = cursor.fetchone()
            cursor.close()
            if row:
              await message.channel.send('目前進度' + str(row[0]) + '週' + str(row[1]) + '王!')
            else:
              pass #非指定頻道 不反應

            await Module.DB_control.CloseConnection(connection, message)
        else:
          await message.channel.send('!目前進度 格式錯誤，應為 !目前進度')
      
      elif tokens[0] == '!下面一位' or tokens[0] == '!下面一位' or tokens[0] == '!n':
        if len(tokens) == 2:
          if tokens[1].isdigit():
            boss = int(tokens[1])
            if boss > 0 and boss < 6:
              connection = await Module.DB_control.OpenConnection(message)
              if connection:
                cursor = connection.cursor(prepared=True)
                sql = "SELECT now_week, now_week_1, now_week_2, now_week_3, now_week_4, now_week_5, boss_change_1, boss_change_2, boss_change_3, boss_change_4, boss_change_5, group_serial FROM princess_connect.group WHERE server_id = ? and sign_channel_id = ? order by group_serial limit 0, 1"
                data = (message.guild.id, message.channel.id)
                cursor.execute(sql, data) # 認證身分
                row = cursor.fetchone()
                cursor.close()
                if row:
                  # CD檢查
                  main_week = row[0]
                  now_week=[row[1], row[2], row[3], row[4], row[5]]
                  boss_change = [row[6], row[7], row[8], row[9], row[10]]
                  group_serial = row[11]
      
                  # UTC+0   UTC+8   =>   UTC+8
                  if not now_week[boss-1] >= main_week + 2:
                    if ( message.created_at + datetime.timedelta(hours = 8) - boss_change[boss-1] ).seconds >= 30: 
                      # 更新該王週目
                      now_week[boss-1] = now_week[boss-1]+1
                      cursor = connection.cursor(prepared=True)
                      sql = ""
                      if boss==1:
                        sql = "UPDATE princess_connect.group SET now_week_1=?, boss_change_1=? WHERE server_id = ? and sign_channel_id = ?"
                      elif boss==2:
                        sql = "UPDATE princess_connect.group SET now_week_2=?, boss_change_2=? WHERE server_id = ? and sign_channel_id = ?"
                      elif boss==3:
                        sql = "UPDATE princess_connect.group SET now_week_3=?, boss_change_3=? WHERE server_id = ? and sign_channel_id = ?"
                      elif boss==4:
                        sql = "UPDATE princess_connect.group SET now_week_4=?, boss_change_4=? WHERE server_id = ? and sign_channel_id = ?"
                      elif boss==5:
                        sql = "UPDATE princess_connect.group SET now_week_5=?, boss_change_5=? WHERE server_id = ? and sign_channel_id = ?"
                      data = (now_week[boss-1], (message.created_at + datetime.timedelta(hours = 8)).strftime("%Y-%m-%d %H:%M:%S"), message.guild.id, message.channel.id)
                      cursor.execute(sql, data)
                      cursor.close
                      connection.commit()

                      msg = ["","","","",""]
                      # 檢查main week是否需要更動
                      new_main_week = min(now_week)
                      if new_main_week > main_week:
                        knifes = await Module.show_knifes.show_knifes(connection, message, group_serial, now_week[boss-1] ,boss)
            
                        if knifes == '':
                          msg[boss-1] = '目前' + str(now_week[boss-1]) + '週' + str(boss) + '王沒人報刀喔，看在真步的面子上，快來報刀!\n'
                        else:
                          msg[boss-1] = knifes + str(now_week[boss-1]) + '週' + str(boss) + '王到囉!\n'

                        # 去除當前的boss
                        boss_index=list(range(1,6))
                        boss_index.remove(boss)

                        #如果其他王week位處main_week+2，一併tag上來
                        for index in boss_index:
                          if now_week[index-1] == main_week+2: 
                            knifes = await Module.show_knifes.show_knifes(connection, message, group_serial, now_week[index-1] ,index)

                            if knifes == '':
                              msg[index-1] = '目前' + str(now_week[index-1]) + '週' + str(index) + '王沒人報刀喔，看在真步的面子上，快來報刀!\n'
                            else:
                              msg[index-1] = knifes + str(now_week[index-1]) + '週' + str(index) + '王到囉!\n'
                          else:
                            pass

                        #更新主週目
                        cursor = connection.cursor(prepared=True)
                        sql = "UPDATE princess_connect.group SET now_week=? WHERE server_id = ? and sign_channel_id = ?"
                        data = (new_main_week, message.guild.id, message.channel.id)
                        cursor.execute(sql, data)
                        cursor.close
                        connection.commit()

                        # 自動周目控制
                        Module.Offset_manager.AutoOffset(connection, message.guild.id, group_serial) 
                      else:
                        if now_week[boss-1] < main_week+2: # 檢查週目是否超出可出刀週目
                          knifes = await Module.show_knifes.show_knifes(connection, message, group_serial, now_week[boss-1] ,boss)

                          if knifes == '':
                            msg[boss-1] = '目前' + str(now_week[boss-1]) + '週' + str(boss) + '王沒人報刀喔，看在真步的面子上，快來報刀!'
                          else:
                            msg[boss-1] = knifes + str(now_week[boss-1]) + '週' + str(boss) + '王到囉!'

                        else:
                          msg[boss-1] = str(now_week[boss-1] - 1) +'週' + str(boss) + '王已討伐，等待其他boss中。'

                      await message.channel.send(msg[0]+msg[1]+msg[2]+msg[3]+msg[4])

                      await Module.Update.Update(message, message.guild.id, group_serial) # 更新刀表
                    else:
                      await message.channel.send(str(boss) + '王目前CD中，上次使用時間:' + str(boss_change[boss-1]) + '。' )
                  else:
                    await message.channel.send('當前主週目為' + str(main_week) + '，還打不到' + str(now_week[boss-1]) + '週' + str(boss) + '王喔!')
                else:
                  pass #非指定頻道 不反應

                await Module.DB_control.CloseConnection(connection, message)
            else:
              await message.channel.send('王只能是包含1~5的正整數!')
          else:
            await message.channel.send('請輸入數字!')
        else:
          await message.channel.send('!下面一位 格式錯誤，應為 !下面一位 [boss]')


      # --------------------------------------------------------------------所有頻道，所有人皆可使用------------------------------------------------------------------------------------------------------          
      # 刀表調整器
      # author: YungPingXu
      # source: https://github.com/YungPingXu/pcr-bot/blob/main/code.py
      elif re.match(r"\s*\.tr\s*[\s\S]+", message.content):
        tr = re.match(r"\s*\.tr\s*(\d+)\s*\n([\s\S]+)", message.content)
        if tr:
            time = int(tr.group(1))
            if 1 <= time <= 90:
                lines = tr.group(2).split("\n")
                resultline = ""
                for line in lines:
                    tmp = ""
                    for c in line: # 全形轉半形
                        if c in ("，", "、", "。"):
                            tmp += c
                        elif 65281 <= ord(c) <= 65374:
                            tmp += chr(ord(c) - 65248)
                        elif ord(c) == 12288: # 空格字元
                            tmp += chr(32)
                        else:
                            tmp += c
                    filter = tmp.replace(":", "").replace("\t", "") # 過濾特殊字元
                    match = re.match(r'(\D*)(\d{2,3})((\s*.\s*)(\d{2,3}))?(.*)?', filter) # 擷取時間
                    if match:
                        content1 = match.group(1) # 時間前面的文字
                        timerange = match.group(3) # 056~057 這種有範圍的時間
                        time1 = int(match.group(2)) # 有範圍的時間 其中的第一個時間
                        time2 = 0
                        if timerange is not None and match.group(5) is not None:
                            time2 = int(match.group(5)) # 有範圍的時間 其中的第二個時間
                        rangecontent = match.group(4) # 第一個時間和第二個時間中間的字串
                        content2 = match.group(6) # 時間後面的文字
                        if checktime(time1) and ((timerange is None and match.group(5) is None) or (timerange is not None and match.group(5) is not None and checktime(time2))):
                            totaltime1 = time1 % 100 + (time1 // 100) * 60 # time1的秒數
                            newtime1 = totaltime1 - (90 - time)
                            result = ""
                            if newtime1 < 0: # 如果時間到了 後續的就不要轉換
                                continue # 迴圈跳到下一個
                            if match.group(5) is None:
                                result = content1 + transform_time(newtime1) + content2
                            else:
                                totaltime2 = time2 % 100 + time2 // 100 # time2的秒數
                                newtime2 = totaltime2 - (90 - time)
                                result = content1 + transform_time(newtime1) + rangecontent + transform_time(newtime2) + content2
                            resultline += result
                        else:
                            resultline += tmp
                    else:
                        resultline += tmp
                    resultline += "\n"
                await message.author.send(resultline)
            else:
                await message.author.send("您輸入的補償秒數錯誤，秒數必須要在 1～90 之間！")
        else:
            await message.author.send("您輸入的秒數格式錯誤，正確的格式為\n.tr 補償秒數\n文字軸")
      
      # 幫助訊息
      elif tokens[0] == '!幫助' or tokens[0] == '!帮助' or tokens[0] == '!h':
        msg = '\
**目前版本為0.9.4 版**\n\
\n\
指令支援繁體/簡體/英文，全形半形。\n\
此外，英文縮寫對照表於上方網頁文件中可以查詢。\n\
'
        embed_msg = Embed(title='說明(網頁好讀版請點我)', url='https://hackmd.io/@dkal/SysbG9clO', description=msg, color=0xB37084)
        embed_msg.set_author(name='咕嚕靈波（●′∀‵）ノ♡', url='https://discord.com/api/oauth2/authorize?client_id=806421470368104449&permissions=2048&scope=bot', icon_url='https://i.imgur.com/TtjU27j.jpg')
        embed_msg.add_field(name='第一步', value='請管理員先建立戰隊，並指派隊長。', inline=False)
        embed_msg.add_field(name='第二步', value='請各隊長先以指令設定好刀表、報刀、歷史紀錄，並設定好各頻道的權限，一般成員是以發言頻道做為判斷基準。', inline=False)
        embed_msg.add_field(name='第三步', value='開始使用囉!', inline=False)
        embed_msg.add_field(name='\u200b', value='\u200b', inline=False) # 空行
        msg = '\
請輸入以下指令來查看指令格式:\n\
　 !管理員專用指令\n\
或 !管理员专用指令\n\
或 !admcmd\n\
\n\
　 !戰隊隊長專用指令\n\
或 !战队队长专用指令\n\
或 !pricmd\n\
\n\
　 !控刀手專用指令\n\
或 !控刀手专用指令\n\
或 !concmd\n\
\n\
　 !一般指令\n\
或 !norcmd\n\
'
        embed_msg.add_field(name='指令格式', value=msg, inline=False)
        embed_msg.set_footer(text='當前版本可能會有些許BUG，歡迎反應或許願新功能!')
        await message.channel.send(embed=embed_msg)



      elif tokens[0] == '!管理員專用指令' or tokens[0] == '!管理员专用指令' or tokens[0] == '!admcmd':
        embed_msg = Embed(title='[管理員專用]', color=0xB87181)
        embed_msg.add_field(name='建立戰隊', value='建立戰隊，並將mention的人員全設為戰隊隊長。\n　!建立戰隊 [數字編號] [@隊長1 @隊長2 .....]\n　!建立战队 [數字編號] [@隊長1 @隊長2 .....]\n　!cg [數字編號] [@隊長1 @隊長2 .....]', inline=False)
        embed_msg.add_field(name='刪除戰隊', value='刪除指定戰隊資料，手起刀落，會砍得一乾二淨請謹慎使用。\n　!刪除戰隊 [數字編號]\n　!删除战队 [數字編號]\n　!dg [數字編號]', inline=False)
        embed_msg.add_field(name='戰隊隊長', value='更換指定戰隊隊長，採用內閣改組方式，會整組換掉，如有異動請全部重新mention一次。\n　!戰隊隊長 [數字編號] [@隊長1 @隊長2 .....]\n　!战队队长 [數字編號] [@隊長1 @隊長2 .....]\n　!gc [數字編號] [@隊長1 @隊長2 .....]', inline=False)
        embed_msg.add_field(name='戰隊列表', value='顯示所有戰隊資料。\n　!戰隊列表\n　!战队列表\n　!gl', inline=False)
        await message.channel.send(embed=embed_msg)



      elif tokens[0] == '!戰隊隊長專用指令' or tokens[0] == '!战队队长专用指令' or tokens[0] == '!pricmd':
        embed_msg = Embed(title='[戰隊隊長專用]', color=0xC5848B)
        embed_msg.add_field(name='控刀手身分組', value='把mention身分組設定為控刀手。\n　!控刀手身分組 [身分組]\n　!控刀手身分组 [身分組]\n　!cr [身分組]', inline=False)
        embed_msg.add_field(name='刀表在此', value='指定某一頻道作為顯示刀表的頻道，建議設定不可發言。\n　!刀表在此\n　!刀表在此\n　!tc', inline=False)
        embed_msg.add_field(name='報刀在此', value='指定某一頻道作為報刀的頻道，請用權限控制，僅有戰隊成員可發言。\n　!報刀在此\n　!报刀在此\n　!sc', inline=False)
        embed_msg.add_field(name='提前週目', value='設定可以提前幾個週目預約。\n　!提前週目 [幾週]\n　!提前周目 [幾週]\n　!wo [幾週]', inline=False)
        embed_msg.add_field(name='清除刀表', value='清除刀表，打掉重來。\n　!清除刀表\n　!清除刀表\n　!ct', inline=False)
        embed_msg.add_field(name='刀表樣式', value='切換刀表樣式。 0:Embed, 1:Text。\n　!刀表樣式 [代號]\n　!刀表样式 [代號]\n　!ts [代號]', inline=False)
        embed_msg.add_field(name='匯出刀表', value='傳送完整csv刀表到私人訊息。\n　!匯出刀表\n　!汇出刀表\n　!e', inline=False)
        await message.channel.send(embed=embed_msg)



      elif tokens[0] == '!控刀手專用指令' or tokens[0] == '!控刀手专用指令' or tokens[0] == '!concmd':
        embed_msg = Embed(title='[控刀手專用]', color=0xCFA6AC)
        embed_msg.add_field(name='移動', value='將該刀從[週目][boss][第幾刀]移動至[週目][boss]，簡單來說就是抽換刀序。\n　!移動 [週目] [boss] [哪一刀] [新週目] [新boss]\n　!移动 [週目] [boss] [哪一刀] [新週目] [新boss]\n　!m [週目] [boss] [哪一刀] [新週目] [新boss]', inline=False)
        embed_msg.add_field(name='刪除', value='刪除**刀表**中的某刀。請指明週目、boss與第幾刀。\n　!刪除 [週目] [boss] [第幾刀]\n　!删除 [週目] [boss] [第幾刀]\n　!fd [週目] [boss] [第幾刀]', inline=False)
        embed_msg.add_field(name='幫報', value='幫mention的人報刀至**刀表**。請指明週目、boss、備註與mention對方。\n　!幫報 [週目] [boss] [備註] [@成員]\n　!帮报 [週目] [boss] [備註] [@成員]\n　!hp [週目] [boss] [備註] [@成員]', inline=False)
        embed_msg.add_field(name='幫報保留刀', value='幫mention的人報刀至**保留區**。請指明boss、備註與mention對方。\n　!幫報保留刀 [boss] [備註] [@成員]\n　!帮报保留刀 [boss] [備註] [@成員]\n　!hkp [boss] [備註] [@成員]', inline=False)
        embed_msg.add_field(name='刪除保留刀', value='刪除**保留區**中的某刀。請指明第幾刀。\n　!刪除保留刀 [第幾刀]\n　!!删除保留刀 [第幾刀]\n　!fdkp [第幾刀]', inline=False)
        embed_msg.add_field(name='設定', value='調整當前boss進度，請指明週目與第幾boss。\n　!設定 [週目] [boss]\n　!设定 [週目] [boss]\n　!s [週目] [boss]', inline=False)        
        await message.channel.send(embed=embed_msg)



      elif tokens[0] == '!一般指令' or tokens[0] == '!norcmd':
        embed_msg = Embed(title='[一般指令]', color=0xD8B8BA)
        embed_msg.add_field(name='預約', value='報刀至**刀表**。請指明週目、boss與備註。\n　!預約 [週目] [幾王] [備註]\n　!预约 [週目] [幾王] [備註]\n　!p [週目] [幾王] [備註]', inline=False)
        embed_msg.add_field(name='取消預約', value='取消自己於**刀表**中的刀。請指明週目、boss與**刀表**中的第幾刀。\n　!取消預約 [週目] [幾王] [第幾刀]\n　!取消预约 [週目] [幾王] [第幾刀]\n　!cp [週目] [幾王] [第幾刀]', inline=False)
        embed_msg.add_field(name='報保留刀', value='報刀至**保留區**。請指明boss與備註。\n　!報保留刀 [幾王] [備註]\n　!报保留刀 [幾王] [備註]\n　!kp [幾王] [備註]', inline=False)
        embed_msg.add_field(name='使用保留刀', value='使用自己於**保留區**中的某刀。請指明**保留區**中的第幾刀，要出的週目與boss。\n　!使用保留刀 [第幾刀] [週目] [boss]\n　!使用保留刀 [第幾刀] [週目] [boss]\n　!ukp [第幾刀] [週目] [boss]', inline=False)
        embed_msg.add_field(name='取消保留刀', value='取消自己於**保留區**中的某刀。請指明boss與**保留區**中的第幾刀。\n　!取消保留刀 [第幾刀]\n　!取消保留刀 [第幾刀]\n　!ckp [第幾刀]', inline=False)
        embed_msg.add_field(name='目前進度', value='顯示目前王的進度，其實刀表最上方就是目前的進度。\n　!目前進度\n　!目前进度\n　!ns', inline=False)
        embed_msg.add_field(name='下面一位', value='進入下一王時使用，同時會tag下一王的成員，30秒僅能使用一次。\n　!下面一位\n　!下面一位\n　!n', inline=False)
        embed_msg.add_field(name='出來打王', value='tag當前王的出刀人員。\n　!出來打王\n　!出来打王\n　!hb', inline=False)
        await message.channel.send(embed=embed_msg)


  except Error as e:
    print("資料庫錯誤 ",e)
  except Exception as e:
    print("error ",e)

