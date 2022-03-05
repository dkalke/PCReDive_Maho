import Module.Kernel.Discord_client
import Module.Kernel.DB_control

@Module.Kernel.Discord_client.slash.slash( 
             name="ns" ,  # TODO: 舊版為ns(now_schedule)，考慮改成np(now_progress)比較適合?
             description="顯示目前進度!",
             )
async def now_progeass(ctx):      
  connection = await Module.Kernel.DB_control.OpenConnection(ctx)
  if connection:
    cursor = connection.cursor(prepared=True)
    sql = "SELECT now_week, now_boss, group_serial FROM princess_connect.group WHERE server_id = ? and sign_channel_id = ? limit 0, 1"
    data = (ctx.guild.id, ctx.channel.id)
    cursor.execute(sql, data) # check頻道，並找出所屬組別
    row = cursor.fetchone()
    cursor.close()
    if row:
      await ctx.send('目前進度' + str(row[0]) + '週' + str(row[1]) + '王!')
    else:
      await ctx.send('這裡不是報刀頻道喔!')

    await Module.Kernel.DB_control.CloseConnection(connection, ctx)