from discord import Embed
from discord_slash.utils.manage_commands import create_option, create_choice
import Module.Kernel.Discord_client
import Module.Kernel.DB_control
import Module.Kernel.Authentication

@Module.Kernel.Discord_client.slash.subcommand( base="captain",
                                  name="set_table_style" ,
                                  description="設定刀表樣式",
                                  options=[
                                    create_option(
                                      name="樣式",
                                      description="選擇樣式",
                                      option_type=4,
                                      required=True,
                                      choices=[
                                        create_choice(name="Embed新版樣式", value=0),
                                        create_choice(name="Text舊版樣式", value=1)
                                      ]
                                    )
                                  ],
                                  connector={"樣式": "style"}
                                )
async def set_table_style(ctx, style):
  connection = await Module.Kernel.DB_control.OpenConnection(ctx)
  if connection:
    server_id = ctx.guild.id
    row = await Module.Kernel.Authentication.IsCaptain(ctx ,'/captain set_table_style', connection, server_id, ctx.author.id)
    if row:
      group_serial = row[0]
      if await Module.Kernel.Authentication.IsSignChannel(ctx,connection,group_serial):
        # 查詢刀表訊息、保留刀訊息
        cursor = connection.cursor(prepared=True)
        sql = "SELECT table_channel_id, table_message_id, knife_pool_message_id FROM princess_connect.group WHERE server_id = ? and group_serial = ? LIMIT 0, 1"
        data = (server_id, group_serial)
        cursor.execute(sql, data)
        row = cursor.fetchone()
        cursor.close
        if row:
          table_channel_id = row[0]
          table_message_id = row[1]
          knife_pool_message_id = row[2]
          # 取得訊息物件並刪除
          try:
            channel = ctx.guild.get_channel(table_channel_id)
            if table_message_id:
              msg_obj = await channel.fetch_message(table_message_id)
              await msg_obj.delete()
            if knife_pool_message_id:
              msg_obj = await channel.fetch_message(knife_pool_message_id)
              await msg_obj.delete()
                    
            # 產生新訊息物件並寫入資料庫
            table_message = None
            knife_pool_message = None
            if style == 0:
              embed_msg = Embed(description="初始化刀表中!",color=0xD98B99)
              table_message = await channel.send(embed = embed_msg)
              embed_msg = Embed(description="初始化暫存刀表中!",color=0xD9ACA3)
              knife_pool_message = await channel.send(embed = embed_msg)
              await ctx.send('已切換為Embed樣式!')
            else:
              msg = "初始化刀表中!"
              table_message = await channel.send(msg)
              msg = "初始化暫存刀表中!"
              knife_pool_message = await channel.send(msg)
              await ctx.send('已切換為Text樣式!')
                    
            # 寫入資料庫
            cursor = connection.cursor(prepared=True)
            sql = "UPDATE princess_connect.group SET table_channel_id = ? ,table_message_id = ?, knife_pool_message_id=?, table_style = ? WHERE server_id = ? and group_serial = ? "
            data = (channel.id, table_message.id, knife_pool_message.id, style, server_id, group_serial)
            cursor.execute(sql, data)
            cursor.close
            connection.commit()
            await Module.Kernel.Update.Update(ctx, ctx.guild.id, group_serial)
          except:
            await ctx.send('刀表訊息已被移除，請重新設定刀表頻道!')
        else:
          await ctx.send('查無戰隊資料!')
     
    await Module.Kernel.DB_control.CloseConnection(connection, ctx)