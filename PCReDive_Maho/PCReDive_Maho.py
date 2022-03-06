import os
import dotenv
dotenv.load_dotenv()

import Module.Kernel.Discord_client
import Module.Kernel.Ready
import Event.Command
import Event.SlashCommand.slash_command

Module.Kernel.Discord_client.bot.run(os.getenv('TOKEN'))