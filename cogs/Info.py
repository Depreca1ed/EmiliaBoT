from typing import Literal, Union, NamedTuple, Optional, List
import discord
from discord.ext import commands
from datetime import datetime
import psutil
import sys
import humanize
import random
import json
import aiohttp
import time
import traceback
import asyncio
from utils.Embed import AiEmbed
from utils.Pagination import ElyPagination


class userinfoView(discord.ui.View):
    def __init__(self, user: discord.Member, ctx: commands.Context, message: discord.Message):
        super().__init__(timeout=120.0)
        self.user: discord.Member = user
        self.ctx: commands.Context = ctx
        self.message: discord.Message = message
        p = []
        for a in user.guild_permissions:
            if a[1] == True:
                p.append(f"<:checkedcheckbox512:1191470926827630662> `{(str(a[0])).replace('_', ' ').title()}`")
            elif a[1] == False:
                p.append(f"<:xmark4512:1191470897811431465> `{(str(a[0])).replace('_', ' ').title()}`")
            else:
                p.append(str((a[0], a[1])))
        self.permissionsstring = "\n".join(p)

    @discord.ui.button(label="Permissions", emoji="🛡️", style=discord.ButtonStyle.blurple)
    async def permissionsbutton(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_message(
            embed=AiEmbed.default(
                self.ctx,
                title=f"{button.emoji} {button.label}",
                description=self.permissionsstring,
                color=0x87CEEB,
            ),
            ephemeral=True,
        )

    async def on_timeout(self):
        await self.message.edit(view=None)
        self.stop()


class roleinfoView(discord.ui.View):
    def __init__(self, role: discord.Role, ctx: commands.Context, msg: discord.Message):
        super().__init__(timeout=120.0)
        self.role: discord.Role = role
        self.ctx: commands.Context = ctx
        self.message: discord.Message = msg
        p = []
        for a in role.permissions:
            if a[1] == True:
                p.append(f"<:checkedcheckbox512:1191470926827630662> `{(str(a[0])).replace('_', ' ').title()}`")
            elif a[1] == False:
                p.append(f"<:xmark4512:1191470897811431465> `{(str(a[0])).replace('_', ' ').title()}`")
            else:
                p.append(str((a[0], a[1])))
        self.permissionsstring = "\n".join(p)

    @discord.ui.button(label="Permissions", emoji="🛡️", style=discord.ButtonStyle.blurple)
    async def permissionsbutton(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_message(
            embed=AiEmbed.default(
                self.ctx,
                title=f"{button.emoji} {button.label}",
                description=self.permissionsstring,
                color=0x87CEEB,
            ),
            ephemeral=True,
        )

    async def on_timeout(self):
        await self.message.edit(view=None)
        self.stop()


class BotinfoView(discord.ui.View):
    def __init__(
        self,
        ctx: commands.Context,
        msg: discord.Message,
        botinfoembed: AiEmbed,
        sysembed: AiEmbed,
        teamembed: AiEmbed,
        avembed: AiEmbed,
    ):
        super().__init__(timeout=500.0)
        self.sysembed: AiEmbed = sysembed
        self.botinfoembed: AiEmbed = botinfoembed
        self.teamembed: AiEmbed = teamembed
        self.avembed: AiEmbed = avembed
        self.ctx: commands.Context = ctx
        self.message: discord.Message = msg

    @discord.ui.select(
        options=[
            discord.SelectOption(label="Bot Information", emoji="<:emilia1:1208447101105602621>"),
            discord.SelectOption(label="System Information", emoji="<:console5121:1208450289888133170>"),
            discord.SelectOption(label="Team Information", emoji="<a:Satella:1208450738498437140>"),
            discord.SelectOption(label="Bot's Avatar", emoji="<:emilia_sexy:1208447436536811592>"),
        ]
    )
    async def on_select(self, inter: discord.Interaction, select: discord.ui.Select):
        if select.values[0].lower() == "bot information":
            await inter.response.edit_message(embed=self.botinfoembed)
        elif select.values[0].lower() == "system information":
            await inter.response.edit_message(embed=self.sysembed)
        elif select.values[0].lower() == "team information":
            await inter.response.edit_message(embed=self.teamembed)
        elif select.values[0].lower() == "bot's avatar":
            await inter.response.edit_message(embed=self.avembed)
        else:
            await inter.reponse.send_message("What The fuck")

    async def on_timeout(self):
        await self.message.edit(view=None)
        self.stop()

    async def on_error(self, inter: discord.Interaction, error: Exception, item: discord.ui.Item):
        if inter.response.is_done():
            func = inter.followup.send
        else:
            func = inter.response.send_message
        errormsg = "```py\n" + "".join(traceback.format_exception(type(error), error, error.__traceback__)) + "```"
        return await func(f"Error(Send this to developer):\n{str(errormsg)}", ephemeral=False)

    async def interaction_check(self, interaction: discord.Interaction):
        if interaction.user.id == self.ctx.author.id:
            return True
        await interaction.response.send_message(
            "This is not your Interaction!",
            ephemeral=True,
        )
        return False


class ServerinfoView(discord.ui.View):
    def __init__(
        self,
        ctx: commands.Context,
        msg: discord.Message,
        serverinfo: AiEmbed,
        boostembed: AiEmbed,
        userembed: AiEmbed,
        avembed: AiEmbed,
        serverembed: AiEmbed,
    ):
        super().__init__(timeout=500.0)
        self.on_select.options = [
            discord.SelectOption(label="Server Information", emoji="<:info4512:1208451924211269693>"),
            discord.SelectOption(label="User Information", emoji="<:emilia1:1208447101105602621>"),
        ]
        if boostembed:
            self.on_select.options.append(
                discord.SelectOption(label="Boost Information", emoji="<:emilia_what:1208447897432096878>")
            )
        if avembed:
            self.on_select.options.append(
                discord.SelectOption(label="Server's Icon", emoji="<:emiliapout:1208447007954309190>")
            )
        if serverembed:
            self.on_select.options.append(
                discord.SelectOption(label="Server's Banner", emoji="<:EmiliaRee:1208447880537571338>")
            )
        self.boostembed: AiEmbed = boostembed
        self.serverinfo: AiEmbed = serverinfo
        self.userembed: AiEmbed = userembed
        self.avembed: AiEmbed = avembed
        self.serverembed: AiEmbed = serverembed
        self.ctx: commands.Context = ctx
        self.message: discord.Message = msg

    @discord.ui.select()
    async def on_select(self, inter: discord.Interaction, select: discord.ui.Select):
        selected_value = select.values[0].lower()
        if selected_value == "server information":
            await inter.response.edit_message(embed=self.serverinfo)
        elif selected_value == "boost information":
            await inter.response.edit_message(embed=self.boostembed)
        elif selected_value == "user information":
            await inter.response.edit_message(embed=self.userembed)
        elif selected_value == "server's icon":
            await inter.response.edit_message(embed=self.avembed)
        elif selected_value == "server's banner":
            await inter.response.edit_message(embed=self.serverembed)
        else:
            await inter.response.send_message("Invalid selection")

    async def on_timeout(self):
        await self.message.edit(view=None)
        self.stop()

    async def on_error(self, inter: discord.Interaction, error: Exception, item: discord.ui.Item):
        if inter.response.is_done():
            func = inter.followup.send
        else:
            func = inter.response.send_message
        errormsg = "```py\n" + "".join(traceback.format_exception(type(error), error, error.__traceback__)) + "```"
        return await func(f"Error(Send this to developer):\n{str(errormsg)}", ephemeral=False)

    async def interaction_check(self, interaction: discord.Interaction):
        if interaction.user.id == self.ctx.author.id:
            return True
        await interaction.response.send_message(
            "This is not your Interaction!",
            ephemeral=True,
        )
        return False


def statusxD(user: discord.Member):
    if user.activity is None:
        return None
    if user.activity.type.name == "competing":
        return f"Competing in **{user.activity.name}**"
    if user.activity.type.name == "listening":
        return f"Listening to **{user.activity.name}**"
    if user.activity.type.name == "playing":
        return f"Playing **{user.activity.name}**"
    if user.activity.type.name == "streaming":
        return f"Streaming **{user.activity.name}**"
    if user.activity.type.name == "watching":
        return f"Watching **{user.activity.name}**"
    if user.activity.type.name == "custom":
        return f"{user.activity.name}"
    if user.activity.type.name == "unknown":
        return "I dont know bro their status isn't getting detected"
    else:
        return None


class Info(commands.Cog):
    """All Information commands"""

    def __init__(self, bot: commands.Bot):
        self.bot: commands.Bot = bot

    @commands.group(name="avatar", description="Shows a user's avatar", invoke_without_command=True)
    @commands.bot_has_permissions(external_emojis=True, embed_links=True, attach_files=True)
    async def avatar(self, ctx: commands.Context, user: Optional[discord.User] = None):
        """Shows a user's avatar"""
        user = user or ctx.author
        await ctx.reply(
            embed=AiEmbed.default(ctx, title=f"{user.name}'s avatar").set_image(url=f"{user.display_avatar.url}")
        )

    @avatar.command(name="server", description="SHows a user's server avatar")
    @commands.bot_has_permissions(external_emojis=True, embed_links=True, attach_files=True)
    async def srv_avatar(self, ctx: commands.Context, user: Optional[discord.Member] = None):
        user = user or ctx.author
        if not user.guild_avatar:
            return await ctx.reply(f"`{user}` does not have a server avatar")
        await ctx.reply(
            embed=AiEmbed.default(ctx, title=f"{user.name}'s server avatar").set_image(url=f"{user.guild_avatar.url}")
        )

    @commands.command(name="serverinfo", description="Shows info about the server")
    @commands.bot_has_permissions(external_emojis=True, embed_links=True, attach_files=True)
    async def serverinfo(self, ctx: commands.Context):
        """Shows info about the server"""

        guild = ctx.guild

        #############################################
        #                                           #
        #        Creating the main embed            #
        #                                           #
        #############################################
        embed_values = [
            f"- **ID -** `{guild.id}`",
            f"- **Owner -** {guild.owner.mention} (`{guild.owner_id}`)",
            f"- **Members -** {guild.member_count}",
            f"- **Emojis -** {len(guild.emojis)}",
            f"- **Stickers -** {len(guild.stickers)}",
            f"- **Created on -** <t:{round(guild.created_at.timestamp())}:D> (<t:{round(guild.created_at.timestamp())}:R>)",
            f"- **Channels -** {len(guild.channels)}",
            f"    - **Categories -** {len(guild.categories)}",
            f"    - **Text Channels -** {len(guild.text_channels)}",
            f"    - **Voice Channels -** {len(guild.voice_channels)}",
            f"    - **Forum Channels -** {len(guild.forums)}",
            f"    - **Stage Channels -** {len(guild.stage_channels)}",
            f"    - **Forums Channels -** {len(guild.forums)}",
        ]

        embed = AiEmbed.default(ctx, title=guild.name, description=guild.description)
        embed.add_field(
            name="Information",
            value="\n".join(embed_values),
            inline=False,
        )
        if guild.icon:
            embed.set_thumbnail(url=guild.icon.url)
        if guild.banner:
            embed.set_image(url=guild.banner.url)
        if not guild.banner and guild.splash:
            embed.set_image(url=guild.splash.url)

        #############################################
        #                                           #
        #        Creating the boost embed           #
        #                                           #
        #############################################
        boostembed = None
        if guild.premium_subscribers:
            subscribers_sorted = [a for a in sorted(guild.premium_subscribers, key=lambda m: m.premium_since)]
            user_count = len(guild.premium_subscribers)
            center_number = len(subscribers_sorted) / 2
            users_per_page = 5
            half_range = (users_per_page - 1) // 2
            start_number = max(center_number - half_range, 1)
            end_number = min(center_number + half_range + 1, user_count + 1)
            listing = ["```py"]
            for i in range(start_number, end_number):
                subscriber = subscribers_sorted[i - 1]
                t = humanize.naturaldelta(
                    datetime.now().replace(tzinfo=None) - subscriber.premium_since.replace(tzinfo=None)
                )
                listing.append(f"{i}. {str(subscriber)}")
                listing.append(f"  + Since {t} | {subscriber.premium_since.strftime('%H:%M:%S, %d/%m/%Y')}")
            listing.append("```")
            stringthing = "\n".join(listing)
            listing = [
                f"- **Tier -** Level `{guild.premium_tier}`",
                f"- **Boosts -** `{guild.premium_subscription_count}`",
            ]
            if guild.premium_subscriber_role:
                listing.append(
                    f"- **Booster role -** {guild.premium_subscriber_role.mention} (`{guild.premium_subscriber_role.id}`)"
                )
            boostembed = AiEmbed.default(
                ctx,
                title="Nitro Boost Status and Information",
                description="\n".join(listing),
            )
            boostembed.add_field(name="Boosters", value=stringthing)

        #############################################
        #                                           #
        #        Creating the user embed            #
        #                                           #
        #############################################
        user = ctx.author

        rolelist = [role.mention for role in user.roles if not role.is_default()]
        rolelist.reverse()
        if len(rolelist) <= 3:
            role_string = ", ".join(rolelist)
        else:
            role_string = ", ".join(rolelist[:3]) + f" +{len(rolelist) - 3} more roles"

        if not role_string:
            role_string = "You have no roles"

        usercolor = user.color if user.color != discord.Colour.default() else None
        badges = []
        if user.id in self.bot.owner_ids:
            badges.append("<:console512:1191472017912897738>")
        if user.bot:
            badges.append("<:1646discordboten:1191473574565924964>")

        members_sorted = sorted(guild.members, key=lambda m: m.joined_at)
        center_number = members_sorted.index(ctx.author) + 1

        uembed = AiEmbed.default(
            ctx,
            title=f"{user} {' '.join(badges) if badges else ''}",
            description=statusxD(user) or "A very cool discord user!",
            colour=usercolor,
        )
        uembed.add_field(
            name="ℹ️ General Information",
            value=f"- **Nickname -** {user.display_name}\n"
            f"- **ID -** `{user.id}`\n"
            f"- **Created at -** <t:{round(user.created_at.timestamp())}:F>\n"
            f"- **Joined at -** <t:{round(user.joined_at.timestamp())}:F>\n"
            f"- **Join Position -** `{center_number}`\n"
            f"- **Roles -** {role_string}",
            inline=False,
        )
        if user.id in self.bot.artist:
            uembed.add_field(
                name="Acknoledgements",
                value=f"- <:Emoji:1199098396468850799> This user is one of the amazing artists of this bot! (They draw cool stuff)",
            )
        uembed.set_thumbnail(url=user.display_avatar.url)
        if user.banner:
            uembed.set_image(url=user.banner)

        #############################################
        #                                           #
        #        Creating the random embeds         #
        #                                           #
        #############################################
        avembed = (
            AiEmbed.default(ctx, title=f"{guild.name}'s icon").set_image(url=f"{guild.icon.url}") if guild.icon else None
        )
        bannerembed = (
            AiEmbed.default(ctx, title=f"{guild.name}'s banner").set_image(url=f"{guild.banner.url}")
            if guild.banner
            else None
        )

        msg = await ctx.reply(embed=embed)
        view = ServerinfoView(ctx, msg, embed, boostembed, uembed, avembed, bannerembed)
        await msg.edit(view=view)

    @commands.command(name="botinfo", description="Shows information about the bot")
    @commands.bot_has_permissions(external_emojis=True, embed_links=True, attach_files=True)
    async def botinfo(self, ctx: commands.Context):
        """Shows information about the bot"""
        bot = ctx.bot

        botinfolisting = [
            f"- **Command Prefix -** `e!`",
            f"- **Commands -** `{len(bot.all_commands)}`",
            f"- **Servers - **`{len(bot.guilds)}`",
            f"- **Users -** `{len(bot.users)}`",
            f"- **Ping -** `{round(bot.latency * 1000)}ms`",
            f"- **Created at -** <t:{round(bot.user.created_at.timestamp())}:F>",
            f"- **Last restart -** <t:{round(bot.load_time.timestamp())}:R>",
        ]
        botinfoembed = AiEmbed.default(ctx, title=f"{bot.user.name}", description=bot.description)
        botinfoembed.add_field(name="About", value="\n".join(botinfolisting))
        botinfoembed.set_thumbnail(url=bot.user.display_avatar.url)

        proc = psutil.Process()
        mem = proc.memory_full_info()
        syslisting = [
            f"- **Made with -** `Python 3` & `discord.py{discord.__version__}`",
            f"- **OS -** `{sys.platform}`",
            f"- **Physical Memory -** `{humanize.naturalsize(mem.rss)}`",
            f"- **Virtual Memory -** `{humanize.naturalsize(mem.vms)}`",
            f"- **Process Memory -** `{humanize.naturalsize(mem.uss)}`",
            f"- **PID -** `{proc.pid} ({proc.name()})`",
            f"- **Thread Count -** `{proc.num_threads()}`",
        ]
        sysembed = AiEmbed.default(ctx, title="System Information", description="\n".join(syslisting))

        teamembed = AiEmbed.default(ctx, title="Ely Support Team")
        teamembed.add_field(
            name="Developers",
            value="\n".join([str(f"- `{bot.get_user(a)}`") for a in bot.owner_ids]),
        )
        teamembed.add_field(
            name="Artists",
            value="\n".join([str(f"- `{bot.get_user(a)}`") for a in bot.artist]),
        )

        user = bot.user
        avembed = AiEmbed.default(ctx, title=f"{user.name}'s avatar").set_image(url=f"{user.display_avatar.url}")
        msg = await ctx.reply(embed=botinfoembed)
        view = BotinfoView(ctx, msg, botinfoembed, sysembed, teamembed, avembed)
        view.add_item(
            discord.ui.Button(
                label="Invite the bot",
                style=discord.ButtonStyle.url,
                url=discord.utils.oauth_url(bot.user.id),
            )
        )
        view.add_item(
            discord.ui.Button(
                label="Support Server",
                style=discord.ButtonStyle.url,
                url="https://discord.gg/hau6SZgRTF",
            )
        )
        await msg.edit(view=view)

    @commands.command(name="userinfo", description="Shows information about a user")
    @commands.bot_has_permissions(external_emojis=True, embed_links=True, attach_files=True)
    async def userinfo(self, ctx: commands.Context, user: Optional[discord.Member] = None):
        """Shows information about a user"""
        user = user or ctx.author

        rolelist = [role.mention for role in user.roles if not role.is_default()]
        rolelist.reverse()
        if len(rolelist) <= 3:
            role_string = ", ".join(rolelist)
        else:
            role_string = ", ".join(rolelist[:3]) + f" +{len(rolelist) - 3} more roles"

        if not role_string:
            role_string = "You have no roles"

        usercolor = user.color if user.color != discord.Colour.default() else None
        badges = []
        if user.id in self.bot.owner_ids:
            badges.append("<:console512:1191472017912897738>")
        if user.bot:
            badges.append("<:1646discordboten:1191473574565924964>")
        members_sorted = sorted(ctx.guild.members, key=lambda m: m.joined_at)
        center_number = members_sorted.index(ctx.author) + 1

        uembed = AiEmbed.default(
            ctx,
            title=f"{user} {' '.join(badges) if badges else ''}",
            description=statusxD(user) or "A very cool discord user!",
            colour=usercolor,
        )
        uembed.add_field(
            name="ℹ️ General Information",
            value=f"- **Nickname -** {user.display_name}\n"
            f"- **ID -** `{user.id}`\n"
            f"- **Created at -** <t:{round(user.created_at.timestamp())}:F>\n"
            f"- **Joined at -** <t:{round(user.joined_at.timestamp())}:F>\n"
            f"- **Join Position -** `{center_number}`\n"
            f"- **Roles -** {role_string}",
            inline=False,
        )
        if user.id in self.bot.artist:
            uembed.add_field(
                name="Acknoledgements",
                value=f"- <:Emilia:1208446673995440219> This user is one of the amazing artists of this bot! (They draw cool stuff)",
            )
        uembed.set_thumbnail(url=user.display_avatar.url)
        if user.banner:
            uembed.set_image(url=user.banner)
        msg = await ctx.reply(embed=uembed)
        view = userinfoView(user, ctx, msg)
        await msg.edit(view=view)

    @commands.command(name="roleinfo", description="Shows information about a role")
    @commands.bot_has_permissions(external_emojis=True, embed_links=True, attach_files=True)
    async def roleinfo(self, ctx: commands.Context, role: discord.Role):
        embed = AiEmbed.default(
            ctx,
            title=role.name + str(str(" " + role.unicode_emoji) if role.unicode_emoji else ""),
            colour=role.colour or None,
        )
        listing = [
            f"- **ID -** `{role.id}`",
            f"- **Created On -** <t:{round(role.created_at.timestamp())}:D> (<t:{round(role.created_at.timestamp())}:R>)",
            f"- **Hoisted -** {'Yes' if role.hoist is True else 'No'}",
            f"- **Position -** {role.position}",
            f"- **Members -** {len(role.members)}",
        ]
        embed.description = "\n".join(listing)
        embed.set_thumbnail(url=role.display_icon or None)
        msg = await ctx.reply(embed=embed)
        view = roleinfoView(role, ctx, msg)
        await msg.edit(view=view)

    @commands.command(name="define", description="Shows defination of a given word")
    @commands.bot_has_permissions(external_emojis=True, embed_links=True, attach_files=True)
    async def define(self, ctx: commands.Context, word: str):
        async with aiohttp.ClientSession() as session:
            r = await session.get(f"https://api.dictionaryapi.dev/api/v2/entries/en/{word}")
            data = await r.read()
            await session.close()
        if r.status != 200:
            return await ctx.reply("No definitions found.")
        data = data.decode()
        data = json.loads(data)
        data = data[0]
        embed = AiEmbed.default(
            ctx,
            title=data["word"],
            description=(f"- Phonetic : `{data['phonetic']}`" if "phonetic" in data.keys() else None),
            url=data["sourceUrls"][0] or None,
        )
        elist = []
        for mean in data["meanings"]:
            for mean1 in mean["definitions"]:
                listing = [f"- {mean1['definition']}", f" - `{mean['partOfSpeech']}`"]
                if "example" in mean1.keys():
                    listing.append(f"- **Example**")
                    listing.append(f" - `{mean1['example']}`")
                embeder = embed.copy()
                embeder.add_field(name=f"Definition", value="\n".join(listing), inline=False)
                elist.append(embeder)
        view = ElyPagination(elist, ctx)
        await view.start()


async def setup(bot: commands.Bot):
    await bot.add_cog(Info(bot))
