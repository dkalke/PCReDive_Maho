import Module.Kernel.DB_control
import Module.Kernel.Authentication
import Module.Kernel.Update
import Module.Kernel.Offset_manager


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
import Event.SlashCommand.Captain.force_set_status
import Event.SlashCommand.Captain.set_fighting_role_id


import Event.SlashCommand.Controller.delete_keep_knife
import Event.SlashCommand.Controller.delete_knife
import Event.SlashCommand.Controller.keep_knife
import Event.SlashCommand.Controller.proposal_knife
import Event.SlashCommand.Controller.set_progress
import Event.SlashCommand.Controller.move_knife


import Event.SlashCommand.General.cancel_keep_proposal
import Event.SlashCommand.General.cancel_proposal
import Event.SlashCommand.General.keep_proposal
import Event.SlashCommand.General.next_boss
import Event.SlashCommand.General.previous_boss
import Event.SlashCommand.General.proposal_knife
import Event.SlashCommand.General.use_keep_proposal
import Event.SlashCommand.General.prefer_time
import Event.SlashCommand.General.use_sl
import Event.SlashCommand.General.add_puppet
import Event.SlashCommand.General.del_puppet
import Event.SlashCommand.General.use_puppet
import Event.SlashCommand.General.help
import Event.SlashCommand.General.calculate_damage

import Event.SlashCommand.General.set_personal_status
import Event.SlashCommand.General.join
import Event.SlashCommand.General.leave
