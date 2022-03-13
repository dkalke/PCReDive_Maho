from mysql.connector import Error
from discord.ext.commands import CommandNotFound
from Module.Kernel.Discord_client import bot

import Module.Kernel.define_value
import Module.General.proposal_knife
import Module.General.cancel_proposal
import Module.General.keep_proposal
import Module.General.use_keep_proposal
import Module.General.cancel_keep_proposal
import Module.General.next_boss
import Module.General.previous_boss
import Module.General.prefer_time
import Module.General.use_sl
import Module.General.add_puppet
import Module.General.del_puppet
import Module.General.use_puppet
import Module.General.timeline_shifter
import Module.General.help
import Module.General.leave
import Module.General.join
import Module.General.set_personal_status


try:


  @bot.event
  async def on_command_error(ctx, error):
    if isinstance(error, CommandNotFound):
      return # 不顯示查無指令的提示訊息在console上
    raise error


  @bot.command(aliases = ['p', 'P', 'ｐ', 'Ｐ' '預約', '预约'])
  #報刀指令 !預約 [周目] [幾王] [註解]
  async def command_p(ctx, *args): 
    if len(args) == 3:
      if args[0].isdigit() and args[1].isdigit():
        comment = args[2]
        await Module.General.proposal_knife.proposal_knife(
          send_obj = ctx, 
          server_id = ctx.guild.id, 
          sign_channel_id = ctx.channel.id, 
          member_id = ctx.author.id, 
          week = int(args[0]), 
          boss = int(args[1]), 
          comment = args[1]
        )
      else:
        await ctx.send('[週目] [王] [預估傷害]請使用阿拉伯數字!')
    else:
      await ctx.send('!預約 格式錯誤，應為 !預約 [週目] [王] [註解]')


  @bot.command(aliases = ['cp', 'CP', 'ｃｐ', 'ＣＰ', '取消預約', '取消预约'])
  #取消報刀  !取消預約 [周目] [幾王] [第幾刀]
  async def command_cp(ctx, *args):
    if len(args) == 3:
      if args[0].isdigit() and args[1].isdigit() and args[2].isdigit():
        await Module.General.cancel_proposal.cancel_proposal(
          send_obj = ctx, 
          server_id = ctx.guild.id, 
          sign_channel_id = ctx.channel.id, 
          member_id = ctx.author.id, 
          week = int(args[0]), 
          boss = int(args[1]), 
          index = int(args[2])
        )
      else:
        await ctx.send('[週目] [王] [第幾刀]請使用阿拉伯數字!')
    else:
      await ctx.send('!取消預約 格式錯誤，應為 !取消預約 [週目] [王] [第幾刀]')


  @bot.command(aliases = ['kp', 'KP', 'ｋｐ', 'ＫＰ', '報保留刀', '报保留刀'])
  #!報保留刀 [備註]
  async def command_kp(ctx, *args):
    if len(args) == 1:
      await Module.General.keep_proposal.keep_proposal(
        send_obj = ctx, 
        server_id = ctx.guild.id, 
        sign_channel_id = ctx.channel.id, 
        member_id = ctx.author.id, 
        comment = args[0]
      )
    else:
      await message.channel.send('!報保留刀 格式錯誤，應為 !報保留刀 [註解]')


  @bot.command(aliases = ['ukp', 'UKP', 'ｕｋｐ', 'ＵＫＰ', '使用保留刀'])
  #!使用保留刀 [第幾刀] [週目] [boss]
  async def command_ukp(ctx, *args):
    if len(args) == 3:
      if args[0].isdigit() and args[1].isdigit() and args[2].isdigit():
        await Module.General.use_keep_proposal.use_keep_proposal(
          send_obj = ctx, 
          server_id = ctx.guild.id, 
          sign_channel_id = ctx.channel.id, 
          member_id = ctx.author.id, 
          index = int(args[0]),
          week = int(args[1]), 
          boss = int(args[2])
        )
      else:
        await ctx.send('[第幾刀] [週目] [boss]請使用阿拉伯數字!')
    else:
      await ctx.send('!使用保留刀 格式錯誤，應為:\n 1~4階段: !使用保留刀 [第幾刀] [週目] [boss]\n5階段: !使用保留刀 [第幾刀] [週目] [boss] [預估傷害]')


  @bot.command(aliases = ['ckp', 'CKP', 'ｃｋｐ', 'ＣＫＰ', '取消保留刀'])
  #!取消保留刀 [第幾刀]
  async def command_ckp(ctx, *args):
    if len(args) == 1:
      if args[0].isdigit():
        await Module.General.cancel_keep_proposal.cancel_keep_proposal(
          send_obj = ctx, 
          server_id = ctx.guild.id, 
          sign_channel_id = ctx.channel.id, 
          member_id = ctx.author.id, 
          index = int(args[0])
        )
      else:
        await message.channel.send('[第幾刀]請使用阿拉伯數字!')
    else:
      await message.channel.send('!取消保留刀 格式錯誤，應為 !取消保留刀 [第幾刀]')


  @bot.command(aliases = ['n', 'N', 'ｎ', 'Ｎ', '下面一位'])
  #!下面一位 [boss]
  async def command_n(ctx, *args):
    if len(args) == 1:
      if args[0].isdigit():
        boss = int(args[0])
        if boss > 0 and boss < 6:
          await Module.General.next_boss.next_boss(
            send_obj = ctx, 
            server_id = ctx.guild.id, 
            sign_channel_id = ctx.channel.id, 
            member_id = ctx.author.id, 
            message_create_time = ctx.message.created_at, 
            boss = boss
          )
        else:
          await ctx.send('[boss]只能是包含1~5的正整數!')
      else:
        await ctx.send('[boss]請使用阿拉伯數字!')
    else:
      await ctx.send('!下面一位 格式錯誤，應為 !下面一位 [boss]')


  @bot.command(aliases = ['cn', 'CN', 'ｃｎ', 'ＣＮ', '反悔'])
  #!反悔 [boss]
  async def command_cn(ctx, *args):
    if len(args) == 1:
      if args[0].isdigit():
        boss = int(args[0])
        if boss > 0 and boss < 6:
          await Module.General.previous_boss.previous_boss(
            send_obj = ctx, 
            server_id = ctx.guild.id, 
            sign_channel_id = ctx.channel.id, 
            member_id = ctx.author.id, 
            message_create_time = ctx.message.created_at, 
            boss = boss
          )
        else:
          await ctx.send('王只能是包含1~5的正整數!')
      else:
        await ctx.send('請輸入數字!')
    else:
      await ctx.send('!反悔 格式錯誤，應為 !反悔 [boss]')


  @bot.command(aliases = ['pt', 'PT', 'ｐｔ', 'ＰＴ', '偏好時段', '偏好时段'])
  #!偏好時段 [時段]
  async def command_pt(ctx, *args):
    if len(args) == 1:
      period = args[0]
      if period== "0" or period== "u" or period== "不定" or period== "不定??-??": # ??-??
        period = Module.Kernel.define_value.Period.UNKNOW.value
      elif period== "1" or period== "d" or period== "日班" or period== "日班08-16": # 08-16
        period = Module.Kernel.define_value.Period.DAY.value
      elif period== "2" or period== "n" or period== "晚班" or period== "晚班16-24": # 16-24
        period = Module.Kernel.define_value.Period.NIGHT.value
      elif period== "3" or period== "g" or period== "夜班" or period== "夜班00-08": # 00-08
        period = Module.Kernel.define_value.Period.GRAVEYARD.value
      elif period== "4" or period== "a" or period== "全日" or period== "全日00-24": # 00-24
        period = Module.Kernel.define_value.Period.ALL.value
      else:
        period = -1 # ERROR

      if not period == -1:
        await Module.General.prefer_time.proposal_knife(
          send_obj = ctx, 
          server_id = ctx.guild.id, 
          sign_channel_id = ctx.channel.id, 
          member_id = ctx.author.id, 
          period = period
        )
      else:
        await ctx.send('[時段]輸入錯誤，請參考說明書!')
    else:
      await ctx.send('!偏好時段 格式錯誤，應為 !偏好時段 [時段]')


  @bot.command(aliases = ['sl', 'SL', 'ｓｌ', 'ＳＬ', '閃退', '闪退'])
  #!閃退
  async def command_sl(ctx, *args):
    if len(args) == 0:
      await Module.General.use_sl.use_sl(
        send_obj = ctx, 
        server_id = ctx.guild.id, 
        sign_channel_id = ctx.channel.id, 
        member_id = ctx.author.id
      )
    else:
      await ctx.send('!閃退 格式錯誤，應為 !閃退')


  @bot.command(aliases = ['add_puppet', 'ADD_PUPPET', 'ａｄｄ＿ｐｕｐｐｅｔ', 'ＡＤＤ＿ＰＵＰＰＥＴ', '增加分身'])
  #!增加分身
  async def command_add_puppet(ctx, *args):
    if len(args) == 1:
      if args[0].isdigit():
        await Module.General.add_puppet.add_puppet(
          send_obj = ctx, 
          server_id = ctx.guild.id, 
          sign_channel_id = ctx.channel.id, 
          member_id = ctx.author.id,
          index = int(args[0])
        )
      else:
        await ctx.send('發生錯誤 [分身編號] 只能是正整數!')
    else:
      await ctx.send('!增加分身 格式錯誤，應為 !增加分身 [分身編號]')


  @bot.command(aliases = ['del_puppet', 'DEL_PUPPET', 'ｄｅｌ＿ｐｕｐｐｅｔ', 'ＤＥＬ＿ＰＵＰＰＥＴ', '移除分身'])
  #!移除分身 (分身號碼最大的)
  async def command_del_puppet(ctx, *args):
    if len(args) == 1:
      if args[0].isdigit():
        await Module.General.del_puppet.del_puppet(
          send_obj = ctx, 
          server_id = ctx.guild.id, 
          sign_channel_id = ctx.channel.id, 
          member_id = ctx.author.id,
          index = int(args[0])
        )
      else:
        await ctx.send('發生錯誤 [分身編號] 只能是正整數!')
    else:
      await ctx.send('!移除分身 格式錯誤，應為 !移除分身 [分身編號]')


  @bot.command(aliases = ['use', 'USE', 'ｕｓｅ', 'ＵＳＥ', '切換分身', '切换分身'])
  #!切換分身 [分身編號]
  async def command_use_puppet(ctx, *args):
    if len(args) == 1:
      if args[0].isdigit():
        await Module.General.use_puppet.use_puppet(
          send_obj = ctx, 
          server_id = ctx.guild.id, 
          sign_channel_id = ctx.channel.id, 
          member_id = ctx.author.id, 
          index = int(args[0])
        )
      else:
        await ctx.send('[分身編號] 請使用阿拉伯數字!')
    else:
      await ctx.send('!切換分身 格式錯誤，應為 !切換分身 [分身編號]')  


  @bot.command(aliases = ['join', 'LOIN', 'ｊｏｉｎ', 'ＪＯＩＮ', '加入'])
  #!加入
  async def command_join(ctx, *args):
    if len(args) == 0:
      await Module.General.join.join(
        send_obj = ctx, 
        server_id = ctx.guild.id, 
        sign_channel_id = ctx.channel.id, 
        member_id = ctx.author.id,
      )
    else:
      await ctx.send('!加入 格式錯誤，應為 !加入')  


  @bot.command(aliases = ['leave', 'LEAVE', 'ｌｅａｖｅ', 'ＬＥＡＶＥ', '退出'])
  #!退出
  async def command_leave(ctx, *args):
    if len(args) == 0:
      await Module.General.leave.leave(
        send_obj = ctx, 
        server_id = ctx.guild.id, 
        sign_channel_id = ctx.channel.id, 
        member_id = ctx.author.id,
      )
    else:
      await ctx.send('!退出 格式錯誤，應為 !退出')  


  @bot.command(aliases = ['f', 'F', 'ｆ', 'Ｆ', '狀態', '状态 '])
  #!狀態 [剩餘正刀數]　[剩餘補償數]
  async def command_f(ctx, *args):
    if len(args) == 2:
      if args[0].isdigit() and args[1].isdigit():
        normal = int(args[0])
        reversed = int(args[1])
        if 0 <= normal and normal <= 3 and 0 <= reversed and reversed <= 3 :
          await Module.General.set_personal_status.set_personal_status(
            send_obj = ctx, 
            server_id = ctx.guild.id, 
            sign_channel_id = ctx.channel.id, 
            member_id = ctx.author.id,
            normal = normal, 
            reversed = reversed
          )
        else:
          await ctx.send('[剩餘正刀數]　[剩餘補償數] 僅能為0~3的整數!')
      else:
        await ctx.send('[剩餘正刀數]　[剩餘補償數] 請使用阿拉伯數字!')
    else:
      await ctx.send('!狀態 格式錯誤，應為 !狀態 [剩餘正刀數]　[剩餘補償數]')  


  @bot.command(aliases = ['tr', 'TR', 'ｔｒ', 'ＴＲ', '刀軸時移', '刀轴时移'])
  #!刀軸時移功能(the author is YungPingXu, this version is modified)
  async def command_tr(ctx, *args):
    await Module.General.timeline_shifter.timeline_shifter(
      send_obj = ctx.author,
      content = ctx.message.content
    )


  @bot.command(aliases = ['h', 'H', 'ｈ', 'Ｈ', '幫助', '帮助'])
  #!帮助
  async def command_h(ctx, *args):
    await Module.General.help.help(ctx)


except Error as e:
  print("資料庫錯誤 ",e)
except Exception as e:
  print("error ",e)
