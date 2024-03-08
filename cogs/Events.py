import discord
from discord import app_commands
from discord.ext import commands, tasks

from utils.Embed import AiEmbed

from datetime import datetime
import random
import json
import inspect
import aiohttp
import time
import traceback
import asyncio
import os
from cogs.RPG import BetaTestHandler


class Events(commands.Cog):
    """Events Cog"""

    def __init__(self, bot: commands.Bot):
        self.bot: commands.Bot = bot
        self.hidden = True
        self.usagecount = 0
        self.updatecache.start()

    def cog_unload(self) -> tasks.Coroutine[tasks.Any, tasks.Any, None]:
        self.updatecache.stop()

    @commands.Cog.listener()
    async def on_guild_join(self, guild: discord.Guild):
        if guild.id in self.bot.blacklistedguilds:
            embed = AiEmbed(
                title=f"Joined {guild.name}",
                description=f"**ID -** {guild.id}\n**Member Count -** {len(guild.members)}",
                colour=0xFF0000,
            )
            embed.set_footer(text="This server is blacklisted therefore I have left it")
            supportchannel = self.bot.get_channel(1212390372987244586) or await self.bot.fetch_channel(1212390372987244586)
            await guild.leave()
            return await supportchannel.send(embed=embed)
        embed = AiEmbed(
            title=f"Joined {guild.name}",
            description=f"**ID -** {guild.id}\n**Member Count -** {len(guild.members)}",
        )
        supportchannel = self.bot.get_channel(1212390372987244586) or await self.bot.fetch_channel(1212390372987244586)
        await supportchannel.send(embed=embed)

    @commands.Cog.listener()
    async def on_guild_remove(self, guild: discord.Guild):
        if guild.id in self.bot.blacklistedguilds:
            return
        embed = AiEmbed(
            title=f"Left {guild.name}",
            description=f"**ID -** {guild.id}\n**Member Count -** {len(guild.members)}",
        )
        supportchannel = self.bot.get_channel(1212390372987244586) or await self.bot.fetch_channel(1212390372987244586)
        await supportchannel.send(embed=embed)

    @commands.Cog.listener()
    async def on_ready(self):
        val = f"""
              
              Bot is on!\n
              Name     - {self.bot.user.name}\n
              Version  - {discord.__version__}\n
              ID       - {self.bot.user.id}\n
              Owner    - {', '.join([str(self.bot.get_user(he)) for he in self.bot.owner_ids])}\n
              Guilds   - {len(self.bot.guilds)}\n
              Users    - {len(self.bot.users)}
              """
        print(val)
        guild = self.bot.get_guild(1178597884774580274)
        channel = await guild.fetch_channel(1212390372987244586)
        await channel.send(
            embed=AiEmbed(
                title="Bot started",
                description=str("```\n" + inspect.cleandoc(val) + "\n```"),
            )
        )

    @commands.Cog.listener()
    async def on_message_edit(self, before: discord.Message, after: discord.Message):
        if after.author.id == 688293803613880334:
            await self.bot.process_commands(after)

    @commands.Cog.listener()
    async def on_command_error(self, ctx: commands.Context, error: Exception):
        if isinstance(error, commands.CommandNotFound):
            return
        elif isinstance(error, commands.MissingRequiredArgument):
            return await ctx.send(
                embed=AiEmbed.default(
                    ctx,
                    title=f"You did not provide a `{error.param.displayed_name}` argument.",
                    colour=discord.Colour.red(),
                )
            )
        elif isinstance(error, commands.BadArgument):
            return await ctx.send(
                embed=AiEmbed.default(ctx, title=f"The parameter was invalid", colour=discord.Colour.red())
            )
        elif isinstance(error, commands.NSFWChannelRequired):
            return await ctx.send(
                embed=AiEmbed.default(
                    ctx,
                    title="You can only run this command in a NSFW channel",
                    colour=discord.Colour.red(),
                )
            )
        elif isinstance(error, commands.NotOwner):
            return await ctx.send(
                embed=AiEmbed.default(
                    ctx,
                    title=f"You cannot use this command",
                    colour=discord.Colour.red(),
                )
            )
        elif isinstance(error, BetaTestHandler):
            return await ctx.send(
                embed=AiEmbed.default(
                    ctx,
                    title="You are not a beta tester. To be a beta tester you must dm the developer of the bot",
                    colour=discord.Colour.red(),
                )
            )
        elif isinstance(error, commands.CheckFailure):
            return
        elif isinstance(error, commands.CommandOnCooldown):
            await ctx.send(embed=AiEmbed.default(ctx, title="Command is on cooldown", colour=discord.Colour.red()))
        elif isinstance(error, commands.TooManyArguments):
            await ctx.send(
                embed=AiEmbed.default(
                    ctx,
                    title="Too many arguments were given",
                    colour=discord.Colour.red(),
                )
            )
        elif isinstance(error, commands.MissingPermissions):
            await ctx.send(embed=AiEmbed.default(ctx, title=f"{error}", colour=discord.Colour.red()))
        elif isinstance(error, commands.BotMissingPermissions):
            await ctx.send(embed=AiEmbed.default(ctx, title=f"{error}", colour=discord.Colour.red()))
        elif isinstance(error, commands.CommandError):
            replyembed = AiEmbed.default(
                ctx,
                title="Oh No!",
                description="The bot failed to run this command due to an internal error. The developers of the bot were informed.",
                colour=0xFF0000,
            )
            replyembed.add_field(name="The Error", value="```py\n" + str(error) + "```", inline=False)
            await ctx.reply(embed=replyembed)

            loggingserver = await ctx.bot.fetch_guild(1178597884774580274)
            logging = await loggingserver.fetch_channel(1212390372987244586)
            errormsg = "".join(traceback.format_exception(type(error), error, error.__traceback__))
            errormsglnk = await self.bot.mystbin.create_paste(filename="error.py", content=errormsg)
            logembed = AiEmbed.default(
                ctx, title="Error", description=f"```py\n{error}```", url=str(errormsglnk), colour=0xFFFFFF
            )
            valueish = [
                f"- **Author -** {ctx.author} (`{ctx.author.id}`)",
                f"- **Command -** `{ctx.message.content}`",
                f"- **Guild -** {ctx.guild.name} (`{ctx.guild.id}`)",
            ]
            logembed.add_field(name="Detail", value="\n".join(valueish), inline=False)
            await logging.send(embed=logembed)
            raise error

    @commands.Cog.listener()
    async def on_message(self, message: discord.Message):
        if message.author.bot is False and message.author.dm_channel and message.channel.id == message.author.dm_channel.id:
            channel = self.bot.get_channel(1212758116467478619) or await self.bot.fetch_channel(1212758116467478619)
            embed = AiEmbed(title=f"{message.author} dmed me:", description=message.content if message.content else None)
            embed.set_image(url=message.attachments[0].url if message.attachments else None)
            await channel.send(embed=embed)
            return
        if message.content == self.bot.user.mention:
            await message.channel.send(
                embed=AiEmbed(
                    title="Hi there",
                    description=f"Hi there, I am {self.bot.user.name}, for more Information please use `e!help`",
                )
            )
            return

    @commands.Cog.listener()
    async def on_command_completion(self, message: discord.Message):
        if message.author.id not in self.bot.owner_ids:
            self.usagecount += 1
        channel = message.channel
        embed = AiEmbed.default(
            message,
            title="Hey!",
            description="Join the [Support Server](https://discord.gg/RYFpYhPCUz) to recieve updates and provide feedback for the bot.",
        )
        chance = random.randint(0, 1000)
        if chance <= 1:
            await channel.send(embed=embed, delete_after=10.0)
        elif chance >= 990:
            await channel.send(
                "<:info4512:1208451924211269693> TIP:\nWanna suggest a feature for the bot? Use `e!suggest` to suggest a feature for the bot. <:EmiliaRee:1208447880537571338> <:EmiliaRee:1208447880537571338>",
                delete_after=10.0,
            )

    @commands.Cog.listener()
    async def on_dbl_vote(self, data):
        guild = self.bot.get_guild(1178597884774580274)
        channel = await guild.fetch_channel(1212390372987244586)
        await channel.send(data)

    @tasks.loop(minutes=1)
    async def updatecache(self):
        dat = {"all": {"name": "all", "usage": self.usagecount}}
        self.usagecount = 0
        self.bot.dispatch("command_usage_sync", dat)
        await self.bot.usage

    @updatecache.before_loop
    async def beforethatloopy(self):
        await self.bot.wait_until_ready()

    @commands.Cog.listener()
    async def on_command_usage_sync(self, data):
        thing = data["all"]
        async with self.bot.pool.bot.acquire() as conn:
            await conn.execute(
                """INSERT INTO BotInfo (command_usage, amount) VALUES (?, ?)
                ON CONFLICT(command_usage) DO UPDATE SET amount = amount + excluded.amount""",
                (thing["name"], thing["usage"]),
            )
            await conn.commit()


async def setup(bot: commands.Bot):
    await bot.add_cog(Events(bot))
