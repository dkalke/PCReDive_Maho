import Discord_client
import Module.DB_control
import Name_manager
import datetime

@Discord_client.slash.slash( 
             name="join" ,
             description="加入該頻道所屬戰隊。",
             )
async def join(ctx):
  # check頻道，並找出所屬組別
  connection = await Module.DB_control.OpenConnection(ctx)
  if connection:
    # 尋找該頻道所屬戰隊
    cursor = connection.cursor(prepared=True)
    sql = "SELECT group_serial FROM princess_connect.group WHERE server_id = ? and sign_channel_id = ?"
    data = (ctx.guild.id, ctx.channel.id)
    cursor.execute(sql, data)
    row = cursor.fetchone()
    if row:
      group_serial = row[0]
      # 檢查是否已經是該戰隊成員
      sql = "SELECT 1 FROM princess_connect.members WHERE server_id = ? and group_serial=? and member_id = ? and sockpuppet = '0'"
      data = (ctx.guild.id, group_serial, ctx.author.id)
      cursor.execute(sql, data)
      row = cursor.fetchone()
      if not row:
        # 寫入成員名單
        sql = "INSERT INTO princess_connect.members (server_id, group_serial, member_id, period, last_sl_time) VALUES (?, ?, ?, ?, ?)"
        data = (ctx.guild.id, group_serial, ctx.author.id, Module.define_value.Period.UNKNOW.value, datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
        cursor.execute(sql, data)
        
        connection.commit() # 資料庫存檔
        await ctx.send( ctx.author.name + ' 已新增為第' + str(group_serial) + '戰隊成員。')
        await Module.info_update.info_update(ctx ,ctx.guild.id, group_serial)
      else:
        await ctx.send( ctx.author.name + ' 目前已為第' + str(group_serial) + '戰隊成員。')
    cursor.close
    await Module.DB_control.CloseConnection(connection, ctx)