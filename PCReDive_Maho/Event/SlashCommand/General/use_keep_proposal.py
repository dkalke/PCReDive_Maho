from discord_slash.utils.manage_commands import create_option, create_choice
import Module.General.use_keep_proposal

@Module.Kernel.Discord_client.slash.slash( 
             name="ukp" ,
             description="使用保留刀",
             options= [
                create_option(
                     name="序號",
                     description="請查看保留區，填入該刀在保留區中的序號",
                     option_type=4,
                     required=True
                 ),
                 create_option(
                     name="週目",
                     description="要用在哪一週目?",
                     option_type=4,
                     required=True
                 ),
                 create_option(
                     name="boss",
                     description="要打哪一隻王?",
                     option_type=4,
                     required=True,
                     choices=[
                         create_choice(name="1", value=1),create_choice(name="2", value=2),create_choice(name="3", value=3),
                         create_choice(name="4", value=4),create_choice(name="5", value=5)
                     ]
                 )
             ],
             connector={"序號": "index", "週目": "week", "boss": "boss"}
             )
async def use_keep_proposal(ctx, index, week, boss):
  await Module.General.use_keep_proposal.use_keep_proposal(
    send_obj = ctx, 
    server_id = ctx.guild.id, 
    sign_channel_id = ctx.channel.id, 
    member_id = ctx.author.id, 
    index = index,
    week = week, 
    boss = boss
  )