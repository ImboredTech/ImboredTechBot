import discord
from discord.ext import commands
import config

bot = commands.Bot(command_prefix="!")


@bot.event
async def on_ready():
    print("Bot is online.")



bot.login(config.token)