from discord_slash.utils.manage_commands import create_option, create_choice
import Module.Kernel.Discord_client
import Module.General.cancel_proposal

@Module.Kernel.Discord_client.slash.slash( 
             name="cp" ,
             description="取消自己在刀表上的預約",
             options= [
                 create_option(
                     name="週目",
                     description="填入要取消的週目",
                     option_type=4,
                     required=True
                 ),
                 create_option(
                     name="boss",
                     description="填入要取消的王",
                     option_type=4,
                     required=True,
                     choices=[
                         create_choice(name="1", value=1),create_choice(name="2", value=2),create_choice(name="3", value=3),
                         create_choice(name="4", value=4),create_choice(name="5", value=5)
                     ]
                 ),
                 create_option(
                     name="序號",
                     description="請查看刀表，填入該刀在刀表中的序號",
                     option_type=4,
                     required=True
                 )
             ],
             connector={"週目": "week","boss": "boss","序號": "index"}
             )
async def cancel_proposal(ctx, week, boss, index):
  await Module.General.cancel_proposal.cancel_proposal(
    send_obj = ctx, 
    server_id = ctx.guild.id, 
    sign_channel_id = ctx.channel.id, 
    member_id = ctx.author.id, 
    week = week, 
    boss = boss, 
    index = index
  )
