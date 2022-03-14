from discord_slash.utils.manage_commands import create_option
import Module.Kernel.Discord_client

import Module.General.del_puppet


@Module.Kernel.Discord_client.slash.slash( 
             name="del_puppet" ,
             description="移除一個分身。",
             options=[
               create_option(
                 name="分身編號",
                 description="分身編號只能為正整數，不可與自己其餘的分身編號重複。",
                 option_type=4,
                 required=True
               )
             ],
             connector={"分身編號": "index"}
             )
async def del_puppet(ctx, index):
  await Module.General.del_puppet.del_puppet(
    send_obj = ctx, 
    server_id = ctx.guild.id, 
    sign_channel_id = ctx.channel.id, 
    member_id = ctx.author.id,
    index = index
  )
  