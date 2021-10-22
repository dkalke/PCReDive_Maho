import Discord_client
from discord import Embed

@Discord_client.slash.slash( 
             name="h" ,
             description="機器人使用說明",
             )
async def help(ctx):
  embed_msg = Embed(title='使用說明書', url='https://github.com/dkalke/PCReDive_Maho/wiki', description='網頁版使用說明書\nhttps://github.com/dkalke/PCReDive_Maho/wiki', color=0xB37084)
  embed_msg.set_footer(text='當前版本可能會有些許BUG，歡迎反應或許願新功能!')
  await ctx.send(embed=embed_msg)