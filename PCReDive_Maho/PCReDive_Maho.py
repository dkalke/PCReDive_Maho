import os

from dotenv import load_dotenv

import discord

import TopGG
import Discord_client
from Discord_client import client
import Name_manager
import Event.Ready
import Event.Command


load_dotenv()
TopGG.init()
Name_manager.init()
client.run(os.getenv('TOKEN'))