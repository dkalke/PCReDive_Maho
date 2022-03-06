from discord_slash.utils.manage_commands import create_option
import Module.General.keep_proposal

@Module.Kernel.Discord_client.slash.slash( 
             name="kp" ,
             description="報保留刀",
             options= [
                 create_option(
                     name="備註",
                     description="備註（預計傷害）",
                     option_type=3,
                     required=True
                 )
             ],
             connector={"備註": "comment"}
             )
async def keep_proposal(ctx, comment):
  await Module.General.keep_proposal.keep_proposal(
    send_obj = ctx, 
    server_id = ctx.guild.id, 
    sign_channel_id = ctx.channel.id, 
    member_id = ctx.author.id, 
    comment = comment
  )