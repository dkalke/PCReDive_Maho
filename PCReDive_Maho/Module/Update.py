import os
import mysql.connector
from discord import Embed
import Discord_client
import Name_manager

async def Update(message ,server_id, group_serial):
  connection = mysql.connector.connect(host=os.getenv('SQLHOST'), database=os.getenv('SQLDB'), user=os.getenv('SQLID'), password=os.getenv('SQLPW'))
  if connection.is_connected():
    cursor = connection.cursor(prepared=True)
    sql = "SELECT table_style FROM princess_connect.group WHERE server_id = ? and group_serial = ? LIMIT 0, 1"
    data = (server_id, group_serial)
    cursor.execute(sql, data)
    row = cursor.fetchone()
    cursor.close
    if row:
      if row[0] == 0:
        await UpdateEmbed(message, server_id, group_serial)
      else:
        await UpdateTraditional(message, server_id, group_serial)
    else:
      await message.channel.send(content='查無戰隊資料!')
    connection.close # 關閉連線
  
async def UpdateEmbed(message, server_id, group_serial): # 更新刀表
  try:
    # 查詢當前周目、王、刀表訊息、保留刀訊息
    connection = mysql.connector.connect(host=os.getenv('SQLHOST'), database=os.getenv('SQLDB'), user=os.getenv('SQLID'), password=os.getenv('SQLPW'))
    if connection.is_connected():
      cursor = connection.cursor(prepared=True)
      sql = "SELECT now_week, week_offset, now_boss, table_channel_id, table_message_id, knife_pool_message_id FROM princess_connect.group WHERE server_id = ? and group_serial = ? LIMIT 0, 1"
      data = (server_id, group_serial)
      cursor.execute(sql, data)
      row = cursor.fetchone()
      cursor.close
      if row:
        now_week = row[0]
        week_offset = row[1]
        now_boss = row[2]
        table_channel_id = row[3]
        table_message_id = row[4]
        knife_pool_message_id = row[5]

        if table_message_id:
          embed_msg = Embed(title='第' + str(group_serial) + '戰隊刀表', color=0xD98B99)
          # 刀表部分，從當前週目開始印
          send_msg = ''
          index_boss = now_boss # 僅第一個週目由此王開始
          for i in range(now_week, now_week + week_offset + 1):
            kinfe_msg_name = ''
            for j in range(index_boss,6):              
              if i == now_week and j == now_boss:
                kinfe_msg_name = kinfe_msg_name + '**'+ str(j) + '王(現在進度)**\n'  # TODO
              else:
                kinfe_msg_name = kinfe_msg_name + '**'+ str(j) + '王**\n'  # TODO
  
              # 刀表SQL
              cursor = connection.cursor(prepared=True)
              sql = "SELECT member_id, comment FROM princess_connect.knifes WHERE server_id = ? and group_serial = ? and week = ? and boss = ? order by serial_number"
              data = (server_id, group_serial,i ,j)
              cursor.execute(sql, data)
              row = cursor.fetchone()
              index = 1
              while row:
                nick_name = await Name_manager.get_nick_name(message, row[0])
                kinfe_msg_name = kinfe_msg_name + '　{' +str(index) + '} ' + nick_name + '\n　　' +row[1] + '\n'
                row = cursor.fetchone()
                index = index +1
              cursor.close()
            index_boss = 1
            embed_msg.add_field(name='\u200b', value='-   -   -   -   -   -   -   -   ', inline=False)
            embed_msg.add_field(name='第' + str(i) + '週目', value=kinfe_msg_name , inline=False)
            
  
          
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
          sql = "SELECT boss, member_id, comment FROM princess_connect.keep_knifes WHERE server_id = ? and group_serial = ? order by boss"
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
      connection.close # 關閉連線
    else:
      await message.channel.send(content='資料庫連線失敗!')
  except Error as e:
    print("資料庫連接失敗：", e)
  finally:
    if (connection.is_connected()):
        cursor.close()
        connection.close()
        print("資料庫連線已關閉")

async def UpdateTraditional(message, server_id, group_serial): # 更新刀表
  try:
    # 查詢當前周目、王、刀表訊息、保留刀訊息
    connection = mysql.connector.connect(host=os.getenv('SQLHOST'), database=os.getenv('SQLDB'), user=os.getenv('SQLID'), password=os.getenv('SQLPW'))
    if connection.is_connected():
      cursor = connection.cursor(prepared=True)
      sql = "SELECT now_week, week_offset, now_boss, table_channel_id, table_message_id, knife_pool_message_id FROM princess_connect.group WHERE server_id = ? and group_serial = ? LIMIT 0, 1"
      data = (server_id, group_serial)
      cursor.execute(sql, data)
      row = cursor.fetchone()
      cursor.close
      if row:
        now_week = row[0]
        week_offset = row[1]
        now_boss = row[2]
        table_channel_id = row[3]
        table_message_id = row[4]
        knife_pool_message_id = row[5]

        if table_message_id:
          # 刀表部分，從當前週目開始印
          send_msg = '```asciidoc\n'
          index_boss = now_boss # 僅第一個週目由此王開始
          for i in range(now_week, now_week + week_offset + 1):
            send_msg = send_msg + '第' + str(i) + '週目:\n'
            for j in range(index_boss,6):
              msg = ''

              # 刀表SQL
              cursor = connection.cursor(prepared=True)
              sql = "SELECT member_id, comment FROM princess_connect.knifes WHERE server_id = ? and group_serial = ? and week = ? and boss = ? order by serial_number"
              data = (server_id, group_serial,i ,j)
              cursor.execute(sql, data)
              row = cursor.fetchone()
              index = 1
              while row:
                nick_name = await Name_manager.get_nick_name(message, row[0])
                msg = msg + '  {' +str(index) + '}' + nick_name + '(' + row[1] + '),\n'
                row = cursor.fetchone()
                index = index +1
              cursor.close()
              if i == now_week and j == now_boss:
                if msg == '':
                  send_msg = send_msg + ' ' + str(j) + '王(當前周目)\n'
                else:
                  send_msg = send_msg + ' ' + str(j) + '王(當前周目)\n' + msg + '\n'  
              else:
                if msg == '':
                  send_msg = send_msg + ' ' + str(j) + '王\n'
                else:
                  send_msg = send_msg + ' ' + str(j) + '王\n' + msg + '\n'  
            index_boss = 1

          
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
          sql = "SELECT boss, member_id, comment FROM princess_connect.keep_knifes WHERE server_id = ? and group_serial = ? order by boss"
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

      connection.close # 關閉連線
    else:
      await message.channel.send(content='資料庫連線失敗!')
  except Error as e:
    print("資料庫連接失敗：", e)
  finally:
    if (connection.is_connected()):
        cursor.close()
        connection.close()
        print("資料庫連線已關閉")