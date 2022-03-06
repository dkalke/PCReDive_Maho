import os
import dotenv

import Module.Kernel.Discord_client
import Module.Kernel.Ready
import Event.Command
import Event.SlashCommand.slash_command

dotenv.load_dotenv()
Module.Kernel.Discord_client.bot.run(os.getenv('TOKEN'))