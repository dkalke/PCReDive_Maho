import Module.Kernel.Discord_client
import Module.Kernel.DB_control
import Module.Kernel.Name_manager

@Module.Kernel.Discord_client.slash.slash( 
             name="leave" ,
             description="離開該頻道所屬戰隊。",
             )
async def leave(ctx):
  # check頻道，並找出所屬組別
  connection = await Module.Kernel.DB_control.OpenConnection(ctx)
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
      if row:
        # 自成員名單中移除，一併並刪除分身
        sql = "DELETE FROM princess_connect.members where server_id = ? and group_serial = ? and member_id =?"
        data = (ctx.guild.id, group_serial, ctx.author.id)
        cursor.execute(sql, data)
        
        connection.commit() # 資料庫存檔
        await ctx.send( ctx.author.name + ' 已退出第' + str(group_serial) + '戰隊。')
        await Module.Kernel.info_update.info_update(ctx ,ctx.guild.id, group_serial)
      else:
        await ctx.send( ctx.author.name + ' 你不是第' + str(group_serial) + '戰隊成員喔。')
    cursor.close
    await Module.Kernel.DB_control.CloseConnection(connection, ctx)