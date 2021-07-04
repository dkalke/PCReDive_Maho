import os

from dotenv import load_dotenv

import discord

import Discord_client
import TopGG
import Name_manager
import Event.Ready
import Event.Command
import Event.Slash_command


load_dotenv()
TopGG.init()
Name_manager.init()
Discord_client.client.run(os.getenv('TOKEN'))