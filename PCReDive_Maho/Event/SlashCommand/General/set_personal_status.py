import datetime
from discord_slash.utils.manage_commands import create_option, create_choice
import Discord_client
import Module.DB_control
import Module.check_boss
import Module.check_week
import Module.Update
import Module.week_stage
import Module.define_value
import Module.get_closest_end_time

@Discord_client.slash.slash( 
             name="f" ,
             description="出刀狀態設定",
             options= [
                 create_option(
                     name="已出正刀數",
                     description="本日已出刀數",
                     option_type=4,
                     required=True,
                     choices=[
                         create_choice(name="0", value=0), create_choice(name="1", value=1),create_choice(name="2", value=2),create_choice(name="3", value=3)
                     ]
                 ),
                 create_option(
                     name="剩餘補償數",
                     description="本日剩餘補償數",
                     option_type=4,
                     required=True,
                     choices=[
                         create_choice(name="0", value=0), create_choice(name="1", value=1),create_choice(name="2", value=2),create_choice(name="3", value=3)
                     ]
                 )
             ],
             connector={"已出正刀數": "normal","剩餘補償數": "reversed"}
             )
async def set_personal_status(ctx, normal, reversed):
  connection = await Module.DB_control.OpenConnection(ctx)
  if connection:
    cursor = connection.cursor(prepared=True)
    sql = "SELECT now_week, now_week_1, now_week_2, now_week_3, now_week_4, now_week_5, week_offset, group_serial FROM princess_connect.group WHERE server_id = ? and sign_channel_id = ? order by group_serial limit 0, 1"
    data = (ctx.guild.id, ctx.channel.id)
    cursor.execute(sql, data) # 認證身分
    row = cursor.fetchone()
    if row:
      group_serial = row[7]
      # 取得正在使用的帳號
      sql = "SELECT serial_number FROM princess_connect.members WHERE now_using = '1' and server_id = ? and group_serial = ? and member_id = ? LIMIT 0, 1"
      data = (ctx.guild.id, group_serial, ctx.author.id)
      cursor.execute(sql, data)
      row = cursor.fetchone()
      if row:
        sql = "INSERT INTO princess_connect.knife_summary VALUES (?, ?, ?, ?) ON DUPLICATE KEY UPDATE normal = ?, reserved = ?"
        data = (row[0], Module.get_closest_end_time.get_closest_end_time(datetime.datetime.now()) - datetime.timedelta(days = 1), normal, reversed, normal, reversed)
        cursor.execute(sql, data)
        connection.commit() # 資料庫存檔
        await ctx.send('更新完成，正刀已出:{}，補償剩餘:{}!'.format(normal, reversed))
        await Module.info_update.info_update(ctx ,ctx.guild.id, group_serial)
      else:
        await ctx.send('找不到你的資料，請通知戰隊隊長協助加入戰隊名單!')
      cursor.close()

    else:
      await ctx.send('這裡不是報刀頻道喔!')
    await Module.DB_control.CloseConnection(connection, ctx)