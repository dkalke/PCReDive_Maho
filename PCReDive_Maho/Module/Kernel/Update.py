from discord import Embed
import Module.Kernel.Discord_client
import Module.Kernel.Name_manager
import Module.Kernel.DB_control
import Module.Kernel.define_value
import Module.Kernel.week_stage

async def Update(send_obj ,server_id, group_serial):
  connection = await Module.Kernel.DB_control.OpenConnection(send_obj)
  if connection.is_connected():
    cursor = connection.cursor(prepared=True)
    sql = "SELECT table_style FROM princess_connect.group WHERE server_id = ? and group_serial = ? LIMIT 0, 1"
    data = (server_id, group_serial)
    cursor.execute(sql, data)
    row = cursor.fetchone()
    cursor.close
    if row:
      if row[0] == 0:
        await UpdateEmbed(connection, send_obj, server_id, group_serial)
      else:
        await UpdateTraditional(connection, send_obj, server_id, group_serial)
    else:
      await send_obj.send(content='查無戰隊資料!')

    await Module.Kernel.DB_control.CloseConnection(connection, send_obj)
  
async def UpdateEmbed(connection, send_obj, server_id, group_serial): # 更新刀表
  # 查詢當前周目、王、刀表訊息、保留刀訊息
  cursor = connection.cursor(prepared=True)
  sql = "SELECT now_week, week_offset, now_week_1, now_week_2, now_week_3, now_week_4, now_week_5, table_channel_id, table_message_id, knife_pool_message_id FROM princess_connect.group WHERE server_id = ? and group_serial = ? LIMIT 0, 1"
  data = (server_id, group_serial)
  cursor.execute(sql, data)
  row = cursor.fetchone()
  cursor.close
  if row:
    now_week = row[0]
    week_offset = row[1]
    now_boss_week = (row[2], row[3], row[4], row[5], row[6])
    table_channel_id = row[7]
    table_message_id = row[8]
    knife_pool_message_id = row[9]

    if table_message_id:
      embed_msg = Embed(title='第' + str(group_serial) + '戰隊刀表', color=0xD98B99)
      lenth_counter = 0 # 為避免超出系統限制，單一區段僅能有1024字元，整體embed僅能有6000字元
      # 刀表部分，從當前週目開始印
      for i in range(now_week, now_week + week_offset + 1):
        week_stage = Module.Kernel.week_stage.week_stage(i)
        week_msg = ''
        for j in range(1,6):  
          kinfe_msg = ''
          if i < now_boss_week[j-1]: # 如果王的週目小於主週目(王死)則不顯示報刀資訊
            title_msg = '**'+ str(j) + '**王(**0**/**' + str(Module.Kernel.define_value.BOSS_HP[week_stage][j-1]) +'**)\n'
            kinfe_msg = '　(已討伐)\n'
          else:
            # 刀表SQL
            cursor = connection.cursor(prepared=True)
            sql = "SELECT member_id, comment, knife_type, done_time, real_damage, estimated_damage FROM princess_connect.knifes WHERE server_id = ? and group_serial = ? and week = ? and boss = ? order by serial_number"
            data = (server_id, group_serial,i ,j)
            cursor.execute(sql, data)
            row = cursor.fetchone()
            index = 1
            kinfe_msg = '' # 該週目該王報刀資訊
            estimated_sum_damage = 0 # 報刀傷害總和(萬)
            while row:
              # 出刀狀況
              nick_name = await Module.Kernel.Name_manager.get_nick_name(server_id, row[0]) # 取得DC暱稱
              comment = row[1]
              knife_status = ''

              # 如選擇需回報傷害，顯示出刀類型與出刀與否記號
              done_time = row[3]
              if done_time:
                comment = '實際傷害:' + format(row[4],',')
                knife_status = "V "
              else:
                knife_status = "X "

              kinfe_msg = kinfe_msg + '　{' +str(index) + '} ' + knife_status + nick_name + '\n　　' + comment + '\n'
              estimated_sum_damage = estimated_sum_damage + row[5]
              index = index +1
              row = cursor.fetchone()
            cursor.close()
            title_msg = '**'+ str(j) + '**王(**' + str(Module.Kernel.define_value.BOSS_HP[week_stage][j-1] - estimated_sum_damage) + '**/**' + str(Module.Kernel.define_value.BOSS_HP[week_stage][j-1]) +'**)\n'
          week_msg = week_msg + title_msg + kinfe_msg
        lenth_counter += len(week_msg)
        if lenth_counter < 5500:
          embed_msg.add_field(name='\u200b', value='-   -   -   -   -   -   -   -   ', inline=False)
          if len(week_msg) <= 950:
            embed_msg.add_field(name='第' + str(i) + '週目', value=week_msg , inline=False)
          else:
            embed_msg.add_field(name='第' + str(i) + '週目', value=week_msg[0:950] + '/n 超出1024字元，無法顯示。' , inline=False)
        else:
          embed_msg.add_field(name='第' + str(i) + '週目', value='刀表超出6000字元，已暫緩顯示' , inline=False)
          break
            
  
          
      try:
        guild = Module.Kernel.Discord_client.bot.get_guild(server_id)
        channel = guild.get_channel(table_channel_id)
        message_obj = await channel.fetch_message(table_message_id)
        await message_obj.edit(embed=embed_msg)
      except:
        await send_obj.send(content='更新刀表時發生錯誤，請檢查有無設定刀表頻道，或連繫作者檢查!')

      # 保留刀部分
      # 從一王印到五王
      # 刀表SQL
      cursor = connection.cursor(prepared=True)
      sql = "SELECT member_id, comment FROM princess_connect.keep_knifes WHERE server_id = ? and group_serial = ? order by serial_number"
      data = (server_id, group_serial)
      cursor.execute(sql, data)
      msg = ''
      index = 1
      row = cursor.fetchone()
      while row:  
        # {index} nickname\tcomment\n
        name = await Module.Kernel.Name_manager.get_nick_name(server_id, row[0])
        msg = msg + '{' +str(index) + '} ' + name + '\n　' + row[1] + '\n'
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
        guild = Module.Kernel.Discord_client.bot.get_guild(server_id)
        channel = guild.get_channel(table_channel_id)
        message_obj = await channel.fetch_message(knife_pool_message_id)
        await message_obj.edit(embed=embed_msg)
      except:
        await send_obj.send(content='保留區訊息已被移除，請重新設定刀表頻道!')

    else:
      await send_obj.send(content='請戰隊隊長設定刀表頻道!')
  else:
    await send_obj.send(content='查無戰隊資料!')


