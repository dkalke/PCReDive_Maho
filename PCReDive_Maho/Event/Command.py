import os
import datetime
import csv
import re
import mysql.connector
from mysql.connector import Error

import discord
from discord import Embed
from Module.Kernel.Discord_client import client
import Module.Kernel.DB_control
import Module.Kernel.Authentication
import Module.Kernel.Update
import Module.Kernel.Offset_manager
import Module.Kernel.check_week
import Module.Kernel.check_boss
import Module.Kernel.full_string_to_half_and_lower
import Module.Kernel.define_value
import Module.Kernel.get_closest_end_time
import Module.Kernel.info_update
import Module.General.proposal_knife
import Module.General.cancel_proposal


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

def period_type_normalized(period):
  if period== "0" or period== "u" or period== "不定" or period== "不定??-??": # ??-??
    return Module.Kernel.define_value.Period.UNKNOW.value
  elif period== "1" or period== "d" or period== "日班" or period== "日班08-16": # 08-16
    return Module.Kernel.define_value.Period.DAY.value
  elif period== "2" or period== "n" or period== "晚班" or period== "晚班16-24": # 16-24
    return Module.Kernel.define_value.Period.NIGHT.value
  elif period== "3" or period== "g" or period== "夜班" or period== "夜班00-08": # 00-08
    return Module.Kernel.define_value.Period.GRAVEYARD.value
  elif period== "4" or period== "a" or period== "全日" or period== "全日00-24": # 00-24
    return Module.Kernel.define_value.Period.ALL.value
  else:
    return -1 # ERROR


