import Module.Kernel.Discord_client

import Module.General.add_puppet


@Module.Kernel.Discord_client.slash.slash( 
             name="add_puppet" ,
             description="增加一個分身",
             )
async def add_puppet(ctx):
  await Module.General.add_puppet.add_puppet(
    send_obj = ctx, 
    server_id = ctx.guild.id, 
    sign_channel_id = ctx.channel.id, 
    member_id = ctx.author.id
  )
  