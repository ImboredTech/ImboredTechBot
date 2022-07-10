import discord
from discord.ext import commands

class info(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
    
    @commands.command()
    async def ping(self, ctx):
        embed = discord.Embed(title="Pong", color=discord.Color.green())
        embed.add_field(name="Latency", value=f"{round(self.bot.latency * 10000)}ms")
        await ctx.send(embed=embed)

def setup(bot):
    bot.add_cog(info(bot))