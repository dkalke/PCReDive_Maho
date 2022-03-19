from discord_slash.utils.manage_commands import create_option, create_choice

import Module.Kernel.Discord_client
import Module.Kernel.define_value
import Module.General.prefer_time

@Module.Kernel.Discord_client.slash.slash( 
             name="prefer_time" ,
             description="設定自己的偏好出刀時段",
             options= [
                 create_option(
                     name="時段",
                     description="選擇偏好的出刀時段",
                     option_type=4,
                     required=True,
                     choices=[
                         create_choice(name="不定??-??", value=Module.Kernel.define_value.Period.UNKNOW.value),     create_choice(name="清晨05-08", value=Module.Kernel.define_value.Period.EARLY_MORNING.value),
                         create_choice(name="日班08-16", value=Module.Kernel.define_value.Period.DAY.value),        create_choice(name="晚班16-24", value=Module.Kernel.define_value.Period.NIGHT.value),
                         create_choice(name="深夜00-05", value=Module.Kernel.define_value.Period.LAST_NIGHT.value), create_choice(name="全日00-24", value=Module.Kernel.define_value.Period.ALL.value)
                     ]
                 )
             ],
             connector={"時段": "period"}
             )
async def proposal_knife(ctx, period):
  await Module.General.prefer_time.proposal_knife(
    send_obj = ctx, 
    server_id = ctx.guild.id, 
    sign_channel_id = ctx.channel.id, 
    member_id = ctx.author.id, 
    period = period
  )
