from discord_slash.utils.manage_commands import create_option, create_choice
import Module.Kernel.Discord_client


import Module.General.previous_boss
#!反悔 [boss]
@Module.Kernel.Discord_client.slash.slash( 
              name="cn" ,
              description="打錯啦，" + str(Module.Kernel.define_value.NCD_TIME) +"秒內可回到上一週目!",
              options=[
                create_option(
                  name="boss",
                  description="哪隻boss?",
                  option_type=4,
                  required=True,
                  choices=[
                    create_choice(name="1", value=1),
                    create_choice(name="2", value=2),
                    create_choice(name="3", value=3),
                    create_choice(name="4", value=4),
                    create_choice(name="5", value=5),
                  ]
                ),
              ],
             )
async def previous_boss(ctx, boss):
  # check頻道，並找出所屬組別
  await Module.General.previous_boss.previous_boss(
    send_obj = ctx, 
    server_id = ctx.guild.id, 
    sign_channel_id = ctx.channel.id, 
    member_id = ctx.author.id, 
    message_create_time = ctx.message.created_at, 
    boss = boss
  )