async def UpdateTraditional(connection, send_obj, server_id, group_serial): # 更新刀表
  # 查詢當前周目、王、刀表訊息、保留刀訊息
  cursor = connection.cursor(prepared=True)
  sql = "SELECT now_week, week_offset, now_week_1, now_week_2, now_week_3, now_week_4, now_week_5, table_channel_id, table_message_id, knife_pool_message_id FROM princess_connect.group WHERE server_id = ? and group_serial = ? LIMIT 0, 1"
  data = (server_id, group_serial)
  cursor.execute(sql, data)
  row = cursor.fetchone()
  cursor.close
  if row:
    now_week = row[0]
    week_offset = row[1]
    now_boss_week = (row[2], row[3], row[4], row[5], row[6])
    table_channel_id = row[7]
    table_message_id = row[8]
    knife_pool_message_id = row[9]

    if table_message_id:
      # 刀表部分，從當前週目開始印
      send_msg = '```asciidoc\n'
      for i in range(now_week, now_week + week_offset + 1):
        week_msg = ''
        week_stage = Module.Kernel.week_stage.week_stage(i)
        for j in range(1,6):
          title_msg = ''
          knife_msg = ''
          if i < now_boss_week[j-1]: # 如果王的週目小於主週目(死了)則不顯示
            title_msg = ' ' + str(j) + '王(0/' + str(Module.Kernel.define_value.BOSS_HP[week_stage][j-1]) + ')\n'
            knife_msg = '　(已討伐)\n'
          else:
            # 刀表SQL
            cursor = connection.cursor(prepared=True)
            sql = "SELECT member_id, comment, knife_type, done_time, real_damage, estimated_damage FROM princess_connect.knifes WHERE server_id = ? and group_serial = ? and week = ? and boss = ? order by serial_number"
            data = (server_id, group_serial,i ,j)
            cursor.execute(sql, data)
            row = cursor.fetchone()
            index = 1
            estimated_sum_damage = 0
            while row:
              # 出刀狀況
              nick_name = await Module.Kernel.Name_manager.get_nick_name(server_id, row[0])
              comment = row[1]
              knife_status = ''
              estimated_sum_damage = estimated_sum_damage + row[5]

              #顯示出刀與否記號
              done_time = row[3]
              if done_time:
                comment = '實際傷害:' + format(row[4],',')
                knife_status = "V "
              else:
                knife_status = "X "

              knife_msg = knife_msg + '  {' +str(index) + '} ' + knife_status + nick_name + '(' + comment + ')\n'
              row = cursor.fetchone()
              index = index +1
            cursor.close()
            title_msg = ' ' + str(j) + '王(' + str(Module.Kernel.define_value.BOSS_HP[week_stage][j-1] - estimated_sum_damage) + '/' + str(Module.Kernel.define_value.BOSS_HP[week_stage][j-1]) + ')\n'
          
          week_msg = week_msg + title_msg + knife_msg  
        send_msg = send_msg + '第' + str(i) + '週目:\n' + week_msg    
      send_msg = send_msg + '```'
            
      # 取得訊息物件
      try:
        guild = Module.Kernel.Discord_client.bot.get_guild(server_id)
        channel = guild.get_channel(table_channel_id)
        message_obj = await channel.fetch_message(table_message_id)
        await message_obj.edit(content = send_msg)
      except:
        await send_obj.send(content='刀表訊息已被移除，請重新設定刀表頻道!')

      # 保留刀部分
      # 從一王印到五王
      # 刀表SQL
      cursor = connection.cursor(prepared=True)
      sql = "SELECT member_id, comment FROM princess_connect.keep_knifes WHERE server_id = ? and group_serial = ? order by serial_number"
      data = (server_id, group_serial)
      cursor.execute(sql, data)
      msg = '```asciidoc\n保留刀:\n'
      index = 1
      row = cursor.fetchone()
      while row:  
        # {index} nickname\tcomment\n
        name = await Module.Kernel.Name_manager.get_nick_name(server_id, row[0])
        msg = msg + '{' +str(index) + '} ' + name + '\t' + row[1] + '\n'
        index = index + 1
        row = cursor.fetchone()
      cursor.close

      # 取得訊息物件
      try:
        guild = Module.Kernel.Discord_client.bot.get_guild(server_id)
        channel = guild.get_channel(table_channel_id)
        message_obj = await channel.fetch_message(knife_pool_message_id)
        if msg == '```asciidoc\n保留刀:\n':
          await message_obj.edit(content = '尚無保留刀資訊!')
        else:
          msg = msg + '```'
          await message_obj.edit(content = msg)
      except:
        await send_obj.send(content='保留區訊息已被移除，請重新設定刀表頻道!')

    else:
      await send_obj.send(content='請戰隊隊長設定刀表頻道!')
  else:
    await send_obj.send(content='查無戰隊資料!')