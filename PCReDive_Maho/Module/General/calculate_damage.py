from discord import Embed

async def calculate_damage(send_obj, remaining, damage1, damage2, second):
  if remaining == 0 or damage1 == 0 or damage2 == 0:
    await send_obj.send('血量和傷害不可為0。')
  elif (damage1 + damage2) < remaining:
    await send_obj.send('兩刀還殺不掉王啊...')
  elif remaining < damage1:
    await send_obj.send('一刀就能殺掉了...')
  else:
    retime = 90 - (remaining - damage1) / (damage2 / (90 - second)) + 20
    if retime > 90:
      retime = 90
    elif retime == 20:
      await send_obj.send('可能殺不死喔, 靠暴擊吧。')
    redmg = round((damage2 / 90) * retime , 1)

    embed_msg = Embed(title='補償計算', color=0xD98B99)
    embed_msg.set_footer(text="出刀打王有賺有賠, 此資料僅供參考")
    embed_msg.add_field(name="目標血量", value=f"{remaining}萬", inline=True)
    embed_msg.add_field(name="第一刀傷害", value=f"{damage1}萬", inline=True)
    embed_msg.add_field(name="第二刀傷害", value=f"{damage2}萬", inline=True)
    embed_msg.add_field(name="第二刀補償時間", value=f"{retime}秒", inline=True)
    embed_msg.add_field(name="理想補償傷害", value=f"{redmg}萬", inline=True)

    await send_obj.send(embed=embed_msg)
