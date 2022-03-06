from discord_slash.utils.manage_commands import create_option, create_choice

import Module.Kernel.Discord_client
import Module.General.set_personal_status


@Module.Kernel.Discord_client.slash.slash( 
             name="f" ,
             description="出刀狀態設定",
             options= [
                 create_option(
                     name="剩餘正刀數",
                     description="本日剩餘正刀數量",
                     option_type=4,
                     required=True,
                     choices=[
                         create_choice(name="0", value=0), create_choice(name="1", value=1),create_choice(name="2", value=2),create_choice(name="3", value=3)
                     ]
                 ),
                 create_option(
                     name="剩餘補償數",
                     description="本日剩餘補償數量",
                     option_type=4,
                     required=True,
                     choices=[
                         create_choice(name="0", value=0), create_choice(name="1", value=1),create_choice(name="2", value=2),create_choice(name="3", value=3)
                     ]
                 )
             ],
             connector={"剩餘正刀數": "normal","剩餘補償數": "reversed"}
             )
async def set_personal_status(ctx, normal, reversed):
  await Module.General.set_personal_status.set_personal_status(
    send_obj = ctx, 
    server_id = ctx.guild.id, 
    sign_channel_id = ctx.channel.id, 
    member_id = ctx.author.id,
    normal = normal, 
    reversed = reversed
  )
