import discord
from discord.ext import commands
from datetime import datetime
today = datetime.today()
class moderation(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    @commands.has_guild_permissions(ban_members=True)
    async def ban(self, ctx, member : discord.Member, *, reason=None):
        embed = discord.Embed(title="Member Banned Successfully", color=discord.Color.green())
        embed.add_field(name="Member Banned", value=f"{member.mention}", inline=False)
        embed.add_field(name="Reason", value=reason, inline=False)
        embed.add_field(name="Date", value=today, inline=False)
        memberEmbed = discord.Embed(title="You have been banned!", description=f"Guild: {ctx.guild.name}", color=discord.Color.red())
        memberEmbed.add_field(name="Staff Member", value=f"{ctx.author.name}", inline=False)
        memberEmbed.add_field(name="Reason", value=reason, inline=False)
        memberEmbed.add_field(name="Date", value=today, inline=False)
        await ctx.send(embed=embed)
        try:
            await member.send(embed=memberEmbed)
            await member.ban(reason=reason)
        except discord.DiscordException:
            await ctx.send(f"The member {member.mention} has not been notified because their dms are closed.")
            await member.ban(reason=reason)

def setup(bot):
    bot.add_cog(moderation(bot))