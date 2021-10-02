import Discord_client
from discord_slash.utils.manage_commands import create_option, create_choice
import Module.DB_control
import Module.Authentication
import Module.Update
import Module.Offset_manager


import Event.SlashCommand.Admin.create_group
import Event.SlashCommand.Admin.delete_group
import Event.SlashCommand.Admin.add_captain
import Event.SlashCommand.Admin.remove_captain
import Event.SlashCommand.Admin.group_list


import Event.SlashCommand.Captain.clear_table
import Event.SlashCommand.Captain.export_table
import Event.SlashCommand.Captain.set_controller_role
import Event.SlashCommand.Captain.set_sign_channel_here
import Event.SlashCommand.Captain.set_table_channel_here
import Event.SlashCommand.Captain.set_table_style
import Event.SlashCommand.Captain.set_weeks_offset
import Event.SlashCommand.Captain.set_info_channel_here
import Event.SlashCommand.Captain.add_member
import Event.SlashCommand.Captain.delete_member
import Event.SlashCommand.Captain.set_member_knifes
import Event.SlashCommand.Captain.set_policy


import Event.SlashCommand.Controller.delete_keep_knife
import Event.SlashCommand.Controller.delete_knife
import Event.SlashCommand.Controller.keep_knife
import Event.SlashCommand.Controller.move_knife
import Event.SlashCommand.Controller.proposal_knife
import Event.SlashCommand.Controller.set_progress


import Event.SlashCommand.General.cancel_keep_proposal
import Event.SlashCommand.General.cancel_proposal
import Event.SlashCommand.General.keep_proposal
import Event.SlashCommand.General.next_boss
import Event.SlashCommand.General.now_progeass
import Event.SlashCommand.General.proposal_knife
import Event.SlashCommand.General.use_keep_proposal
import Event.SlashCommand.General.prefer_time
import Event.SlashCommand.General.done_proposal
import Event.SlashCommand.General.done_skip_proposal


# import Event.SlashCommand.General.hit_boss # 擾民棄用，實際狀況可直接使用discord內建tag功能提醒尚未出刀者。