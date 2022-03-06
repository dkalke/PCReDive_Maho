import Module.Kernel.Discord_client

import Module.General.help


@Module.Kernel.Discord_client.slash.slash( 
             name="h" ,
             description="機器人使用說明",
             )
async def help(ctx):
  await Module.General.help.help(ctx)
