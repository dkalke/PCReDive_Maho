import datetime
from discord_slash.utils.manage_commands import create_option, create_choice
import Discord_client
import Module.DB_control
import Module.Update
import Module.info_update
import Module.define_value

@Discord_client.slash.slash( 
             name="ds" ,
             description="不報刀，出刀後直接回報傷害。",
             options= [
                 create_option(
                     name="週目",
                     description="填入本刀的週目",
                     option_type=4,
                     required=True
                 ),
                 create_option(
                     name="boss",
                     description="填入本刀的王",
                     option_type=4,
                     required=True,
                     choices=[
                         create_choice(name="1", value=1),create_choice(name="2", value=2),create_choice(name="3", value=3),
                         create_choice(name="4", value=4),create_choice(name="5", value=5)
                     ]
                 ),
                 create_option(
                     name="類型",
                     description="是正刀、尾刀、還是補償刀?",
                     option_type=4,
                     required=True,
                     choices=[
                         create_choice(name="正刀", value=1),create_choice(name="尾刀", value=2),create_choice(name="補償刀", value=3)
                         # value = 0 為一般報刀使用，無法統計刀數
                         # 尾刀出完扣除0.5
                         # 補償刀出完扣除0.5
                     ]
                 ),
                  create_option(
                     name="傷害",
                     description="實際打了多少血，僅能輸入數字",
                     option_type=4,
                     required=True
                 )
             ],
             connector={"週目":"week", "boss":"boss", "類型": "knife_type", "傷害": "real_damage"}
             )
async def done_skip_proposal(ctx, week, boss, knife_type, real_damage):
  connection = await Module.DB_control.OpenConnection(ctx)
  if connection:
    cursor = connection.cursor(prepared=True)
    sql = "SELECT now_week, now_week_1, now_week_2, now_week_3, now_week_4, now_week_5, week_offset, group_serial, policy FROM princess_connect.group WHERE server_id = ? and sign_channel_id = ? order by group_serial limit 0, 1"
    data = (ctx.guild.id, ctx.channel.id)
    cursor.execute(sql, data) # 認證身分
    row = cursor.fetchone()
    cursor.close
    if row:
      now_week = row[0]
      group_serial = row[7]
      policy = row[8]
      if policy == Module.define_value.Policy.YES.value:
        if 0 <= real_damage and real_damage <= Module.define_value.MAX_DAMAGE:
          if Module.check_week.Check_week((now_week, row[6]), week):
            if Module.check_boss.Check_boss((row[1], row[2], row[3], row[4], row[5]), week, boss):
              # 新增刀
              cursor = connection.cursor(prepared=True)
              sql = "INSERT INTO princess_connect.knifes (server_id, group_serial, week, boss, member_id, comment, knife_type, real_damage, done_time) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)"
              data = (ctx.guild.id, group_serial, week, boss, ctx.author.id, '直接出刀並回報傷害',knife_type, real_damage, datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
              cursor.execute(sql, data)
              cursor.close
              connection.commit()
              await ctx.send('第' + str(week) + '週目' + str(boss) + '王，實際傷害:' + format(real_damage,",") + '，回報成功!')
              await Module.Update.Update(ctx, ctx.guild.id, group_serial) # 更新刀表
              await Module.info_update.info_update(ctx ,ctx.guild.id, group_serial) # 更新資訊
            else:
              await ctx.send('該王不存在喔!')
          else:
            await ctx.send('該週目不存在喔!')
        else:
          await message.channel.send('傷害異常，目前最高僅能紀載0至' + str(Module.define_value.MAX_DAMAGE) + '!')
      else:
        await ctx.send('目前戰隊政策為:**不回報傷害**! 指令無效，感謝你的自主回報!')
    else:
      await ctx.send('這裡不是報刀頻道喔!')
    await Module.DB_control.CloseConnection(connection, ctx)