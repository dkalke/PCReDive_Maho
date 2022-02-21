import datetime
from discord_slash.utils.manage_commands import create_option, create_choice
import Discord_client
import Module.DB_control
import Module.Authentication
import Module.Update
import Module.Offset_manager
import Module.get_closest_end_time


@Discord_client.slash.subcommand( base="captain",
                                  name="set_force_status" ,
                                  description="強制修改成員出刀狀態",
                                  options=[
                                    create_option(
                                        name="序號",
                                        description="請查看資訊表，輸入要修改的序號",
                                        option_type=4,
                                        required=True
                                    ),
                                    create_option(
                                        name="剩餘正刀數",
                                        description="本日剩餘正刀數量",
                                        option_type=4,
                                        required=True,
                                        choices=[
                                            create_choice(name="0", value=0), create_choice(name="1", value=1),create_choice(name="2", value=2),create_choice(name="3", value=3)
                                        ]
                                    ),
                                    create_option(
                                        name="剩餘補償數",
                                        description="本日剩餘補償數量",
                                        option_type=4,
                                        required=True,
                                        choices=[
                                            create_choice(name="0", value=0), create_choice(name="1", value=1),create_choice(name="2", value=2),create_choice(name="3", value=3)
                                        ]
                                    )
                                  ],
                                  connector={"序號": "index","剩餘正刀數": "normal","剩餘補償數": "reversed"}
                                )
async def force_set_status(ctx, index, normal, reversed):
  connection = await Module.DB_control.OpenConnection(ctx)
  if connection:
    row = await Module.Authentication.IsCaptain(ctx, "/captain set_weeks_offset", connection, ctx.guild.id, ctx.author.id)
    if row:
      group_serial = row[0]
      if await Module.Authentication.IsSignChannel(ctx,connection,group_serial):
        start_time = Module.get_closest_end_time.get_closest_end_time(datetime.datetime.now()) - datetime.timedelta(days = 1)
        # 寫入資料庫
        cursor = connection.cursor(prepared=True)
        sql = "SELECT a.serial_number \
        FROM princess_connect.members a\
        LEFT JOIN princess_connect.knife_summary b ON a.serial_number = b.serial_number and day = ?\
        WHERE server_id = ?  and group_serial = ? LIMIT ?, 1"
        data = (start_time, ctx.guild.id, group_serial, index - 1)
        cursor.execute(sql, data)
        row = cursor.fetchone()
        if row:
          sql = "INSERT INTO princess_connect.knife_summary VALUES (?, ?, ?, ?) ON DUPLICATE KEY UPDATE normal = ?, reserved = ?"
          data = (row[0], start_time, normal, reversed, normal, reversed)
          cursor.execute(sql, data)
          
          connection.commit()
          await ctx.send('已強制更新序號:{}，正刀剩餘:{}，補償剩餘:{}!'.format(index, normal, reversed))
          await Module.info_update.info_update(ctx ,ctx.guild.id, group_serial)
        else:
          await ctx.send("該序號不存在，請再次確認!")
        cursor.close

    await Module.DB_control.CloseConnection(connection, ctx)