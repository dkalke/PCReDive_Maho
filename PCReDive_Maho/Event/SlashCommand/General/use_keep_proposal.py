from discord_slash.utils.manage_commands import create_option, create_choice
import Module.Kernel.Discord_client
import Module.Kernel.DB_control
import Module.Kernel.check_boss
import Module.Kernel.check_week

@Module.Kernel.Discord_client.slash.slash( 
             name="ukp" ,
             description="使用保留刀",
             options= [
                create_option(
                     name="序號",
                     description="請查看保留區，填入該刀在保留區中的序號",
                     option_type=4,
                     required=True
                 ),
                 create_option(
                     name="週目",
                     description="要用在哪一週目?",
                     option_type=4,
                     required=True
                 ),
                 create_option(
                     name="boss",
                     description="要打哪一隻王?",
                     option_type=4,
                     required=True,
                     choices=[
                         create_choice(name="1", value=1),create_choice(name="2", value=2),create_choice(name="3", value=3),
                         create_choice(name="4", value=4),create_choice(name="5", value=5)
                     ]
                 ),
                 create_option(
                     name="預估傷害",
                     description="單位為\'萬\'，預估能打出的傷害",
                     option_type=4,
                     required=False
                 )
             ],
             connector={"序號": "index", "週目": "week", "boss": "boss", "預估傷害":"estimated_damage"}
             )
async def use_keep_proposal(ctx, index, week, boss, **kwargs):
  connection = await Module.Kernel.DB_control.OpenConnection(ctx)
  if connection:
    cursor = connection.cursor(prepared=True)
    sql = "SELECT  now_week, now_week_1, now_week_2, now_week_3, now_week_4, now_week_5, week_offset, group_serial FROM princess_connect.group WHERE server_id = ? and sign_channel_id = ? order by group_serial limit 0, 1"
    data = (ctx.guild.id, ctx.channel.id)
    cursor.execute(sql, data) # 認證身分
    row = cursor.fetchone()
    cursor.close
    if row:
      group_serial = row[7]
      if Module.Kernel.check_week.Check_week((row[0], row[6]), week):
        if Module.Kernel.check_boss.Check_boss((row[1], row[2], row[3], row[4], row[5]), week, boss):  
          try:
            estimated_damage = kwargs["estimated_damage"]
          except KeyError as e:
            estimated_damage = 0
          if not (Module.Kernel.week_stage.week_stage(week) == 4 and estimated_damage == 0):
            # 檢查有無溢傷
            cursor = connection.cursor(prepared=True)
            sql = "SELECT SUM(estimated_damage) from knifes WHERE server_id = ? and group_serial = ? and week = ? and boss = ?"
            data = (ctx.guild.id, group_serial, week, boss)
            cursor.execute(sql, data)
            row = cursor.fetchone()
            cursor.close
            sum_estimated_damage = 0
            if row[0]:
              sum_estimated_damage = int(row[0])
            if (Module.Kernel.define_value.BOSS_HP[Module.Kernel.week_stage.week_stage(week)][boss-1] - sum_estimated_damage) > 0:
              if index > 0:
                # 尋找指定刀資訊
                cursor = connection.cursor(prepared=True)
                sql = "SELECT serial_number, member_id, comment from princess_connect.keep_knifes where server_id=? and group_serial=? order by serial_number limit ?,1"
                data = (ctx.guild.id, group_serial, index-1)
                cursor.execute(sql, data)
                row = cursor.fetchone()
                cursor.close()
                if row:
                  if ctx.author.id == row[1]:
                    # 新增刀
                    cursor = connection.cursor(prepared=True)
                    sql = "INSERT INTO princess_connect.knifes (server_id, group_serial, week, boss, member_id, comment, estimated_damage) VALUES (?, ?, ?, ?, ?, ?, ?)"
                    data = (ctx.guild.id, group_serial, week, boss, row[1], row[2], estimated_damage)
                    cursor.execute(sql, data)
                    cursor.close

                    # 刪除刀
                    cursor = connection.cursor(prepared=True)
                    sql = "DELETE from princess_connect.keep_knifes where serial_number=?"
                    data = (row[0],)
                    cursor.execute(sql, data)
                    cursor.close()

                    connection.commit()
                    await ctx.send('第' + str(week) + '週目' + str(boss) + '王，備註:' + row[2] + '，報刀成功!')
                    await Module.Kernel.Update.Update(ctx, ctx.guild.id, group_serial) # 更新刀表
                  else:
                    await ctx.send('您並非該刀主人喔!')
                else:
                  await ctx.send('該刀不存在喔!')
              else:
                await ctx.send('序號必須大於0!')
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
    await Module.Kernel.DB_control.CloseConnection(connection, ctx)