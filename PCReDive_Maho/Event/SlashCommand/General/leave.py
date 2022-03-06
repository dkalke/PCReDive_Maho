import Module.Kernel.Discord_client
import Module.General.leave


@Module.Kernel.Discord_client.slash.slash( 
             name="leave" ,
             description="離開該頻道所屬戰隊。",
             )
async def leave(ctx):
  await Module.General.leave.leave(
    send_obj = ctx, 
    server_id = ctx.guild.id, 
    sign_channel_id = ctx.channel.id, 
    member_id = ctx.author.id,
  )
