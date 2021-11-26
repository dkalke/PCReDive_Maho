from discord_slash.utils.manage_commands import create_option, create_choice
import Discord_client
import Module.DB_control
import Module.check_boss
import Module.check_week
import Module.Update
import Module.week_stage
import Module.define_value

@Discord_client.slash.slash( 
             name="p" ,
             description="預約打王",
             options= [
                 create_option(
                     name="週目",
                     description="填入要預約的週目",
                     option_type=4,
                     required=True
                 ),
                 create_option(
                     name="boss",
                     description="填入要打的王",
                     option_type=4,
                     required=True,
                     choices=[
                         create_choice(name="1", value=1),create_choice(name="2", value=2),create_choice(name="3", value=3),
                         create_choice(name="4", value=4),create_choice(name="5", value=5)
                     ]
                 ),
                 create_option(
                     name="備註",
                     description="備註",
                     option_type=3,
                     required=True
                 ),
                 create_option(
                     name="預估傷害",
                     description="單位為\'萬\'，預估能打出的傷害",
                     option_type=4,
                     required=False
                 )
             ],
             connector={"週目": "week","boss": "boss","備註": "comment","預估傷害":"estimated_damage"}
             )
async def proposal_knife(ctx, week, boss, comment, **kwargs):
  connection = await Module.DB_control.OpenConnection(ctx)
  if connection:
    cursor = connection.cursor(prepared=True)
    sql = "SELECT now_week, now_week_1, now_week_2, now_week_3, now_week_4, now_week_5, week_offset, group_serial FROM princess_connect.group WHERE server_id = ? and sign_channel_id = ? order by group_serial limit 0, 1"
    data = (ctx.guild.id, ctx.channel.id)
    cursor.execute(sql, data) # 認證身分
    row = cursor.fetchone()
    cursor.close
    if row:
      group_serial = row[7]
      if Module.check_week.Check_week((row[0], row[6]), week):
        if Module.check_boss.Check_boss((row[1], row[2], row[3], row[4], row[5]), week, boss):
          try:
            estimated_damage = kwargs["estimated_damage"]
          except KeyError as e:
            estimated_damage = 0
          if not (Module.week_stage.week_stage(week) == 4 and estimated_damage == 0):
            # 新增刀
            cursor = connection.cursor(prepared=True)
            sql = "SELECT SUM(estimated_damage) from knifes WHERE server_id = ? and group_serial = ? and week = ? and boss = ?"
            data = (ctx.guild.id, group_serial, week, boss)
            cursor.execute(sql, data)
            row = cursor.fetchone()
            cursor.close
            sum_estimated_damage = 0
            if row[0]:
              sum_estimated_damage = int(row[0])
            if (Module.define_value.BOSS_HP[Module.week_stage.week_stage(week)][boss-1] - sum_estimated_damage) > 0:
              cursor = connection.cursor(prepared=True)
              sql = "INSERT INTO princess_connect.knifes (server_id, group_serial, week, boss, member_id, comment, estimated_damage) VALUES (?, ?, ?, ?, ?, ?, ?)"
              data = (ctx.guild.id, group_serial, week, boss, ctx.author.id, comment, estimated_damage)
              cursor.execute(sql, data)
              cursor.close
              connection.commit()
              await ctx.send('第' + str(week) + '週目' + str(boss) + '王，備註:' + comment + '，報刀成功!')
              await Module.Update.Update(ctx, ctx.guild.id, group_serial) # 更新刀表
            else:
              await ctx.send('偵測到溢傷，請改報其他週目!')
          else:
            await ctx.send('發生錯誤，五階段報刀請填寫可選參數[預估傷害]，單位為萬!')
        else:
          await ctx.send('該王不存在喔!')
      else:
        await ctx.send('該週目不存在喔!')
    else:
      await ctx.send('這裡不是報刀頻道喔!')
    await Module.DB_control.CloseConnection(connection, ctx)