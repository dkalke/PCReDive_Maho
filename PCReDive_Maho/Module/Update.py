import os
import mysql.connector
from discord import Embed
import Discord_client
import Name_manager
import Module.DB_control
import Module.define_value
import Module.week_stage

async def Update(message ,server_id, group_serial):
  connection = await Module.DB_control.OpenConnection(message)
  if connection.is_connected():
    cursor = connection.cursor(prepared=True)
    sql = "SELECT table_style FROM princess_connect.group WHERE server_id = ? and group_serial = ? LIMIT 0, 1"
    data = (server_id, group_serial)
    cursor.execute(sql, data)
    row = cursor.fetchone()
    cursor.close
    if row:
      if row[0] == 0:
        await UpdateEmbed(connection, message, server_id, group_serial)
      else:
        await UpdateTraditional(connection, message, server_id, group_serial)
    else:
      await message.channel.send(content='查無戰隊資料!')

    await Module.DB_control.CloseConnection(connection, message)
  
async def UpdateEmbed(connection, message, server_id, group_serial): # 更新刀表
  # 查詢當前周目、王、刀表訊息、保留刀訊息
  cursor = connection.cursor(prepared=True)
  sql = "SELECT now_week, week_offset, now_week_1, now_week_2, now_week_3, now_week_4, now_week_5, now_boss, table_channel_id, table_message_id, knife_pool_message_id, policy FROM princess_connect.group WHERE server_id = ? and group_serial = ? LIMIT 0, 1"
  data = (server_id, group_serial)
  cursor.execute(sql, data)
  row = cursor.fetchone()
  cursor.close
  if row:
    now_week = row[0]
    week_offset = row[1]
    now_boss_week = (row[2], row[3], row[4], row[5], row[6])
    now_boss = row[7]
    table_channel_id = row[8]
    table_message_id = row[9]
    knife_pool_message_id = row[10]
    policy = row[11]

    if table_message_id:
      embed_msg = Embed(title='第' + str(group_serial) + '戰隊刀表', color=0xD98B99)
      # 刀表部分，從當前週目開始印
      index_boss = now_boss # 僅第一個週目由此王開始
      for i in range(now_week, now_week + week_offset + 1):
        weel_stage = Module.week_stage.week_stage(i)
        week_msg = ''
        for j in range(index_boss,6):  
          kinfe_msg = ''
          if i < now_boss_week[j-1]: # 如果王的週目小於主週目(王死)則不顯示報刀資訊
            title_msg = '**'+ str(j) + '**王(**0**/**' + str(Module.define_value.BOSS_HP[weel_stage][j-1]) +'**)\n'
            kinfe_msg = '　(已討伐)\n'
          else:
            # 刀表SQL
            cursor = connection.cursor(prepared=True)
            sql = "SELECT member_id, comment, knife_type, done_time, real_damage FROM princess_connect.knifes WHERE server_id = ? and group_serial = ? and week = ? and boss = ? order by serial_number"
            data = (server_id, group_serial,i ,j)
            cursor.execute(sql, data)
            row = cursor.fetchone()
            index = 1
            kinfe_msg = '' # 該週目該王報刀資訊
            sum_damage = 0 # 報刀傷害總和(萬)
            while row:
              # 出刀狀況
              nick_name = await Name_manager.get_nick_name(message, row[0]) # 取得DC暱稱
              comment = row[1]
              knife_status = ''
              knife_type = ''

              # 如選擇需回報傷害，顯示出刀類型與出刀與否記號
              if policy == Module.define_value.Policy.YES.value:
                done_time = row[3]
                if done_time:
                  comment = '實際傷害:' + format(row[4],',')
                  knife_status = ":ballot_box_with_check: "

                  knife_type = row[2]
                  if knife_type == 1:
                    knife_type = '[正刀] '
                  elif knife_type == 2:
                    knife_type = '[尾刀] '
                  elif knife_type == 3:
                    knife_type = '[補償刀] '
                  else:
                    knife_type = ''
                else:
                  knife_status = ":negative_squared_cross_mark: "

              else:
                pass

              kinfe_msg = kinfe_msg + '　{' +str(index) + '} ' + knife_status + nick_name + '\n　　' + knife_type + comment + '\n'
              sum_damage = sum_damage + row[4]
              index = index +1
              row = cursor.fetchone()
            cursor.close()
            title_msg = '**'+ str(j) + '**王(**' + str(Module.define_value.BOSS_HP[weel_stage][j-1] - sum_damage) + '**/**' + str(Module.define_value.BOSS_HP[weel_stage][j-1]) +'**)\n'
          week_msg = week_msg + title_msg + kinfe_msg
        index_boss = 1
        embed_msg.add_field(name='\u200b', value='-   -   -   -   -   -   -   -   ', inline=False)
        embed_msg.add_field(name='第' + str(i) + '週目', value=week_msg , inline=False)
            
  
          
      try:
        guild = Discord_client.client.get_guild(server_id)
        channel = guild.get_channel(table_channel_id)
        message_obj = await channel.fetch_message(table_message_id)
        await message_obj.edit(embed=embed_msg)
      except:
        await message.channel.send(content='刀表訊息已被移除，請重新設定刀表頻道!')

      # 保留刀部分
      # 從一王印到五王
      # 刀表SQL
      cursor = connection.cursor(prepared=True)
      sql = "SELECT boss, member_id, comment FROM princess_connect.keep_knifes WHERE server_id = ? and group_serial = ? order by boss, serial_number"
      data = (server_id, group_serial)
      cursor.execute(sql, data)
      msg = ''
      index = 1
      row = cursor.fetchone()
      while row:  
        # {index} ?王 nickname\tcomment\n
        name = await Name_manager.get_nick_name(message, row[1])
        msg = msg + '{' +str(index) + '} ' + str(row[0]) + '王 ' + name + '\n　' + row[2] + '\n'
        index = index + 1
        row = cursor.fetchone()
      cursor.close
  
      # 修改保留刀表
      if msg == '':
        msg = '尚無保留刀資訊!'
      else:
        pass
      embed_msg = Embed(title='保留刀', color=0xD9ACA3)
      embed_msg.add_field(name='\u200b', value=msg , inline=False)
            

      # 取得訊息物件
      try:
        guild = Discord_client.client.get_guild(server_id)
        channel = guild.get_channel(table_channel_id)
        message_obj = await channel.fetch_message(knife_pool_message_id)
        await message_obj.edit(embed=embed_msg)
      except:
        await message.channel.send(content='保留區訊息已被移除，請重新設定刀表頻道!')

    else:
      await message.channel.send(content='請戰隊隊長設定刀表頻道!')
  else:
    await message.channel.send(content='查無戰隊資料!')


