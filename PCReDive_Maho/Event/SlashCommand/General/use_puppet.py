from discord_slash.utils.manage_commands import create_option

import Module.Kernel.Discord_client
import Module.General.use_puppet


#!下面一位 [boss]
@Module.Kernel.Discord_client.slash.slash( 
              name="use" ,
              description="切換分身",
              options=[
                create_option(
                  name="分身編號",
                  description="輸入要切換的分身編號",
                  option_type=4,
                  required=True
                ),
              ],
              connector={"分身編號": "index"}
             )
async def next_boss(ctx, index):
  await Module.General.use_puppet.use_puppet(
    send_obj = ctx, 
    server_id = ctx.guild.id, 
    sign_channel_id = ctx.channel.id, 
    member_id = ctx.author.id, 
    index = index
  )
