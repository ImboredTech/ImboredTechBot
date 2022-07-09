import discord
from discord.ext import commands
import config
import os

bot = commands.Bot(command_prefix="!")


@bot.event
async def on_ready():
    print("Bot is online.")


@bot.command()
async def load(ctx, extension):
    if ctx.author.id == "866285734808780812":
        bot.load_extension(f'cogs.{extension}')
        await ctx.send(f"Loaded Cog: {extension}")
    else:
        await ctx.send("Sorry, only the owner of this bot can run this command.")



@bot.command()
async def unload(ctx, extension):
    if ctx.author.id == "866285734808780812":
        bot.unload_extension(f'cogs.{extension}')
        await ctx.send(f"Unloaded Cog: {extension}")
    else:
        await ctx.send("Sorry, only the owner of this bot can run this command.")


@bot.command()
async def reload(ctx, extension):
    if ctx.author.id == "866285734808780812":
        if extension == "all":
            for filename in os.listdir('./cogs'):
                if filename.endswith('.py'):
                    bot.reload_extension(f'cogs.{filename[:-3]}')
                    await ctx.send("Reloaded all cogs.")
                else:
                    print("Ignore this.")
        else:
            bot.reload_extension(f'cogs.{extension}')
            await ctx.send(f'Reloaded Cog: {extension}')
    else:
        await ctx.send("Sorry, only the owner of this can run this command.")

for filename in os.listdir('./cogs'):
    if filename.endswith('.py'):
        bot.load_extension(f'cogs.{filename[:-3]}')
    else:
        print("Ignore this message.")

bot.login(config.token)