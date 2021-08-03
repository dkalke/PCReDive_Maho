import os
import csv
import datetime
import discord
import Discord_client
import Name_manager
import Module.DB_control
import Module.Authentication

@Discord_client.slash.subcommand( base="captain",
                                  name="export_table" ,
                                  description="匯出csv刀表",                                 
                                )
async def export_table(ctx):
  connection = await Module.DB_control.OpenConnection(ctx)
  if connection:
    row = await Module.Authentication.IsCaptain(ctx ,'/captain export_table', connection, ctx.guild.id, ctx.author.id)
    if row:
      group_serial = row[0]
      server_id = ctx.guild.id
            
      msg = [['序號', '週目', 'BOSS', '隊員識別碼', '隊員姓名', '備註', '時間']]

      # 獲取刀表
      cursor = connection.cursor(prepared=True)
      sql = "SELECT member_id, week, boss, comment, timestamp FROM princess_connect.knifes WHERE server_id = ? and group_serial = ? order by week, boss, serial_number"
      data = (server_id, group_serial)
      cursor.execute(sql, data)
      row = cursor.fetchone()
      index = 1
      while row:
        nick_name = await Name_manager.get_nick_name(ctx, row[0])
        msg.append([index,row[1] ,row[2] ,row[0] ,nick_name, row[3], row[4]])
        row = cursor.fetchone()
        index = index +1
      cursor.close()
            
      filename = datetime.datetime.now().strftime("%Y%m%d%H%M%S") + '_' + str(server_id) + '_request.csv' # 檔案名稱

      # 寫檔
      with open(filename, 'w', newline='', encoding='utf-8-sig') as csvfile:
        writer = csv.writer(csvfile) # 建立 CSV 檔寫入器
        writer.writerows(msg) # 寫入欄位

      # 傳送私人訊息
      await ctx.author.send('咕嚕靈波，你要的刀表來囉!')
      await ctx.defer()
      await ctx.author.send(file=discord.File(filename))
      await ctx.send('刀表匯出成功!')

      os.remove(filename) # 移除檔案

    await Module.DB_control.CloseConnection(connection, ctx)