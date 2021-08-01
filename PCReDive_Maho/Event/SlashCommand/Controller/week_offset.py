import discord_slash
import Discord_client
from discord_slash.utils.manage_commands import create_option, create_choice
import Module.DB_control
import Module.Authentication
import Module.Update
import Module.Offset_manager

@Discord_client.slash.slash(name="提前週目數設定" ,
             description="設定各段可提前的週目數。",
             options=[
               create_option(
                 name="level1",
                 description="輸入第一階段可提前週目數。",
                 option_type=4,
                 required=True,
                 choices=[
                  create_choice(name="不提前", value=0),create_choice(name="提前1個週目", value=1),create_choice(name="提前2個週目", value=2),create_choice(name="提前3個週目", value=3),create_choice(name="提前4個週目", value=4),create_choice(name="提前5個週目", value=5),
                  create_choice(name="提前6個週目", value=6),create_choice(name="提前7個週目", value=7),create_choice(name="提前8個週目", value=8),create_choice(name="提前9個週目", value=9),create_choice(name="提前10個週目", value=10)
                  ]
               ),
               create_option(
                 name="level2",
                 description="輸入第二階段可提前週目數。",
                 option_type=4,
                 required=True,
                 choices=[
                  create_choice(name="不提前", value=0),create_choice(name="提前1個週目", value=1),create_choice(name="提前2個週目", value=2),create_choice(name="提前3個週目", value=3),create_choice(name="提前4個週目", value=4),create_choice(name="提前5個週目", value=5),
                  create_choice(name="提前6個週目", value=6),create_choice(name="提前7個週目", value=7),create_choice(name="提前8個週目", value=8),create_choice(name="提前9個週目", value=9),create_choice(name="提前10個週目", value=10)
                 ]
               ),
               create_option(
                 name="level3",
                 description="輸入第三階段可提前週目數。",
                 option_type=4,
                 required=True,
                 choices=[
                  create_choice(name="不提前", value=0),create_choice(name="提前1個週目", value=1),create_choice(name="提前2個週目", value=2),create_choice(name="提前3個週目", value=3),create_choice(name="提前4個週目", value=4),create_choice(name="提前5個週目", value=5),
                  create_choice(name="提前6個週目", value=6),create_choice(name="提前7個週目", value=7),create_choice(name="提前8個週目", value=8),create_choice(name="提前9個週目", value=9),create_choice(name="提前10個週目", value=10)
                  ]
               ),
               create_option(
                 name="level4",
                 description="輸入第四階段可提前週目數。",
                 option_type=4,
                 required=True,
                 choices=[
                  create_choice(name="不提前", value=0),create_choice(name="提前1個週目", value=1),create_choice(name="提前2個週目", value=2),create_choice(name="提前3個週目", value=3),create_choice(name="提前4個週目", value=4),create_choice(name="提前5個週目", value=5),
                  create_choice(name="提前6個週目", value=6),create_choice(name="提前7個週目", value=7),create_choice(name="提前8個週目", value=8),create_choice(name="提前9個週目", value=9),create_choice(name="提前10個週目", value=10)
                  ]
               ),
               create_option(
                 name="level5",
                 description="輸入第五階段可提前週目數。",
                 option_type=4,
                 required=True,
                 choices=[
                  create_choice(name="不提前", value=0),create_choice(name="提前1個週目", value=1),create_choice(name="提前2個週目", value=2),create_choice(name="提前3個週目", value=3),create_choice(name="提前4個週目", value=4),create_choice(name="提前5個週目", value=5),
                  create_choice(name="提前6個週目", value=6),create_choice(name="提前7個週目", value=7),create_choice(name="提前8個週目", value=8),create_choice(name="提前9個週目", value=9),create_choice(name="提前10個週目", value=10)
                  ]
               )
             ])
async def weekset(ctx, level1, level2, level3, level4, level5):
  connection = await Module.DB_control.OpenConnection(ctx)
  group_serial = await Module.Authentication.IsCaptain(ctx, "/提前週目數設定", connection, ctx.guild.id, ctx.author.id)
  group_serial = group_serial[0]
  # 寫入資料庫
  cursor = connection.cursor(prepared=True)
  sql = "UPDATE princess_connect.group SET week_offset_1 = ?, week_offset_2 = ?,week_offset_3 = ?,week_offset_4 = ?,week_offset_5 = ? WHERE server_id = ? and group_serial = ? "
  data = (level1, level2, level3, level4, level5, ctx.guild.id, group_serial)
  cursor.execute(sql, data)
  cursor.close
  connection.commit()
  await ctx.send(f"第{group_serial}戰隊提前週目設置如下\n第1階段:提前{level1}週目\n第2階段:提前{level2}週目\n第3階段:提前{level3}週目\n第4階段:提前{level4}週目\n第5階段:提前{level5}週目")
  await Module.DB_control.CloseConnection(connection, ctx)                
  # 動態調整週目
  Module.Offset_manager.AutoOffset(connection, ctx.guild.id, group_serial)
  await Module.Update.Update(ctx, ctx.guild.id, group_serial)
