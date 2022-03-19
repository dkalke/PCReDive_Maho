from discord.ext import commands 
import discord_slash
import discord

intents = discord.Intents.default()  # Allow the use of custom intents
intents.members = True
bot = commands.Bot(command_prefix=('!','！'), intents=intents)
slash = discord_slash.SlashCommand(bot, sync_commands=True)
