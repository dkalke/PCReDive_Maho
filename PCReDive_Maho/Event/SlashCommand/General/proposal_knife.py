from discord_slash.utils.manage_commands import create_option, create_choice
import Module.Kernel.Discord_client
import Module.General.proposal_knife

@Module.Kernel.Discord_client.slash.slash( 
             name="p" ,
             description="預約打王",
             options= [
                 create_option(
                     name="週目",
                     description="填入要預約的週目",
                     option_type=4,
                     required=True
                 ),
                 create_option(
                     name="boss",
                     description="填入要打的王",
                     option_type=4,
                     required=True,
                     choices=[
                         create_choice(name="1", value=1),create_choice(name="2", value=2),create_choice(name="3", value=3),
                         create_choice(name="4", value=4),create_choice(name="5", value=5)
                     ]
                 ),
                 create_option(
                     name="備註",
                     description="備註",
                     option_type=3,
                     required=True
                 )
             ],
             connector={"週目": "week","boss": "boss","備註": "comment"}
             )
async def proposal_knife(ctx, week, boss, comment):
  await Module.General.proposal_knife.proposal_knife(
    send_obj = ctx, 
    server_id = ctx.guild.id, 
    sign_channel_id = ctx.channel.id, 
    member_id = ctx.author.id, 
    week = week, 
    boss = boss, 
    comment = comment
  )
