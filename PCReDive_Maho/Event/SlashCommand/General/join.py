import Module.Kernel.Discord_client
import Module.General.join


@Module.Kernel.Discord_client.slash.slash( 
             name="join" ,
             description="加入該頻道所屬戰隊。",
             )
async def join(ctx):
  await Module.General.join.join(
    send_obj = ctx, 
    server_id = ctx.guild.id, 
    sign_channel_id = ctx.channel.id, 
    member_id = ctx.author.id,
  )
