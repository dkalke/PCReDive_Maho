from discord_slash.utils.manage_commands import create_option, create_choice

import Module.Kernel.Discord_client
import Module.General.next_boss


#!下面一位 [boss]
@Module.Kernel.Discord_client.slash.slash( 
              name="n" ,
              description="王死拉，下面一位!",
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
async def next_boss(ctx, boss):
  await Module.General.next_boss.next_boss(
    send_obj = ctx, 
    server_id = ctx.guild.id, 
    sign_channel_id = ctx.channel.id, 
    member_id = ctx.author.id, 
    message_create_time = ctx.created_at, 
    boss = boss
  )
