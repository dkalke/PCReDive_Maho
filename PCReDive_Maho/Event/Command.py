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
import Module.define_value


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

def knife_type_normalized(knife_type): # 檢查是否吻合繁體、檢體、英文、數字之形式
  if knife_type== "正刀":
    return 1
  elif knife_type== "尾刀":
    return 2
  elif knife_type== "補償刀":
    return 3
  elif knife_type== "补偿刀":
    return 3
  elif knife_type== "n": # normal
    return 1
  elif knife_type== "k": # kill
    return 2
  elif knife_type== "c": # compensate
    return 3
  elif knife_type== "1": # normal
    return 1
  elif knife_type== "2": # kill
    return 2
  elif knife_type== "3": # compensate
    return 3
  else:
    return 0


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

      #!報刀回傷 [boss] [序號] [類型] [傷害]
      elif tokens[0] == '!報刀回傷' or tokens[0] == '!报刀回伤' or tokens[0] == '!d':
        connection = await Module.DB_control.OpenConnection(message)
        if connection:
          cursor = connection.cursor(prepared=True)
          sql = "SELECT now_week_1, now_week_2, now_week_3, now_week_4, now_week_5, group_serial, policy FROM princess_connect.group WHERE server_id = ? and sign_channel_id = ? order by group_serial limit 0, 1"
          data = (message.guild.id, message.channel.id)
          cursor.execute(sql, data) # 認證身分
          row = cursor.fetchone()
          cursor.close
          if row:
            if len(tokens) == 5:
              boss, index, knife_type, real_damage = tokens[1], tokens[2], tokens[3], tokens[4]
              if boss.isdigit():
                if index.isdigit():
                  knife_type = knife_type_normalized(knife_type)
                  if knife_type: 
                    if real_damage.isdigit():
                      boss, index, real_damage = int(tokens[1]), int(tokens[2]), int(tokens[4])
                      if (0 < boss) and (boss < 6):
                        if 0 <= real_damage and real_damage <= Module.define_value.MAX_DAMAGE:
                          now_week = [row[0], row[1], row[2], row[3], row[4]]
                          group_serial = row[5]
                          policy = row[6]
                          if policy == Module.define_value.Policy.YES.value:
                            if index > 0:
                              # 尋找該刀
                              cursor = connection.cursor(prepared=True)
                              sql = "SELECT serial_number,member_id from princess_connect.knifes where server_id=? and group_serial=? and week=? and boss=? order by serial_number limit ?,1"
                              data = (message.guild.id, group_serial, now_week[boss-1], boss, index-1)
                              cursor.execute(sql, data)
                              row = cursor.fetchone()
                              cursor.close()
                              if row:
                                if message.author.id == row[1]:
                                  cursor = connection.cursor(prepared=True)
                                  sql = "UPDATE princess_connect.knifes set real_damage=?, knife_type=?, done_time=? where serial_number=?"
                                  data = (real_damage, knife_type, datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"), row[0])
                                  row = cursor.execute(sql, data)
                                  cursor.close()
                                  connection.commit()
                                  await message.channel.send('回報成功!')
                                  await Module.Update.Update(message, message.guild.id, group_serial) # 更新刀表
                                  await Module.info_update.info_update(message ,message.guild.id, group_serial) # 更新資訊
                                else:
                                  await message.channel.send('您並非該刀主人喔!')
                              else:
                                await message.channel.send('該刀不存在喔!')
                            else:
                              await message.channel.send('[第幾刀]必須大於0!')
                          else:
                            await message.channel.send('目前戰隊政策為:**不回報傷害**! 指令無效，感謝你的自主回報!')
                        else:
                          await message.channel.send('傷害異常，目前最高僅能紀載0至' + str(Module.define_value.MAX_DAMAGE) + '!')
                      else:
                        await message.channel.send('[boss]只能輸入1~5!')
                    else:
                      await message.channel.send('[傷害]請使用阿拉伯數字!')
                  else:
                    await message.channel.send('[種類]輸入錯誤，請參考說明書!')
                else:
                  await message.channel.send('[第幾刀]請使用阿拉伯數字!')
              else:
                await message.channel.send('[boss]請使用阿拉伯數字!')
            else:
              await message.channel.send('!報刀回傷 格式錯誤，應為 !報刀回傷 [boss] [第幾刀] [類型] [傷害]')
          else:
            await message.channel.send('這裡不是報刀頻道喔!')
          await Module.DB_control.CloseConnection(connection, message)

      #!無報回傷
      elif tokens[0] == '!無報回傷' or tokens[0] == '!取消保留刀' or tokens[0] == '!ds':
        print()


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
                  if ( not now_week[boss-1] >= main_week + 2 ) and (Module.week_stage.week_stage(now_week[boss-1]) == Module.week_stage.week_stage(main_week)):
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
                          if new_main_week == Module.define_value.Stage.one.value or \
                          new_main_week == Module.define_value.Stage.two.value or \
                          new_main_week == Module.define_value.Stage.three.value or \
                          new_main_week == Module.define_value.Stage.four.value or \
                          new_main_week == Module.define_value.Stage.five.value or \
                          (now_week[index-1] == main_week+2 and Module.week_stage.week_stage(now_week[index-1])== Module.week_stage.week_stage(new_main_week)):
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
                        if (now_week[boss-1] < main_week+2) and (Module.week_stage.week_stage(now_week[boss-1]) == Module.week_stage.week_stage(main_week)): # 檢查週目是否超出可出刀週目
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
        embed_msg = Embed(title='使用說明書', url='https://github.com/dkalke/PCReDive_Maho/wiki', description='網頁版使用說明書\nhttps://github.com/dkalke/PCReDive_Maho/wiki', color=0xB37084)
        embed_msg.set_footer(text='當前版本可能會有些許BUG，歡迎反應或許願新功能!')
        await message.channel.send(embed=embed_msg)


      # TODO 2021/10/23指令廢棄一律改用網頁版，過一陣子移除該指令。
      elif tokens[0] == '!管理員專用指令' or tokens[0] == '!管理员专用指令' or tokens[0] == '!admcmd':
        embed_msg = Embed(title='使用說明書', url='https://github.com/dkalke/PCReDive_Maho/wiki', description='網頁版使用說明書\nhttps://github.com/dkalke/PCReDive_Maho/wiki', color=0xB37084)
        embed_msg.set_footer(text='當前版本可能會有些許BUG，歡迎反應或許願新功能!')
        await message.channel.send(embed=embed_msg)


      # TODO 2021/10/23指令廢棄一律改用網頁版，過一陣子移除該指令。
      elif tokens[0] == '!戰隊隊長專用指令' or tokens[0] == '!战队队长专用指令' or tokens[0] == '!pricmd':
        embed_msg = Embed(title='使用說明書', url='https://github.com/dkalke/PCReDive_Maho/wiki', description='網頁版使用說明書\nhttps://github.com/dkalke/PCReDive_Maho/wiki', color=0xB37084)
        embed_msg.set_footer(text='當前版本可能會有些許BUG，歡迎反應或許願新功能!')
        await message.channel.send(embed=embed_msg)


      # TODO 2021/10/23指令廢棄一律改用網頁版，過一陣子移除該指令。
      elif tokens[0] == '!控刀手專用指令' or tokens[0] == '!控刀手专用指令' or tokens[0] == '!concmd':
        embed_msg = Embed(title='使用說明書', url='https://github.com/dkalke/PCReDive_Maho/wiki', description='網頁版使用說明書\nhttps://github.com/dkalke/PCReDive_Maho/wiki', color=0xB37084)
        embed_msg.set_footer(text='當前版本可能會有些許BUG，歡迎反應或許願新功能!')
        await message.channel.send(embed=embed_msg)


      # TODO 2021/10/23指令廢棄一律改用網頁版，過一陣子移除該指令。
      elif tokens[0] == '!一般指令' or tokens[0] == '!norcmd':
        embed_msg = Embed(title='使用說明書', url='https://github.com/dkalke/PCReDive_Maho/wiki', description='網頁版使用說明書\nhttps://github.com/dkalke/PCReDive_Maho/wiki', color=0xB37084)
        embed_msg.set_footer(text='當前版本可能會有些許BUG，歡迎反應或許願新功能!')
        await message.channel.send(embed=embed_msg)


  except Error as e:
    print("資料庫錯誤 ",e)
  except Exception as e:
    print("error ",e)

