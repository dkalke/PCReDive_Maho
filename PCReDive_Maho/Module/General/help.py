from discord import Embed

async def help(send_obj):
  embed_msg = Embed(title='使用說明書', url='https://github.com/dkalke/PCReDive_Maho/wiki', description='網頁版使用說明書\nhttps://github.com/dkalke/PCReDive_Maho/wiki', color=0xB37084)
  embed_msg.set_footer(text='當前版本可能會有些許BUG，歡迎反應或許願新功能!')
  await send_obj.send(embed=embed_msg)
  