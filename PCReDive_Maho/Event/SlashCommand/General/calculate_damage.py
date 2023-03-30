from discord_slash.utils.manage_commands import create_option, create_choice
import Module.Kernel.Discord_client
import Module.General.calculate_damage

@Module.Kernel.Discord_client.slash.slash( 
             name="cbre" ,
             description="補償刀計算機",
             options= [
                 create_option(
                     name="剩餘血量",
                     description="王當前的剩餘血量(萬)。僅能輸入數字。",
                     option_type=4,
                     required=True,
                 ),
                 create_option(
                     name="第一刀傷害",
                     description="第一刀傷害(萬)。僅能輸入數字。",
                     option_type=4,
                     required=True,
                 ),
                 create_option(
                     name="第二刀傷害",
                     description="第二刀傷害(萬)。僅能輸入數字。",
                     option_type=4,
                     required=True,
                 )
             ],
             connector={"剩餘血量": "remaining","第一刀傷害": "damage1","第二刀傷害": "damage2"}
             )
async def calculate_damage(ctx, remaining, damage1, damage2):
  await Module.General.calculate_damage.calculate_damage(
    send_obj = ctx, 
    remaining = remaining, 
    damage1 = damage1, 
    damage2 = damage2
  )



