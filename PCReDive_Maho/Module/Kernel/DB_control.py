import os
import mysql.connector
from mysql.connector import Error

async def OpenConnection(send_obj):
  connection = mysql.connector.connect(host=os.getenv('SQLHOST'), port=os.getenv('SQLPORT'), database=os.getenv('SQLDB'), user=os.getenv('SQLID'), password=os.getenv('SQLPW'))
  if connection.is_connected():
    return connection
  else:
    if not send_obj == None:
      await send_obj.send('資料庫連線失敗!')
    else:
      print('資料庫連線失敗!')
    return None

async def CloseConnection(connection, send_obj):
  if connection.is_connected():
    connection.close
    return True
  else:
    print('連線不存在!!')
    return False