import os

import Module.Kernel.Discord_client
import Module.Kernel.TopGG
import Module.Kernel.Name_manager
import Module.Kernel.Ready

import Event.Command
import Event.SlashCommand.slash_command



Module.Kernel.TopGG.init()
Module.Kernel.Name_manager.init()
Module.Kernel.Discord_client.client.run(os.getenv('TOKEN'))