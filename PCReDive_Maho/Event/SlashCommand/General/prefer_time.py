from discord_slash.utils.manage_commands import create_option, create_choice
import Module.Kernel.Discord_client
import Module.Kernel.define_value
import Module.Kernel.DB_control
import Module.Kernel.info_update

@Module.Kernel.Discord_client.slash.slash( 
             name="prefer_time" ,
             description="設定自己的偏好出刀時段",
             options= [
                 create_option(
                     name="時段",
                     description="選擇偏好的出刀時段",
                     option_type=4,
                     required=True,
                     choices=[
                         create_choice(name="不定??-??", value=Module.Kernel.define_value.Period.UNKNOW.value),create_choice(name="日班08-16", value=Module.Kernel.define_value.Period.DAY.value),
                         create_choice(name="晚班16-24", value=Module.Kernel.define_value.Period.NIGHT.value),create_choice(name="夜班00-08", value=Module.Kernel.define_value.Period.GRAVEYARD.value),
                         create_choice(name="全日00-24", value=Module.Kernel.define_value.Period.ALL.value)
                     ]
                 )
             ],
             connector={"時段": "period"}
             )
async def proposal_knife(ctx, period):
  connection = await Module.Kernel.DB_control.OpenConnection(ctx)
  if connection:
    cursor = connection.cursor(prepared=True)
    sql = "SELECT group_serial FROM princess_connect.group WHERE server_id = ? and sign_channel_id = ? order by group_serial limit 0, 1"
    data = (ctx.guild.id, ctx.channel.id)
    cursor.execute(sql, data) # 認證身分
    row = cursor.fetchone()
    cursor.close
    if row:
      group_serial = row[0]

      # 檢查使否屬於該戰隊
      cursor = connection.cursor(prepared=True)
      sql = "select * from princess_connect.members WHERE server_id = ? and group_serial = ? and member_id = ? limit 0,1"
      data = (ctx.guild.id, group_serial, ctx.author.id)
      cursor.execute(sql, data)
      row = cursor.fetchone()
      if row:
        # 修改出刀偏好
        cursor = connection.cursor(prepared=True)
        sql = "update princess_connect.members SET period=? WHERE server_id = ? and group_serial = ? and member_id = ?"
        data = (period, ctx.guild.id, group_serial, ctx.author.id)
        cursor.execute(sql, data)
        connection.commit()
        await Module.Kernel.info_update.info_update(ctx ,ctx.guild.id, group_serial)
        await ctx.send('您在第' + str(group_serial) + '戰隊的出刀偏好時段已修改完成!')
      else:
        await ctx.send('您不屬於第' + str(group_serial) + '戰隊喔!')
    else:
      await ctx.send('這裡不是報刀頻道喔，請在所屬戰隊報刀頻道使用!')
    await Module.Kernel.DB_control.CloseConnection(connection, ctx)