@client.event
async def on_message(message):
  # 防止機器人自問自答
  if message.author == client.user:
    return

  # --------------------------------------------------------------------指令部分------------------------------------------------------------------------------------------------------
  try:
    tokens = message.content.split()
    if len(tokens) > 0: # 邊界檢查
      tokens[0] = Module.Kernel.full_string_to_half_and_lower.full_string_to_half_and_lower(tokens[0])

      # --------------------------------------------------------------------一般成員 僅限報刀頻道使用------------------------------------------------------------------------------------------------------          
      #報刀指令 !預約 [周目] [幾王] [註解]
      if tokens[0] == '!預約' or tokens[0] == '!预约' or tokens[0] == '!p':
        if len(tokens) == 4:
          if tokens[1].isdigit() and tokens[2].isdigit():
            comment = tokens[3]
            await Module.General.proposal_knife.proposal_knife(
              send_obj = message.channel, 
              server_id = message.guild.id, 
              sign_channel_id = message.channel.id, 
              member_id = message.author.id, 
              week = int(tokens[1]), 
              boss = int(tokens[2]), 
              comment = tokens[3]
            )
          else:
            await message.channel.send('[週目] [王] [預估傷害]請使用阿拉伯數字!')
        else:
          await message.channel.send('!預約 格式錯誤，應為 !預約 [週目] [王] [註解]')

      #!取消報刀  !取消預約 [周目] [幾王] [第幾刀]
      elif tokens[0] == '!取消預約' or tokens[0] == '!取消预约' or tokens[0] == '!cp':
        if len(tokens) == 4:
          if tokens[1].isdigit() and tokens[2].isdigit() and tokens[3].isdigit():
            await Module.General.cancel_proposal.cancel_proposal(
              send_obj = message.channel, 
              server_id = message.guild.id, 
              sign_channel_id = message.channel.id, 
              member_id = message.author.id, 
              week = int(tokens[1]), 
              boss = int(tokens[2]), 
              index = int(tokens[3])
            )
          else:
            await message.channel.send('[週目] [王] [第幾刀]請使用阿拉伯數字!')
        else:
          await message.channel.send('!取消預約 格式錯誤，應為 !取消預約 [週目] [王] [第幾刀]')

      #!報保留刀 [備註]
      elif tokens[0] == '!報保留刀' or tokens[0] == '!报保留刀' or tokens[0] == '!kp':
        # check頻道，並找出所屬組別
        group_serial = 0
        connection = await Module.Kernel.DB_control.OpenConnection(message)
        if connection:
          cursor = connection.cursor(prepared=True)
          sql = "SELECT group_serial FROM princess_connect.group WHERE server_id = ? and sign_channel_id = ? order by group_serial limit 0, 1"
          data = (message.guild.id, message.channel.id)
          cursor.execute(sql, data) # 認證身分
          row = cursor.fetchone()
          cursor.close
          if row:
            group_serial = row[0]
            if len(tokens) == 2:
              # 寫入保留刀表
              cursor = connection.cursor(prepared=True)
              sql = "INSERT INTO princess_connect.keep_knifes (server_id, group_serial, member_id, comment) VALUES (?, ?, ?, ?)"
              data = (message.guild.id, group_serial, message.author.id, tokens[1])
              cursor.execute(sql, data)
              cursor.close()
              connection.commit()
              await message.channel.send( '備註:' + tokens[1] + '，**保留刀**報刀成功!')
              await Module.Kernel.Update.Update(message, message.guild.id, group_serial) # 更新刀表
            else:
              await message.channel.send('!報保留刀 格式錯誤，應為 !報保留刀 [註解]')
          else:
            pass #非指定頻道 不反應
          await Module.Kernel.DB_control.CloseConnection(connection, message)
        
      #!使用保留刀 [第幾刀] [週目] [boss]
      elif tokens[0] == '!使用保留刀' or tokens[0] == '!使用保留刀' or tokens[0] == '!ukp':
        connection = await Module.Kernel.DB_control.OpenConnection(message)
        if connection:
          cursor = connection.cursor(prepared=True)
          sql = "SELECT  now_week, now_week_1, now_week_2, now_week_3, now_week_4, now_week_5, week_offset, group_serial FROM princess_connect.group WHERE server_id = ? and sign_channel_id = ? order by group_serial limit 0, 1"
          data = (message.guild.id, message.channel.id)
          cursor.execute(sql, data) # 認證身分
          row = cursor.fetchone()
          cursor.close
          if row:
            group_serial = row[7]
            # 檢測預估傷害格式
            token_5_pass_flag = True
            estimated_damage = 0
            if len(tokens) == 5:
              token_5_pass_flag = False
              if tokens[4].isdigit():
                token_5_pass_flag = True
                estimated_damage = int(tokens[4])


            if len(tokens) == 4 or len(tokens) == 5 :
              if tokens[1].isdigit() and tokens[2].isdigit() and token_5_pass_flag:
                index = int(tokens[1]) # TODO check index 不可為負數
                week = int(tokens[2])
                boss = int(tokens[3])
                if Module.Kernel.check_week.Check_week((row[0], row[6]), week):
                  if Module.Kernel.check_boss.Check_boss((row[1], row[2], row[3], row[4], row[5]),week, boss):  
                    if not (Module.Kernel.week_stage.week_stage(week) == 4 and estimated_damage == 0):
                      # 檢查溢傷
                      sql = "SELECT SUM(estimated_damage) from knifes WHERE server_id = ? and group_serial = ? and week = ? and boss = ?"
                      data = (message.guild.id, group_serial, week, boss)
                      cursor.execute(sql, data)
                      row = cursor.fetchone()
                      cursor.close
                      sum_estimated_damage = 0
                      if row[0]:
                        sum_estimated_damage = int(row[0])
                      if (Module.Kernel.define_value.BOSS_HP[Module.Kernel.week_stage.week_stage(week)][boss-1] - sum_estimated_damage) > 0:
                        cursor = connection.cursor(prepared=True)
                        sql = "SELECT serial_number, member_id, comment from princess_connect.keep_knifes where server_id=? and group_serial=? order by serial_number limit ?,1"
                        data = (message.guild.id, group_serial, index-1)
                        cursor.execute(sql, data)
                        row = cursor.fetchone()
                        cursor.close()
                        if row:
                          if message.author.id == row[1]:
                            # 新增刀
                            cursor = connection.cursor(prepared=True)
                            sql = "INSERT INTO princess_connect.knifes (server_id, group_serial, week, boss, member_id, comment, timestamp, estimated_damage) VALUES (?, ?, ?, ?, ?, ?, ?, ?)"
                            data = (message.guild.id, group_serial, week, boss, row[1], row[2] ,datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"), estimated_damage)
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
                            await Module.Kernel.Update.Update(message, message.guild.id, group_serial) # 更新刀表
                          else:
                            await message.channel.send('您並非該刀主人喔!')
                        else:
                          await message.channel.send('該刀不存在喔!')   
                      else:
                        await message.channel.send('偵測到溢傷，請改報其他週目!')
                    else:
                      await message.channel.send('發生錯誤，五階段使用保留刀格式為: !ukp [序號] [週目] [boss] [預估傷害(萬)]')
                  else:
                    await message.channel.send('該王不存在喔!')
                else:
                  await message.channel.send('該週目不存在喔!')
              else:
                await message.channel.send('[第幾刀] [週目] [boss]請使用阿拉伯數字!')
            else:
              await message.channel.send('!使用保留刀 格式錯誤，應為:\n 1~4階段: !使用保留刀 [第幾刀] [週目] [boss]\n5階段: !使用保留刀 [第幾刀] [週目] [boss] [預估傷害]')
          else:
            pass #非指定頻道 不反應
          await Module.Kernel.DB_control.CloseConnection(connection, message)

      #!取消保留刀 [第幾刀]
      elif tokens[0] == '!取消保留刀' or tokens[0] == '!取消保留刀' or tokens[0] == '!ckp':
        connection = await Module.Kernel.DB_control.OpenConnection(message)
        if connection:
          cursor = connection.cursor(prepared=True)
          sql = "SELECT  now_week, week_offset, group_serial FROM princess_connect.group WHERE server_id = ? and sign_channel_id = ? order by group_serial limit 0, 1"
          data = (message.guild.id, message.channel.id)
          cursor.execute(sql, data) # 認證身分
          row = cursor.fetchone()
          cursor.close
          if row:
            group_serial = row[2]
            if len(tokens) == 2:
              if tokens[1].isdigit():
                index = int(tokens[1]) # TODO check index 不可為負數

                # 尋找要刪除刀的序號
                cursor = connection.cursor(prepared=True)
                sql = "SELECT serial_number,member_id from princess_connect.keep_knifes where server_id=? and group_serial=? order by serial_number limit ?,1"
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
                    await Module.Kernel.Update.Update(message, message.guild.id, group_serial) # 更新刀表
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
          await Module.Kernel.DB_control.CloseConnection(connection, message)

      #!下面一位 [boss]
      elif tokens[0] == '!下面一位' or tokens[0] == '!下面一位' or tokens[0] == '!n':
        if len(tokens) == 2:
          if tokens[1].isdigit():
            boss = int(tokens[1])
            if boss > 0 and boss < 6:
              connection = await Module.Kernel.DB_control.OpenConnection(message)
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
                  if ( not now_week[boss-1] >= main_week + 2 ) and (Module.Kernel.week_stage.week_stage(now_week[boss-1]) == Module.Kernel.week_stage.week_stage(main_week)):
                    if message.created_at + datetime.timedelta(hours = 8) >= boss_change[boss-1] + datetime.timedelta(seconds = Module.Kernel.define_value.CD_TIME): 
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
                        knifes = await Module.Kernel.show_knifes.show_knifes(connection, message, group_serial, now_week[boss-1] ,boss)
            
                        if knifes == '':
                          msg[boss-1] = '目前' + str(now_week[boss-1]) + '週' + str(boss) + '王沒人報刀喔，看在真步的面子上，快來報刀!\n'
                        else:
                          msg[boss-1] = knifes + str(now_week[boss-1]) + '週' + str(boss) + '王到囉!\n'

                        # 去除當前的boss
                        boss_index=list(range(1,6))
                        boss_index.remove(boss)

                        #如果其他王week位處main_week+2，一併tag上來
                        for index in boss_index:
                          if new_main_week == Module.Kernel.define_value.Stage.one.value or \
                          new_main_week == Module.Kernel.define_value.Stage.two.value or \
                          new_main_week == Module.Kernel.define_value.Stage.three.value or \
                          new_main_week == Module.Kernel.define_value.Stage.four.value or \
                          new_main_week == Module.Kernel.define_value.Stage.five.value or \
                          (now_week[index-1] == main_week+2 and Module.Kernel.week_stage.week_stage(now_week[index-1])== Module.Kernel.week_stage.week_stage(new_main_week)):
                            knifes = await Module.Kernel.show_knifes.show_knifes(connection, message, group_serial, now_week[index-1] ,index)

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
                        Module.Kernel.Offset_manager.AutoOffset(connection, message.guild.id, group_serial) 
                      else:
                        if (now_week[boss-1] < main_week+2) and (Module.Kernel.week_stage.week_stage(now_week[boss-1]) == Module.Kernel.week_stage.week_stage(main_week)): # 檢查週目是否超出可出刀週目
                          knifes = await Module.Kernel.show_knifes.show_knifes(connection, message, group_serial, now_week[boss-1] ,boss)

                          if knifes == '':
                            msg[boss-1] = '目前' + str(now_week[boss-1]) + '週' + str(boss) + '王沒人報刀喔，看在真步的面子上，快來報刀!'
                          else:
                            msg[boss-1] = knifes + str(now_week[boss-1]) + '週' + str(boss) + '王到囉!'

                        else:
                          msg[boss-1] = str(now_week[boss-1] - 1) +'週' + str(boss) + '王已討伐，等待其他boss中。'

                      await message.channel.send(msg[0]+msg[1]+msg[2]+msg[3]+msg[4])

                      await Module.Kernel.Update.Update(message, message.guild.id, group_serial) # 更新刀表
                    else:
                      await message.channel.send(str(boss) + '王目前CD中，上次使用時間:' + str(boss_change[boss-1]) + '。' )
                  else:
                    await message.channel.send('當前主週目為' + str(main_week) + '，還打不到' + str(now_week[boss-1]) + '週' + str(boss) + '王喔!')
                else:
                  pass #非指定頻道 不反應

                await Module.Kernel.DB_control.CloseConnection(connection, message)
            else:
              await message.channel.send('王只能是包含1~5的正整數!')
          else:
            await message.channel.send('請輸入數字!')
        else:
          await message.channel.send('!下面一位 格式錯誤，應為 !下面一位 [boss]')

      #!反悔 [boss]
      elif tokens[0] == '!反悔' or tokens[0] == '!反悔' or tokens[0] == '!cn':
        if len(tokens) == 2:
          if tokens[1].isdigit():
            boss = int(tokens[1])
            if boss > 0 and boss < 6:
              connection = await Module.Kernel.DB_control.OpenConnection(message)
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
                  if boss_change[boss-1] <= message.created_at + datetime.timedelta(hours = 8):
                    if message.created_at + datetime.timedelta(hours = 8) <= boss_change[boss-1] + datetime.timedelta(seconds = Module.Kernel.define_value.NCD_TIME): 
                      # 更新該王週目與主週目
                      # 注意，為避免濫用此功能，使用/cn後，會將/n的時間加上60秒，可達到以下效果
                      # 1. 避免/n /cn 重複來回使用
                      # 2. 避免60秒內 連續使用/cn
                      # 3. 僅能使用/cn回退一個週目
                      now_week[boss-1] = now_week[boss-1]-1
                      new_main_week = min(now_week)
                      cursor = connection.cursor(prepared=True)
                      sql = ""
                      if boss==1:
                        sql = "UPDATE princess_connect.group SET now_week_1=?, now_week=?, boss_change_1=?  WHERE server_id = ? and sign_channel_id = ?"
                      elif boss==2:
                        sql = "UPDATE princess_connect.group SET now_week_2=?, now_week=?, boss_change_2=? WHERE server_id = ? and sign_channel_id = ?"
                      elif boss==3:
                        sql = "UPDATE princess_connect.group SET now_week_3=?, now_week=?, boss_change_3=? WHERE server_id = ? and sign_channel_id = ?"
                      elif boss==4:
                        sql = "UPDATE princess_connect.group SET now_week_4=?, now_week=?, boss_change_4=? WHERE server_id = ? and sign_channel_id = ?"
                      elif boss==5:
                        sql = "UPDATE princess_connect.group SET now_week_5=?, now_week=?, boss_change_5=? WHERE server_id = ? and sign_channel_id = ?"
                      data = (now_week[boss-1], new_main_week, (boss_change[boss-1] + datetime.timedelta(seconds = Module.Kernel.define_value.NCD_TIME)).strftime("%Y-%m-%d %H:%M:%S"), message.guild.id, message.channel.id)
                      cursor.execute(sql, data)
                      cursor.close
                      connection.commit()

                      await message.channel.send(str(boss) + '王已退回' + str(now_week[boss-1]) + '週目，請務必提醒受影響成員，以免成員誤入!')
                      Module.Kernel.Offset_manager.AutoOffset(connection, message.guild.id, group_serial) # 自動周目控制
                      await Module.Kernel.Update.Update(message, message.guild.id, group_serial) # 更新刀表
                    else:
                      await message.channel.send(str(boss) + '王已超過可反悔時間，請聯繫控刀手!\n/n下次可用時間:' + str(boss_change[boss-1] + datetime.timedelta(seconds = Module.Kernel.define_value.NCD_TIME + Module.Kernel.define_value.CD_TIME )) + '。' )
                  else:
                    await message.channel.send('只能反悔一週，如有需要請聯繫控刀手!')

                else:
                  pass #非指定頻道 不反應

                await Module.Kernel.DB_control.CloseConnection(connection, message)
            else:
              await message.channel.send('王只能是包含1~5的正整數!')
          else:
            await message.channel.send('請輸入數字!')
        else:
          await message.channel.send('!反悔 格式錯誤，應為 !反悔 [boss]')

      #!偏好時段 [時段]
      elif tokens[0] == '!偏好時段' or tokens[0] == '!偏好时段' or tokens[0] == '!pt':
        connection = await Module.Kernel.DB_control.OpenConnection(message)
        if connection:
          cursor = connection.cursor(prepared=True)
          sql = "SELECT group_serial FROM princess_connect.group WHERE server_id = ? and sign_channel_id = ? order by group_serial limit 0, 1"
          data = (message.guild.id, message.channel.id)
          cursor.execute(sql, data) # 認證身分
          row = cursor.fetchone()
          cursor.close
          if row:
            group_serial = row[0]
            if len(tokens) == 2:
              period = period_type_normalized(tokens[1])
              if not period == -1:
                # 檢查使否屬於該戰隊
                cursor = connection.cursor(prepared=True)
                sql = "select * from princess_connect.members WHERE server_id = ? and group_serial = ? and member_id = ? limit 0,1"
                data = (message.guild.id, group_serial, message.author.id)
                cursor.execute(sql, data)
                row = cursor.fetchone()
                if row:
                  # 修改出刀偏好
                  cursor = connection.cursor(prepared=True)
                  sql = "update princess_connect.members SET period=? WHERE server_id = ? and group_serial = ? and member_id = ?"
                  data = (period, message.guild.id, group_serial, message.author.id)
                  cursor.execute(sql, data)
                  connection.commit()
                  await Module.Kernel.info_update.info_update(message ,message.guild.id, group_serial)
                  await message.channel.send('您在第' + str(group_serial) + '戰隊的出刀偏好時段已修改完成!')
                else:
                  await message.channel.send('您不屬於第' + str(group_serial) + '戰隊喔!')
              else:
                await message.channel.send('[時段]輸入錯誤，請參考說明書!')
            else:
              await message.channel.send('!偏好時段 格式錯誤，應為 !偏好時段 [時段]')
          else:
            await message.channel.send('這裡不是報刀頻道喔，請在所屬戰隊報刀頻道使用!')
          await Module.Kernel.DB_control.CloseConnection(connection, message)

      #!閃退
      elif tokens[0] == '!閃退' or tokens[0] == '!闪退' or tokens[0] == '!sl':
        connection = await Module.Kernel.DB_control.OpenConnection(message)
        if connection:
          cursor = connection.cursor(prepared=True)
          sql = "SELECT group_serial FROM princess_connect.group WHERE server_id = ? and sign_channel_id = ? order by group_serial limit 0, 1"
          data = (message.guild.id, message.channel.id)
          cursor.execute(sql, data) # 認證身分
          row = cursor.fetchone()
          cursor.close
          if row:
            group_serial = row[0]

            # 檢查使否屬於該戰隊
            cursor = connection.cursor(prepared=True)
            sql = "select last_sl_time from princess_connect.members WHERE server_id = ? and group_serial = ? and member_id = ? limit 0,1"
            data = (message.guild.id, group_serial, message.author.id)
            cursor.execute(sql, data)
            row = cursor.fetchone()
            if row:
              # 修改SL時間
              closest_end_time = Module.Kernel.get_closest_end_time.get_closest_end_time(datetime.datetime.now())
              if row[0] < closest_end_time:
                cursor = connection.cursor(prepared=True)
                sql = "update princess_connect.members SET last_sl_time=? WHERE server_id = ? and group_serial = ? and member_id = ?"
                data = (closest_end_time, message.guild.id, group_serial, message.author.id)
                cursor.execute(sql, data)
                connection.commit()
                await message.channel.send('紀錄完成!')
                await Module.Kernel.info_update.info_update(message ,message.guild.id, group_serial)
              else:
                await message.channel.send('注意，今日已使用過SL，請勿退出遊戲!')
            else:
              await message.channel.send('您不屬於第' + str(group_serial) + '戰隊喔!')
          else:
            await message.channel.send('這裡不是報刀頻道喔，請在所屬戰隊報刀頻道使用!')
          await Module.Kernel.DB_control.CloseConnection(connection, message)

      #!add_puppet
      elif tokens[0] == '!add_puppet':
        connection = await Module.Kernel.DB_control.OpenConnection(message)
        if connection:
          cursor = connection.cursor(prepared=True)
          sql = "SELECT now_week, now_week_1, now_week_2, now_week_3, now_week_4, now_week_5, week_offset, group_serial FROM princess_connect.group WHERE server_id = ? and sign_channel_id = ? order by group_serial limit 0, 1"
          data = (message.guild.id, message.channel.id)
          cursor.execute(sql, data) # 認證身分
          row = cursor.fetchone()
          cursor.close
          if row:
            group_serial = row[7]
            if len(tokens) == 1:
              # 檢查成員是否存, 並找出最大的puppet number
              cursor = connection.cursor(prepared=True)
              sql = "SELECT MAX(sockpuppet) FROM princess_connect.members WHERE server_id=? and group_serial = ? and member_id=?"
              data = (message.guild.id, group_serial, message.author.id)
              cursor.execute(sql, data)
              row = cursor.fetchone()
              cursor.close
              if not row[0] == None:
                # Insert 一條新的，puppet number + 1，並使其禁用
                sockpuppet = int(row[0]) + 1
                cursor = connection.cursor(prepared=True)
                sql = "INSERT INTO princess_connect.members (server_id, group_serial, member_id, sockpuppet, now_using) VALUES (?, ?, ?, ?, ?)"
                data = (message.guild.id, group_serial, message.author.id, sockpuppet, 0)
                cursor.execute(sql, data)
                cursor.close
                connection.commit() # 資料庫存檔

                await message.channel.send('您已取得分身{}，請使用!use {}進行切換'.format(sockpuppet, sockpuppet))
                await Module.Kernel.info_update.info_update(message ,message.guild.id, group_serial)
              else:
                await message.channel.send('該成員不在此戰隊中')
            else:
              await message.channel.send('格式錯誤，應為:\n!add_puppet')
          else:
            pass #非指定頻道 不反應
          await Module.Kernel.DB_control.CloseConnection(connection, message)

      #!del_puppet
      elif tokens[0] == '!del_puppet':
        if len(tokens) == 1:
          connection = await Module.Kernel.DB_control.OpenConnection(message)
          if connection:
            cursor = connection.cursor(prepared=True)
            sql = "SELECT now_week, now_week_1, now_week_2, now_week_3, now_week_4, now_week_5, week_offset, group_serial FROM princess_connect.group WHERE server_id = ? and sign_channel_id = ? order by group_serial limit 0, 1"
            data = (message.guild.id, message.channel.id)
            cursor.execute(sql, data) # 認證身分
            row = cursor.fetchone()
            cursor.close
            if row:
              group_serial = row[7]
              # 檢查成員是否存, 並找出最大的puppet number
              sql = "SELECT MAX(sockpuppet) FROM princess_connect.members WHERE server_id=? and group_serial = ? and member_id=?"
              data = (message.guild.id, group_serial, message.author.id)
              cursor.execute(sql, data)
              row = cursor.fetchone()
              cursor.close
              if not row[0] == None:
                sockpuppet = int(row[0])
                if sockpuppet != 0:
                  # Delect 最大隻的 puppet
                  # 刪除帳務資訊
                  sockpuppet = int(row[0])
                  cursor = connection.cursor(prepared=True)
                  sql = "Delete FROM princess_connect.members WHERE server_id = ? and group_serial = ? AND member_id = ? AND sockpuppet = ?"
                  data = (message.guild.id, group_serial, message.author.id, sockpuppet)
                  cursor.execute(sql, data)
                  cursor.close

                  # 切換帳號
                  # 先關閉持有的所有帳號，再開啟要使用的帳號
                  # 關閉
                  cursor = connection.cursor(prepared=True)
                  sql = "UPDATE princess_connect.members SET now_using = '0' WHERE server_id = ? and group_serial = ? AND member_id = ?"
                  data = (message.guild.id, group_serial, message.author.id)
                  cursor.execute(sql, data)
                  cursor.close

                  # 開啟本尊
                  cursor = connection.cursor(prepared=True)
                  sql = "UPDATE princess_connect.members SET now_using = '1' WHERE server_id = ? and group_serial = ? AND member_id = ? AND sockpuppet = '0' "
                  data = (message.guild.id, group_serial, message.author.id)
                  cursor.execute(sql, data)
                  cursor.close

                  connection.commit() # 資料庫存檔
              
                  await message.channel.send('您已刪除分身{}，為您切換至本尊'.format(sockpuppet))
                  await Module.Kernel.info_update.info_update(message ,message.guild.id, group_serial)
                else:
                  await message.channel.send('您已無分身')
              else:
                await message.channel.send('該成員不在此戰隊中')

              await Module.Kernel.DB_control.CloseConnection(connection, message)
            else:
              pass #非指定頻道 不反應
            await Module.Kernel.DB_control.CloseConnection(connection, message)
        else:
          await message.channel.send('格式錯誤，應為:\n!del_puppet')

      #!use [分身編號]
      elif tokens[0] == '!use':
        if len(tokens) == 2:
          if tokens[1].isdigit():
            use_sockpuppet = int(tokens[1])
            connection = await Module.Kernel.DB_control.OpenConnection(message)
            if connection:
              cursor = connection.cursor(prepared=True)
              sql = "SELECT now_week, now_week_1, now_week_2, now_week_3, now_week_4, now_week_5, week_offset, group_serial FROM princess_connect.group WHERE server_id = ? and sign_channel_id = ? order by group_serial limit 0, 1"
              data = (message.guild.id, message.channel.id)
              cursor.execute(sql, data) # 認證身分
              row = cursor.fetchone()
              cursor.close
              if row:
                group_serial = row[7]
                # 檢查成員是否存在，並取得最大隻的分身編號
                cursor = connection.cursor(prepared=True)
                sql = "SELECT MAX(sockpuppet) FROM princess_connect.members WHERE server_id=? and group_serial = ? and member_id=?"
                data = (message.guild.id, group_serial, message.author.id)
                cursor.execute(sql, data)
                row = cursor.fetchone()
                cursor.close
                if row[0] != None:
                  max_sockpuppet = int(row[0])
                  if 0 <= use_sockpuppet and use_sockpuppet <= max_sockpuppet:
                    # 先關閉持有的所有帳號，再開啟要使用的帳號
                    # 關閉
                    cursor = connection.cursor(prepared=True)
                    sql = "UPDATE princess_connect.members SET now_using = '0' WHERE server_id = ? and group_serial = ? AND member_id = ?"
                    data = (message.guild.id, group_serial, message.author.id)
                    cursor.execute(sql, data)
                    cursor.close

                    # 開啟
                    cursor = connection.cursor(prepared=True)
                    sql = "UPDATE princess_connect.members SET now_using = '1' WHERE server_id = ? and group_serial = ? AND member_id = ? AND sockpuppet = ? "
                    data = (message.guild.id, group_serial, message.author.id, use_sockpuppet)
                    cursor.execute(sql, data)
                    cursor.close

                    connection.commit() # 資料庫存檔
              
                    if use_sockpuppet == 0:
                      await message.channel.send('為您切換至本尊')
                    else:
                      await message.channel.send('為您切換至分身{}'.format(use_sockpuppet))
                    await Module.Kernel.info_update.info_update(message ,message.guild.id, group_serial)
                  else:
                    await message.channel.send('你沒有這隻分身喔')
                else:
                  await message.channel.send('該成員不在此戰隊中')

                await Module.Kernel.DB_control.CloseConnection(connection, message)
              else:
                pass #非指定頻道 不反應
              await Module.Kernel.DB_control.CloseConnection(connection, message)
          else:
            await message.channel.send('[分身編號] 僅能使用阿拉伯數字')
        else:
          await message.channel.send('格式錯誤，應為:\n!del_puppet')

         
      # --------------------------------------------------------------------所有頻道，所有人皆可使用------------------------------------------------------------------------------------------------------          
      #.ts [秒數]
      #[刀軸]
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
                    match = re.match(r'(\D*)(\d{2,3})((\s*[~-]\s*)(\d{2,3}))?(.*)?', filter) # 擷取時間
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
                                totaltime2 = time2 % 100 + time2 // 100 * 60 # time2的秒數
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
            await message.author.send("您輸入的秒數格式錯誤！正確的格式為\n.tr 補償秒數\n文字軸\n\n(補償秒數後面請直接換行，不要有其他字元)")
      
      #!幫助
      elif tokens[0] == '!幫助' or tokens[0] == '!帮助' or tokens[0] == '!h':
        embed_msg = Embed(title='使用說明書', url='https://github.com/dkalke/PCReDive_Maho/wiki', description='網頁版使用說明書\nhttps://github.com/dkalke/PCReDive_Maho/wiki', color=0xB37084)
        embed_msg.set_footer(text='當前版本可能會有些許BUG，歡迎反應或許願新功能!')
        await message.channel.send(embed=embed_msg)


  except Error as e:
    print("資料庫錯誤 ",e)
  except Exception as e:
    print("error ",e)

