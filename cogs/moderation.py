from ast import arg
import discord
from discord.ext import commands, tasks
from datetime import datetime
import re
from copy import deepcopy
import asyncio
from dateutil.relativedelta import relativedelta
today = datetime.today()

time_regex = re.compile("(?:(\d{1,5})(h|s|m|d))+?")
time_dict = {"h": 3600, "s": 1, "m": 60, "d": 86400}


class TimeConverter(commands.Converter):
    async def convert(self, ctx, argument):
        args = argument.lower()
        matches = re.findall(time_regex, args)
        time = 0
        for key, value in matches:
            try:
                time += time_dict[value] * float(key)
            except KeyError:
                raise commands.BadArgument(f"{value} is an invalid time key! h|m|s|d are valid arguments")
            except ValueError:
                raise commands.BadArgument(f"{key} is not a number!")
        return round(time)


class moderation(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.mute_task = self.check_current_mutes.start()

    def cog_unload(self):
        self.mute_task.cancel()
    
    @tasks.loop(minutes=5)
    async def check_current_mutes(self):
        currentTime = datetime.now()
        mutes = deepcopy(self.bot.muted_users)
        for key, value in mutes.items():
            if value['muteDuration'] is None:
                continue

            unmuteTime = value['mutedAt'] + relativedelta(seconds=value['muteDuration'])

            if currentTime >= unmuteTime:
                guild = self.bot.get_guild(value['guildId'])
                member = guild.get_member(value['_id'])

                role = discord.utils.get(guild.roles, name="muted")
                if role in member.roles:
                    await member.remove_roles(role)
                    print(f"Unmuted: {member.display_name}")
                

                await self.bot.mutes.delete(member.id)
                try:
                    self.bot.muted_users.pop(member.id)
                except KeyError:
                    pass

    @check_current_mutes.before_loop
    async def before_check_current_mutes(self):
        await self.bot.wait_until_ready()

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
    
    @commands.command()
    @commands.has_guild_permissions(kick_members=True)
    async def kick(self, ctx, member : discord.Member, *, reason=None):
        embed = discord.Embed(title="Member Kicked Successfully", color=discord.Color.green())
        embed.add_field(name="Member Kicked", value=f"{member.mention}", inline=False)
        embed.add_field(name="Reason", value=reason, inline=False)
        embed.add_field(name="Date", value=today, inline=False)
        memberEmbed = discord.Embed(title="You have been kicked!", description=f"Guild: {ctx.guild.name}", color=discord.Color.red())
        memberEmbed.add_field(name="Staff Member", value=f"{ctx.author.name}", inline=False)
        memberEmbed.add_field(name="Reason", value=reason, inline=False)
        memberEmbed.add_field(name="Date", value=today, inline=False)
        await ctx.send(embed=embed)
        try:
            await member.send(embed=memberEmbed)
            await member.kick()
        except discord.DiscordException:
            await ctx.send(f"The member {member.mention} has not been notified because their dms are closed.")
            await member.kick()

    @commands.command()
    @commands.has_guild_permissions(mute_members=True)
    async def mute(self, ctx, member : discord.Member, *, time: TimeConverter=None):
        role = discord.utils.get(ctx.guild.roles, name="muted")
        if not role:
            await ctx.send("No muted role was found! Please create one called `muted`")
            return
        
        try:
            if self.bot.muted_users[member.id]:
                await ctx.send("This user is already muted")
                return
        except KeyError:
            pass
            
        data = {
            '_id': member.id,
            'mutedAt': datetime.now(),
            'muteDuration': time or None,
            'mutedBy': ctx.author.id,
            'guildId': ctx.guild.id,
        }
        await self.bot.mutes.upsert(data)
        self.bot.muted_users[member.id] = data

        await member.add_roles(role)

        if not time:
            await ctx.send(f"Muted {member.mention}")
        else:
            minutes, seconds = divmod(time, 60)
            hours, minutes = divmod(minutes, 60)
            if int(hours):
                await ctx.send(f"Muted {member.mention} for {hours} hours, {minutes} minutes and {seconds} seconds")
            elif int(minutes):
                await ctx.send(f"Muted {member.mention} for {minutes} minutes, {seconds} seconds")
            elif int(seconds):
                await ctx.send(f"Muted {member.mention} for {seconds} seconds")
        
        if time and time < 300:
            await asyncio.sleep(time)

            if role in member.roles:
                await member.remove_roles(role)
                await ctx.send(f"Unmuted `{member.mention}`")
            
            await self.bot.mutes.delete(member.id)
            try:
                self.bot.muted_users.pop(member.id)
            except KeyError:
                pass
    
    @commands.command()
    @commands.has_permissions(mute_members=True)
    async def unmute(self, ctx, member : discord.Member):
        role = discord.utils.get(ctx.guild.roles, name="muted")
        if not role:
            await ctx.send("No muted role was found! Please create one called `muted`")
            return
        
        await self.bot.mutes.delete(member.id)
        try:
            self.bot.muted_users.pop(member.id)
        except KeyError:
            pass
    
        
        if role not in member.roles:
            await ctx.send("This member is not muted.")
            return
        
        await member.remove_roles(role)
        await ctx.send(f"Unmuted `{member.mention}")

def setup(bot):
    bot.add_cog(moderation(bot))