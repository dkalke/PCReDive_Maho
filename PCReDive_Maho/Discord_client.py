import discord
import discord_slash
client = discord.Client()
slash = discord_slash.SlashCommand(client,sync_commands=True)