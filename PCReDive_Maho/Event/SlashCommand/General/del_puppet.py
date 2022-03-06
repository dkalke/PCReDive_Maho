import Module.Kernel.Discord_client

import Module.General.del_puppet


@Module.Kernel.Discord_client.slash.slash( 
             name="del_puppet" ,
             description="移除一個分身(分身編號最大的)",
             )
async def del_puppet(ctx):
  await Module.General.del_puppet.del_puppet(
    send_obj = ctx, 
    server_id = ctx.guild.id, 
    sign_channel_id = ctx.channel.id, 
    member_id = ctx.author.id
  )
  