async def UpdateTraditional(connection, message, server_id, group_serial): # 更新刀表
  # 查詢當前周目、王、刀表訊息、保留刀訊息
  cursor = connection.cursor(prepared=True)
  sql = "SELECT now_week, week_offset, now_week_1, now_week_2, now_week_3, now_week_4, now_week_5, now_boss, table_channel_id, table_message_id, knife_pool_message_id, policy FROM princess_connect.group WHERE server_id = ? and group_serial = ? LIMIT 0, 1"
  data = (server_id, group_serial)
  cursor.execute(sql, data)
  row = cursor.fetchone()
  cursor.close
  if row:
    now_week = row[0]
    week_offset = row[1]
    now_boss_week = (row[2], row[3], row[4], row[5], row[6])
    now_boss = row[7]
    table_channel_id = row[8]
    table_message_id = row[9]
    knife_pool_message_id = row[10]
    policy = row[11]

    if table_message_id:
      # 刀表部分，從當前週目開始印
      send_msg = '```asciidoc\n'
      index_boss = now_boss # 僅第一個週目由此王開始
      for i in range(now_week, now_week + week_offset + 1):
        week_msg = ''
        weel_stage = Module.week_stage.week_stage(i)
        for j in range(index_boss,6):
          title_msg = ''
          knife_msg = ''
          if i < now_boss_week[j-1]: # 如果王的週目小於主週目(死了)則不顯示
            title_msg = ' ' + str(j) + '王(0/' + str(Module.define_value.BOSS_HP[weel_stage][j-1]) + ')\n'
            knife_msg = '　(已討伐)\n'
          else:
            # 刀表SQL
            cursor = connection.cursor(prepared=True)
            sql = "SELECT member_id, comment, knife_type, done_time, real_damage FROM princess_connect.knifes WHERE server_id = ? and group_serial = ? and week = ? and boss = ? order by serial_number"
            data = (server_id, group_serial,i ,j)
            cursor.execute(sql, data)
            row = cursor.fetchone()
            index = 1
            sum_damage = 0
            while row:
              # 出刀狀況
              nick_name = await Name_manager.get_nick_name(message, row[0])
              comment = row[1]
              knife_status = ''
              knife_type = ''
              sum_damage = sum_damage + row[4]

              # 如選擇需回報傷害，顯示出刀類型與出刀與否記號
              if policy == Module.define_value.Policy.YES.value:
                done_time = row[3]
                if done_time:
                  comment = '實際傷害:' + format(row[4],',')
                  knife_status = "V "

                  knife_type = row[2]
                  if knife_type == 1:
                    knife_type = '[正刀] '
                  elif knife_type == 2:
                    knife_type = '[尾刀] '
                  elif knife_type == 3:
                    knife_type = '[補償刀] '
                  else:
                    knife_type = ''
                else:
                  knife_status = "X "
              else:
                pass

              knife_msg = knife_msg + '  {' +str(index) + '} ' + knife_status + nick_name + '(' + knife_type + comment + ')\n'
              row = cursor.fetchone()
              index = index +1
            cursor.close()
            title_msg = ' ' + str(j) + '王(' + str(Module.define_value.BOSS_HP[weel_stage][j-1] - sum_damage) + '/' + str(Module.define_value.BOSS_HP[weel_stage][j-1]) + ')\n'
          
          week_msg = week_msg + title_msg + knife_msg  
        index_boss = 1
        send_msg = send_msg + '第' + str(i) + '週目:\n' + week_msg    
      send_msg = send_msg + '```'
            
      # 取得訊息物件
      try:
        guild = Discord_client.client.get_guild(server_id)
        channel = guild.get_channel(table_channel_id)
        message_obj = await channel.fetch_message(table_message_id)
        await message_obj.edit(content = send_msg)
      except:
        await message.channel.send(content='刀表訊息已被移除，請重新設定刀表頻道!')

      # 保留刀部分
      # 從一王印到五王
      # 刀表SQL
      cursor = connection.cursor(prepared=True)
      sql = "SELECT boss, member_id, comment FROM princess_connect.keep_knifes WHERE server_id = ? and group_serial = ? order by boss, serial_number"
      data = (server_id, group_serial)
      cursor.execute(sql, data)
      msg = '```asciidoc\n保留刀:\n'
      index = 1
      row = cursor.fetchone()
      while row:  
        # {index} ?王 nickname\tcomment\n
        name = await Name_manager.get_nick_name(message, row[1])
        msg = msg + '{' +str(index) + '} ' + str(row[0]) + '王 ' + name + '\t' + row[2] + '\n'
        index = index + 1
        row = cursor.fetchone()
      cursor.close

      # 取得訊息物件
      try:
        guild = Discord_client.client.get_guild(server_id)
        channel = guild.get_channel(table_channel_id)
        message_obj = await channel.fetch_message(knife_pool_message_id)
        if msg == '```asciidoc\n保留刀:\n':
          await message_obj.edit(content = '尚無保留刀資訊!')
        else:
          msg = msg + '```'
          await message_obj.edit(content = msg)
      except:
        await message.channel.send(content='保留區訊息已被移除，請重新設定刀表頻道!')

    else:
      await message.channel.send(content='請戰隊隊長設定刀表頻道!')
  else:
    await message.channel.send(content='查無戰隊資料!')