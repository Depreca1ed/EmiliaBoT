from typing import Literal, Union, NamedTuple, Optional, Any
from enum import Enum
import discord
from discord.ext import commands
from discord import app_commands
import datetime
import asyncio
from utils.Embed import AiEmbed
from utils.Helpcommand import MyHelpCommand
from collections import Counter
from itertools import product
import json


def get_prefix(client, message):
    prefix = "Ely"
    if message.author.id in client.owner_ids and client.tempvars["Prefixless"] is True:
        return ""
    prefixes = ["".join(capitalization) for capitalization in product(*zip(prefix.lower(), prefix.upper()))]
    return prefixes


class Dev(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot: commands.Bot = bot
        self.bot.help_command = MyHelpCommand()

    @commands.group(
        name="dev",
        description="Developer commands",
        invoke_without_command=True,
        hidden=True,
    )
    @commands.is_owner()
    async def dev(self, ctx: commands.Context):
        await ctx.send("Deprecated is a very cool person")

    @dev.command(name="beta", description="Yes")
    @commands.is_owner()
    async def beta(self, ctx: commands.Context):
        await ctx.reply("Shut the fuck up")
        raise commands.CommandError

    @dev.command(name="hello", description="Says Hello")
    @commands.is_owner()
    async def hello(self, ctx: commands.Context):
        """Says Hello"""
        await ctx.reply(
            embed=AiEmbed.default(
                ctx,
                title="Hi",
                description=f"I am [{self.bot.user.name}](https://discord.com/users/{self.bot.user.id}), made by [Deprecated](https://discord.com/users/688293803613880334).",
            )
        )

    @dev.command(name="say", description="Say things")
    @commands.is_owner()
    async def say(self, ctx: commands.Context, *, message: str):
        if ctx.message.reference:
            try:
                await ctx.message.delete()
            except:
                pass
            return await (await ctx.channel.fetch_message(ctx.message.reference.message_id)).reply(content=message)
        try:
            await ctx.message.delete()
        except:
            pass
        await ctx.send(content=message)

    @dev.command(name="pull", description="Pull things")
    @commands.is_owner()
    async def pull(self, ctx: commands.Context):
        result = await self.shell("git pull origin main")
        output = "\n".join(i.strip() for i in result)
        embed = AiEmbed.default(ctx, title="Pulling from source", description="```ansi\n" + output + "```")
        msg = await ctx.reply(embed=embed)
        reloads = []
        cogs = [a for a in ctx.bot.cogs]
        cogs.remove("Jishaku")
        successfuls = 1
        failures = 0
        for cog in cogs:
            try:
                await ctx.bot.reload_extension("cogs." + cog)
            except Exception as err:
                reloads.append(
                    f"<:xmark4512:1191470897811431465> Failed to reload **{cog}**.py\nError: ```py\n{str(err)}```"
                )
                failures = failures + 1
            else:
                reloads.append(f"<:checkedcheckbox512:1191470926827630662> Successfully reloaded **{cog}.py**")
                successfuls = successfuls + 1
        embed.add_field(
            name=f"Successfully reloaded [{successfuls}/{len(ctx.bot.cogs)}] files with {failures} failures",
            value=str("\n".join(reloads)),
        )
        await msg.edit(embed=embed)

    async def shell(self, code: str, wait: bool = True):
        proc = await asyncio.subprocess.create_subprocess_shell(
            code, stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE
        )
        if wait:
            await proc.wait()
        return tuple(i.decode() for i in await proc.communicate())

    @dev.command(name="del", description="Delete things")
    @commands.is_owner()
    async def dele(self, ctx: commands.Context):
        if ctx.message.reference:
            await (await ctx.channel.fetch_message(ctx.message.reference.message_id)).delete()
            try:
                await ctx.message.delete()
            except:
                pass

    @dev.command("prefixless", description="Mf boutta get or unget prefix")
    @commands.is_owner()
    async def prefixless(self, ctx: commands.Context):
        if self.bot.tempvars["Prefixless"] is True:
            self.bot.tempvars["Prefixless"] = False
            return await ctx.reply(f"`STATE CHANGE`: 'PREFIXLESS' is {self.bot.tempvars['Prefixless']}")
        self.bot.tempvars["Prefixless"] = True
        return await ctx.reply(f"`STATE CHANGE`: 'PREFIXLESS' is {ctx.bot.tempvars['Prefixless']}")

    @dev.command("roleplay", description="Mf boutta get or unget roleplay")
    @commands.is_owner()
    async def roleplayshit(self, ctx: commands.Context):
        if self.bot.tempvars["Roleplay"] is True:
            self.bot.tempvars["Roleplay"] = False
            return await ctx.reply(f"`STATE CHANGE`: 'ROLEPLAY' is {self.bot.tempvars['Roleplay']}")
        self.bot.tempvars["Roleplay"] = True
        return await ctx.reply(f"`STATE CHANGE`: 'ROLEPLAY' is {ctx.bot.tempvars['Roleplay']}")

    @dev.command(description="Search for emojis with name")
    @commands.guild_only()
    @commands.is_owner()
    async def emojisearch(self, ctx: commands.Context, name: str):
        emojis = [emoji for emoji in ctx.bot.emojis if name in emoji.name]
        if not emojis:
            return await ctx.reply("Sorry, there are no emojis with that name that i can see.")
        embed = AiEmbed.default(
            ctx,
            title=f"Emojis with the name {name}",
            description=str("\n".join([f"{str(emoji)} `:` `{emoji}`" for emoji in emojis])),
        )
        await ctx.reply(embed=embed)

    @dev.group(
        name="bl",
        description="Blacklist commands",
        invoke_without_command=True,
        hidden=True,
    )
    @commands.is_owner()
    async def bl(self, ctx: commands.Context):
        return await ctx.reply("Use the subcommands dumbass")

    @bl.command(name="add", description="A motherfucker is about to be blacklisted")
    @commands.is_owner()
    async def bl_add(self, ctx: commands.Context, user: discord.User):
        async with self.bot.pool.bot.acquire() as db:
            async with db.execute("SELECT * FROM blacklisted_users WHERE id = ?", (user.id,)) as cursor:
                already_blacklisted = await cursor.fetchone()

            if already_blacklisted:
                return await ctx.reply(f"{user} is already blacklisted")

            # Add user to the blacklist
            await db.execute("INSERT INTO blacklisted_users (id) VALUES (?)", (user.id,))
            await db.commit()

            ctx.bot.blacklistedusers.append(user.id)
            return await ctx.reply(f"Blacklisted `{user}`")

    @bl.command(name="remove", description="A motherfucker is about to be unblacklisted")
    @commands.is_owner()
    async def bl_remove(self, ctx: commands.Context, user: discord.User):
        async with self.bot.pool.bot.acquire() as db:
            async with db.execute("SELECT * FROM blacklisted_users WHERE id = ?", (user.id,)) as cursor:
                already_blacklisted = await cursor.fetchone()

            if not already_blacklisted:
                return await ctx.reply(f"{user} is not already blacklisted")

            # Remove user from the blacklist
            await db.execute("DELETE FROM blacklisted_users WHERE id = ?", (user.id,))
            await db.commit()

            ctx.bot.blacklistedusers.remove(user.id)
            return await ctx.reply(f"Unblacklisted `{user}`")

    @dev.group(
        name="gbl",
        description="Guild Blacklist commands",
        invoke_without_command=True,
        hidden=True,
    )
    @commands.is_owner()
    async def gbl(self, ctx: commands.Context):
        return await ctx.reply("Use the subcommands dumbass")

    @gbl.command(name="add", description="A guild is about to be blacklisted")
    @commands.is_owner()
    async def gbl_add(self, ctx: commands.Context, guild: discord.Guild):
        async with self.bot.pool.bot.acquire() as db:
            async with db.execute("SELECT * FROM blacklisted_guilds WHERE id = ?", (guild.id,)) as cursor:
                already_blacklisted = await cursor.fetchone()

            if already_blacklisted:
                return await ctx.reply(f"{guild.name} is already blacklisted")

            # Add user to the blacklist
            await db.execute("INSERT INTO blacklisted_guilds (id) VALUES (?)", (guild.id,))
            await db.commit()

            ctx.bot.blacklistedguilds.append(guild.id)
            await ctx.reply(f"Blacklisted `{guild.name}`")
            return await guild.leave()

    @gbl.command(name="remove", description="A motherfucker is about to be unblacklisted")
    @commands.is_owner()
    async def gbl_remove(self, ctx: commands.Context, guild: discord.Guild):
        async with self.bot.pool.bot.acquire() as db:
            async with db.execute("SELECT * FROM blacklisted_guilds WHERE id = ?", (guild.id,)) as cursor:
                already_blacklisted = await cursor.fetchone()

            if not already_blacklisted:
                return await ctx.reply(f"{guild.name} is not already blacklisted")

            # Remove guild from the blacklist
            await db.execute("DELETE FROM blacklisted_guilds WHERE id = ?", (guild.id,))
            await db.commit()

            ctx.bot.blacklistedguilds.remove(guild.id)
            return await ctx.reply(f"Unblacklisted `{guild.name}`")

    @dev.command(name="sugshow", description="A motherfucker is about to be shown a suggestion")
    @commands.is_owner()
    async def sugshow(self, ctx: commands.Context, msg: discord.Message):
        channel = (await self.bot.fetch_user(self.bot.dep.id)).dm_channel
        await ctx.reply(embed=(await channel.fetch_message(msg.id)).embeds[0])

    async def _basic_cleanup_strategy(self, ctx: commands.Context, search: int):
        count = 0
        async for msg in ctx.history(limit=search, before=ctx.message):
            if (
                msg.author == ctx.me and not (msg.mentions or msg.role_mentions)
                if msg.author.id not in self.bot.owner_ids
                else False
            ):
                await msg.delete()
                count += 1
        return {"Bot": count}

    async def _complex_cleanup_strategy(self, ctx: commands.Context, search: int):

        def check(m):
            prefixes = tuple(get_prefix(self.bot, m))
            return m.author == ctx.me or m.content.startswith(prefixes) if m.author.id not in self.bot.owner_ids else False

        deleted = await ctx.channel.purge(limit=search, check=check, before=ctx.message)
        return Counter(m.author.display_name for m in deleted)

    async def _regular_user_cleanup_strategy(self, ctx: commands.Context, search: int):

        def check(m):
            prefixes = tuple(get_prefix(self.bot, m))
            return (
                (m.author == ctx.me or m.content.startswith(prefixes)) and not (m.mentions or m.role_mentions)
                if m.author.id not in self.bot.owner_ids
                else False
            )

        deleted = await ctx.channel.purge(limit=search, check=check, before=ctx.message)
        return Counter(m.author.display_name for m in deleted)

    @dev.command()
    @commands.cooldown(1, 5.0, type=commands.BucketType.channel)
    @commands.is_owner()
    async def cleanup(self, ctx: commands.Context, search: int = 100):
        """Cleans up the bot's messages from the channel.

        If a search number is specified, it searches that many messages to delete.
        If the bot has Manage Messages permissions then it will try to delete
        messages that look like they invoked the bot as well.

        After the cleanup is completed, the bot will send you a message with
        which people got their messages deleted and their count. This is useful
        to see which users are spammers.

        Members with Manage Messages can search up to 1000 messages.
        Members without can search up to 25 messages.
        """

        strategy = self._basic_cleanup_strategy
        is_mod = ctx.channel.permissions_for(ctx.author).manage_messages
        if ctx.channel.permissions_for(ctx.me).manage_messages:
            if is_mod:
                strategy = self._complex_cleanup_strategy
            else:
                strategy = self._regular_user_cleanup_strategy
        if is_mod:
            search = min(max(2, search), 1000)
        else:
            search = min(max(2, search), 25)
        spammers = await strategy(ctx, search)
        deleted = sum(spammers.values())
        messages = [f'{deleted} message{" was" if deleted == 1 else "s were"} removed.']
        if deleted:
            messages.append("")
            spammers = sorted(spammers.items(), key=lambda t: t[1], reverse=True)
            messages.extend(f"- **{author}**: {count}" for author, count in spammers)

        await ctx.send("\n".join(messages), delete_after=10)


async def setup(bot: commands.Bot):
    await bot.add_cog(Dev(bot))
