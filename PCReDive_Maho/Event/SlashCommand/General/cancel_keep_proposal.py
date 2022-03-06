from discord_slash.utils.manage_commands import create_option
import Module.Kernel.Discord_client
import Module.Kernel.DB_control
import Module.Kernel.Update

#!取消保留刀 [第幾刀]
@Module.Kernel.Discord_client.slash.slash( 
             name="ckp" ,
             description="取消自己在保留區的刀",
             options= [
                 create_option(
                     name="序號",
                     description="請查看刀表，填入該刀在保留區中的序號",
                     option_type=4,
                     required=True
                 )
             ],
             connector={"序號": "index"}
             )
async def cancel_keep_proposal(ctx, index):
  await Module.General.cancel_keep_proposal.cancel_keep_proposal(
    send_obj = ctx, 
    server_id = ctx.guild.id, 
    sign_channel_id = ctx.channel.id, 
    member_id = ctx.author.id, 
    index = index
  )