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