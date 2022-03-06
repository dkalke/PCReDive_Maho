import Module.Kernel.Discord_client

import Module.General.use_sl


@Module.Kernel.Discord_client.slash.slash( 
             name="sl" ,
             description="使用SL",
             )
async def use_sl(ctx):
  await Module.General.use_sl.use_sl(
    send_obj = ctx, 
    server_id = ctx.guild.id, 
    sign_channel_id = ctx.channel.id, 
    member_id = ctx.author.id
  )
  