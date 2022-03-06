from discord.ext import commands 
import discord_slash

bot = commands.Bot(command_prefix=('!','！'))
slash = discord_slash.SlashCommand(bot, sync_commands=True)