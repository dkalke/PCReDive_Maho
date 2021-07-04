import os
import mysql.connector
from mysql.connector import Error

async def OpenConnection(message):
  connection = mysql.connector.connect(host=os.getenv('SQLHOST'), database=os.getenv('SQLDB'), user=os.getenv('SQLID'), password=os.getenv('SQLPW'))
  if connection.is_connected():
    return connection
  else:
    await message.channel.send('資料庫連線失敗!')
    return None

async def CloseConnection(connection, message):
  if connection.is_connected():
    connection.close
    return True
  else:
    await message.channel.send('連線不存在!!')
    return False
