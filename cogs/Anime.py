from typing import List, Optional
import discord
from discord.ext import commands, tasks
from discord import app_commands
import aiohttp
import json
from datetime import datetime
import waifuim
from utils.Embed import AiEmbed
import re
import traceback


class SorPView(discord.ui.View):
    def __init__(self, ctx: commands.Context, message: discord.Message, req: str):
        super().__init__(timeout=500.0)
        self.ctx: commands.Context = ctx
        self.message: discord.Message = message
        self.smashers: List = []
        self.passers: List = []
        self.voted: List = []
        self.req: str = req

    @discord.ui.button(
        label="SMASH!",
        emoji="<:elysia_yes:1187106328355803156>",
        style=discord.ButtonStyle.green,
    )
    async def smash(self, interaction: discord.Interaction, button: discord.ui.Button):
        self.smashers.append(interaction.user)
        embed = interaction.message.embeds[0]
        self.voted.append(interaction.user.id)
        embed.description = f"<:elysia_yes:1187106328355803156> Smashers - {len(self.smashers)}\n<:elysia_no:1187109158785405058> Passers - {len(self.passers)}"
        await interaction.response.edit_message(embed=embed)

    @discord.ui.button(
        label="Pass...",
        emoji="<:elysia_no:1187109158785405058>",
        style=discord.ButtonStyle.red,
    )
    async def passbutton(self, interaction: discord.Interaction, button: discord.ui.Button):
        self.passers.append(interaction.user)
        embed = interaction.message.embeds[0]
        self.voted.append(interaction.user.id)
        embed.description = f"<:elysia_yes:1187106328355803156> Smashers - {len(self.smashers)}\n<:elysia_no:1187109158785405058> Passers - {len(self.passers)}"
        await interaction.response.edit_message(embed=embed)

    @discord.ui.button(emoji="🔁", style=discord.ButtonStyle.blurple)
    async def loopit(self, interaction: discord.Interaction, button: discord.ui.Button):
        self.passers: List = []
        self.smashers: List = []
        self.voted: List = []
        if self.req in ["neko", "shinobu", "megumin"]:
            async with aiohttp.ClientSession() as session:
                waifufrfr = await session.get(f"https://api.waifu.pics/sfw/{self.req}")
                await session.close()
            waifulnk = json.loads(await waifufrfr.text())
            embed = AiEmbed.default(
                self.ctx,
                title="Smash or Pass",
                description=f"<:elysia_yes:1187106328355803156> Smashers - {len(self.smashers)}\n<:elysia_no:1187109158785405058> Passers - {len(self.passers)}",
            )
            embed.set_image(url=str(waifulnk["url"]))
            return await interaction.response.edit_message(embed=embed)
        elif self.req in ["waifu", "maid", "raiden"]:
            embed = AiEmbed.default(
                self.ctx,
                title="Smash or Pass",
                description=f"<:elysia_yes:1187106328355803156> Smashers - {len(self.smashers)}\n<:elysia_no:1187109158785405058> Passers - {len(self.passers)}",
            )
            cli = waifuim.WaifuAioClient()
            waifu = await cli.search(
                included_tags=[self.req],
                excluded_tags=[
                    "ass",
                    "hentai",
                    "milf",
                    "oral",
                    "paizuri",
                    "ecchi",
                    "ero",
                ],
                is_nsfw=False,
            )
            embed.set_image(url=str(waifu.url))
            embed.colour = discord.Colour.from_str(waifu.dominant_color)
            await cli.close()
            return await interaction.response.edit_message(embed=embed)
        return await interaction.response.send_message("Send this to dep and call him an idiot")

    async def interaction_check(self, interaction: discord.Interaction):
        if (
            interaction.user.id != self.ctx.author.id
            and interaction.data["custom_id"] == [x.custom_id for x in self.children][2]
        ):
            await interaction.response.send_message(
                "Only the command initiator can cycle through waifus in this message.",
                ephemeral=True,
            )
            return False
        if (
            interaction.user.id == self.ctx.author.id
            and interaction.data["custom_id"] == [x.custom_id for x in self.children][2]
        ):
            return True
        if (
            interaction.user.id == self.ctx.author.id
            and interaction.data["custom_id"] == [x.custom_id for x in self.children][0]
            and interaction.user.id in self.voted
        ):
            await interaction.response.send_message(
                embed=AiEmbed.default(
                    self.ctx,
                    title="Smashers",
                    description=", ".join([str(usr) for usr in self.smashers]),
                ),
                ephemeral=True,
            )
            return False
        if (
            interaction.user.id == self.ctx.author.id
            and interaction.data["custom_id"] == [x.custom_id for x in self.children][1]
            and interaction.user.id in self.voted
        ):
            await interaction.response.send_message(
                embed=AiEmbed.default(
                    self.ctx,
                    title="Passers",
                    description=", ".join([str(usr) for usr in self.passers]),
                ),
                ephemeral=True,
            )
            return False
        elif interaction.user.id not in self.voted:
            return True
        await interaction.response.send_message(
            "Once you choose a path, you cannot go back to it. Its your duty to choose one path and one path only. Its a one time chance. Thats how life works.",
            ephemeral=True,
        )
        return False

    async def on_timeout(self):
        await self.message.edit(view=None)
        self.stop()

    async def on_error(self, inter: discord.Interaction, error: Exception, item: discord.ui.Item):
        if inter.response.is_done():
            func = inter.followup.send
        else:
            func = inter.response.send_message
        errormsg = "```py\n" + "".join(traceback.format_exception(type(error), error, error.__traceback__)) + "```"
        return await func(f"Error:\n{str(errormsg)}", ephemeral=False)


class AniSelect(discord.ui.Select):
    def __init__(self, animes: List, ctx: commands.Context):
        self.ctx: commands.Context = ctx
        self.animes: List = animes
        animesel = [
            (
                (str(a["title"] if len(a["title"]) <= 99 else (a["title"][:96] + "..."))),
                a["title_japanese"],
            )
            for a in self.animes
        ]
        options = []
        for anime, janime in animesel:
            options.append(discord.SelectOption(label=anime or janime, description=janime if anime else None))
        super().__init__(placeholder="Choose An Anime", options=options)

    async def callback(self, inter: discord.Interaction):
        for animel in self.animes:
            if animel["title"] == self.values[0]:
                anime = animel
        if len(self.view.children) == 2:
            self.view.remove_item(self.view.children[1])
        genres = anime["genres"] + anime["explicit_genres"] + anime["themes"] + anime["demographics"]
        genrestr = [f"{genre['name']}" for genre in genres]
        listing = [
            f"- **Japanese Title -** {anime['title_japanese'] or anime['title']}",
            f"- **Type -** {anime['type']}",
            f"- **Episodes -** {anime['episodes'] or 'Episode count not finalized'}",
            f"- **Status -** {anime['status']}",
            f" - **From -** {str('<t:'+str(round((datetime.strptime(anime['aired']['from'][:19], '%Y-%m-%dT%H:%M:%S')).timestamp()))+':D>') if anime['aired']['from'] else 'No time given'} {str('(<t:'+str(round((datetime.strptime(anime['aired']['from'][:19], '%Y-%m-%dT%H:%M:%S')).timestamp()))+':R>)') if anime['aired']['from'] else ''}",
            f" - **Till -** {str('<t:'+str(round((datetime.strptime(anime['aired']['to'][:19], '%Y-%m-%dT%H:%M:%S')).timestamp()))+':D>') if anime['aired']['to'] else 'No time given'} {str('(<t:'+str(round((datetime.strptime(anime['aired']['to'][:19], '%Y-%m-%dT%H:%M:%S')).timestamp()))+':R>)') if anime['aired']['to'] else ''}",
            f"- **Age Rating -** {anime['rating'] if anime['rating'] else 'No Rating'}",
            f"- **Review Score -** {anime['score'] if anime['score'] else 'No Score'} {str('(`'+str(anime['scored_by'])+'` voters)') if anime['scored_by'] else ''}",
            f"- **Rank -** `#{anime['rank'] if anime['rank'] else 'N/A'}`",
            f"- **Release Season & Year -** {anime['season'].title() if anime['season'] else 'Any Season'} in {anime['year'] if anime['year'] else 'No Year Given'}",
            f"- **Broadcast -** {anime['broadcast']['string'] if anime['broadcast'] else 'Undecided'}",
            f"- **Genres -** {', '.join(genrestr)}",
        ]
        embed = AiEmbed.default(self.ctx, title=anime["title"], url=anime["url"])
        if anime["synopsis"]:
            embed.description = anime["synopsis"]
        embed.add_field(name=f"About {anime['title']}", value="\n".join(listing), inline=False)
        listing2 = [f"- **Producers** :"]
        for producer in anime["producers"]:
            listing2.append(f" - [{producer['name']}]({producer['url']})")
        listing2.append(f"- **Licensors** :")
        for lincensor in anime["licensors"]:
            listing2.append(f" - [{lincensor['name']}]({lincensor['url']})")
        listing2.append(f"- **Studios** :")
        for studio in anime["studios"]:
            listing2.append(f" - [{studio['name']}]({studio['url']})")
        embed.add_field(name="Commercial Info", value="\n".join(listing2), inline=False)
        if anime["trailer"]["youtube_id"]:
            self.view.add_item(
                discord.ui.Button(
                    label="Anime Trailer",
                    style=discord.ButtonStyle.url,
                    url=anime["trailer"]["url"],
                    emoji="<:youtube:1189236809021005844>",
                )
            )
            embed.set_image(url=anime["trailer"]["images"]["maximum_image_url"])
        embed.set_thumbnail(url=anime["images"]["webp"]["large_image_url"] if anime["images"] else None)
        await inter.response.edit_message(embed=embed, view=self.view)


class MangaSelect(discord.ui.Select):
    def __init__(self, animes: List, ctx: commands.Context):
        self.ctx: commands.Context = ctx
        self.animes: List = animes
        animesel = [
            (
                (str(a["title"] if len(a["title"]) <= 99 else (a["title"][:96] + "..."))),
                a["title_japanese"],
            )
            for a in self.animes
        ]
        animesel = list(set(animesel))
        options = []
        for anime, janime in animesel:
            options.append(discord.SelectOption(label=anime or janime, description=janime if anime else None))
        super().__init__(placeholder="Choose A Manga", options=options)

    async def callback(self, inter: discord.Interaction):
        for animel in self.animes:
            if animel["title"] == self.values[0]:
                anime = animel
        if len(self.view.children) == 2:
            self.view.remove_item(self.view.children[1])
        genres = anime["genres"] + anime["explicit_genres"] + anime["themes"] + anime["demographics"]
        genrestr = [f"{genre['name']}" for genre in genres]
        listing = [
            f"- **Japanese Title -** {anime['title_japanese'] or anime['title']}",
            f"- **Type -** {anime['type']}",
            f"- **Chapters -** {anime['chapters'] or 'Chapter count not finalized'}",
            f"- **Volumes -** {anime['volumes'] or 'Volume count not finalized'}",
            f"- **Status -** {anime['status']}",
            f" - **From -** {str('<t:'+str(round((datetime.strptime(anime['published']['from'][:19], '%Y-%m-%dT%H:%M:%S')).timestamp()))+':D>') if anime['published']['from'] else 'No time given'} {str('(<t:'+str(round((datetime.strptime(anime['published']['from'][:19], '%Y-%m-%dT%H:%M:%S')).timestamp()))+':R>)') if anime['published']['from'] else ''}",
            f" - **Till -** {str('<t:'+str(round((datetime.strptime(anime['published']['to'][:19], '%Y-%m-%dT%H:%M:%S')).timestamp()))+':D>') if anime['published']['to'] else 'No time given'} {str('(<t:'+str(round((datetime.strptime(anime['published']['to'][:19], '%Y-%m-%dT%H:%M:%S')).timestamp()))+':R>)') if anime['published']['to'] else ''}",
            f"- **Review Score -** {anime['score'] if anime['score'] else 'No Score'} {str('(`'+str(anime['scored_by'])+'` voters)') if anime['scored_by'] else ''}",
            f"- **Rank -** `#{anime['rank'] if anime['rank'] else 'N/A'}`",
            f"- **Genres -** {', '.join(genrestr)}",
        ]
        embed = AiEmbed.default(self.ctx, title=anime["title"], url=anime["url"])
        if anime["synopsis"]:
            embed.description = anime["synopsis"]
        embed.add_field(name=f"About {anime['title']}", value="\n".join(listing), inline=False)
        listing2 = [f"- **Authors** :"]
        for producer in anime["authors"]:
            listing2.append(f" - [{producer['name']}]({producer['url']})")
        embed.add_field(name="Commercial Info", value="\n".join(listing2), inline=False)
        embed.set_image(url=anime["images"]["webp"]["large_image_url"] if anime["images"] else None)
        await inter.response.edit_message(embed=embed, view=self.view)


class animecmdview(discord.ui.View):
    def __init__(self, animes: List, ctx: commands.Context, message: discord.Message):
        super().__init__(timeout=500.0)
        self.ctx: commands.Context = ctx
        self.message: discord.Message = message
        self.add_item(AniSelect(animes, ctx))

    async def on_timeout(self):
        await self.message.edit(view=None)
        self.stop()

    async def interaction_check(self, interaction: discord.Interaction):
        if interaction.user.id == self.ctx.author.id:
            return True
        await interaction.response.send_message(
            "This is not your Interaction!",
            ephemeral=True,
        )
        return False

    async def on_error(self, inter: discord.Interaction, error: Exception, item: discord.ui.Item):
        if inter.response.is_done():
            func = inter.followup.send
        else:
            func = inter.response.send_message
        errormsg = "```py\n" + "".join(traceback.format_exception(type(error), error, error.__traceback__)) + "```"
        return await func(f"Error(Send this to developer):\n{str(errormsg)}", ephemeral=False)


class mangacmdview(discord.ui.View):
    def __init__(self, animes: List, ctx: commands.Context, message: discord.Message):
        super().__init__(timeout=500.0)
        self.ctx: commands.Context = ctx
        self.message: discord.Message = message
        self.add_item(MangaSelect(animes, ctx))

    async def on_timeout(self):
        await self.message.edit(view=None)
        self.stop()

    async def interaction_check(self, interaction: discord.Interaction):
        if interaction.user.id == self.ctx.author.id:
            return True
        await interaction.response.send_message(
            "This is not your Interaction!",
            ephemeral=True,
        )
        return False

    async def on_error(self, inter: discord.Interaction, error: Exception, item: discord.ui.Item):
        if inter.response.is_done():
            func = inter.followup.send
        else:
            func = inter.response.send_message
        errormsg = "```py\n" + "".join(traceback.format_exception(type(error), error, error.__traceback__)) + "```"
        return await func(f"Error(Send this to developer):\n{str(errormsg)}", ephemeral=False)


class Anime(commands.Cog):
    """All Anime related commands"""

    def __init__(self, bot: commands.Bot):
        self.bot: commands.Bot = bot

    @commands.command(name="anime", description="Shows description about a given anime")
    @commands.bot_has_permissions(external_emojis=True, embed_links=True, attach_files=True)
    async def animecmd(self, ctx: commands.Context, *, name: str):
        """Shows description about a given anime"""
        name = re.sub(r"/", "", name)
        name = re.sub(r"&", "", name)
        async with aiohttp.ClientSession() as session:
            data = await session.get(f"https://api.jikan.moe/v4/anime?q={name}&sfw=true&type=tv")
            data = await data.json()
            await session.close()
        if data["pagination"]["items"]["total"] == 0:
            return await ctx.reply(
                embed=AiEmbed.default(
                    ctx,
                    title="Sorry!",
                    description=f"Unfortunately, there are no animes with the name `{name}`. Perhaps you should try making it simpler",
                    colour=discord.Colour.red(),
                )
            )
        animes = data["data"]
        anime = animes[0]
        genres = anime["genres"] + anime["explicit_genres"] + anime["themes"] + anime["demographics"]
        genrestr = [f"{genre['name']}" for genre in genres]
        listing = [
            f"- **Japanese Title -** {anime['title_japanese'] or anime['title']}",
            f"- **Type -** {anime['type']}",
            f"- **Episodes -** {anime['episodes'] or 'Episode count not finalized'}",
            f"- **Status -** {anime['status']}",
            f" - **From -** {str('<t:'+str(round((datetime.strptime(anime['aired']['from'][:19], '%Y-%m-%dT%H:%M:%S')).timestamp()))+':D>') if anime['aired']['from'] else 'No time given'} {str('(<t:'+str(round((datetime.strptime(anime['aired']['from'][:19], '%Y-%m-%dT%H:%M:%S')).timestamp()))+':R>)') if anime['aired']['from'] else ''}",
            f" - **Till -** {str('<t:'+str(round((datetime.strptime(anime['aired']['to'][:19], '%Y-%m-%dT%H:%M:%S')).timestamp()))+':D>') if anime['aired']['to'] else 'No time given'} {str('(<t:'+str(round((datetime.strptime(anime['aired']['to'][:19], '%Y-%m-%dT%H:%M:%S')).timestamp()))+':R>)') if anime['aired']['to'] else ''}",
            f"- **Age Rating -** {anime['rating'] if anime['rating'] else 'No Rating'}",
            f"- **Review Score -** {anime['score'] if anime['score'] else 'No Score'} {str('(`'+str(anime['scored_by'])+'` voters)') if anime['scored_by'] else ''}",
            f"- **Rank -** `#{anime['rank'] if anime['rank'] else 'N/A'}`",
            f"- **Release Season & Year -** {anime['season'].title() if anime['season'] else 'Any Season'} in {anime['year'] if anime['year'] else 'No Year Given'}",
            f"- **Broadcast -** {anime['broadcast']['string'] if anime['broadcast'] else 'Undecided'}",
            f"- **Genres -** {', '.join(genrestr)}",
        ]
        embed = AiEmbed.default(ctx, title=anime["title"], url=anime["url"])
        if anime["synopsis"]:
            embed.description = anime["synopsis"]
        embed.add_field(name=f"About {anime['title']}", value="\n".join(listing), inline=False)
        listing2 = [f"- **Producers** :"]
        for producer in anime["producers"]:
            listing2.append(f" - [{producer['name']}]({producer['url']})")
        listing2.append(f"- **Licensors** :")
        for lincensor in anime["licensors"]:
            listing2.append(f" - [{lincensor['name']}]({lincensor['url']})")
        listing2.append(f"- **Studios** :")
        for studio in anime["studios"]:
            listing2.append(f" - [{studio['name']}]({studio['url']})")
        embed.add_field(name="Commercial Info", value="\n".join(listing2), inline=False)
        msg = await ctx.reply(embed=embed)
        view = animecmdview(animes, ctx, msg)
        if anime["trailer"]["youtube_id"]:
            view.add_item(
                discord.ui.Button(
                    label="Anime Trailer",
                    style=discord.ButtonStyle.url,
                    url=anime["trailer"]["url"],
                    emoji="<:youtube:1189236809021005844>",
                )
            )
            embed.set_image(url=anime["trailer"]["images"]["maximum_image_url"])
        embed.set_thumbnail(url=anime["images"]["webp"]["large_image_url"] if anime["images"] else None)
        return await msg.edit(view=view)

    @commands.command(name="manga", description="Shows description about a given manga")
    @commands.bot_has_permissions(external_emojis=True, embed_links=True, attach_files=True)
    async def mangaecmd(self, ctx: commands.Context, *, name: str):
        """Shows description about a given manga"""
        name = re.sub(r"/", "", name)
        name = re.sub(r"&", "", name)
        async with aiohttp.ClientSession() as session:
            data = await session.get(f"https://api.jikan.moe/v4/manga?q={name}&sfw=true&type=manga")
            data = await data.json()
            await session.close()
        if data["pagination"]["items"]["total"] == 0:
            return await ctx.reply(
                embed=AiEmbed.default(
                    ctx,
                    title="Sorry!",
                    description=f"Unfortunately, there are no mangas with the name `{name}`. Perhaps you should try making it simpler",
                    colour=discord.Colour.red(),
                )
            )
        animes = data["data"]
        anime = animes[0]
        genres = anime["genres"] + anime["explicit_genres"] + anime["themes"] + anime["demographics"]
        genrestr = [f"{genre['name']}" for genre in genres]
        listing = [
            f"- **Japanese Title -** {anime['title_japanese'] or anime['title']}",
            f"- **Type -** {anime['type']}",
            f"- **Chapters -** {anime['chapters'] or 'Chapter count not finalized'}",
            f"- **Volumes -** {anime['volumes'] or 'Volume count not finalized'}",
            f"- **Status -** {anime['status']}",
            f" - **From -** {str('<t:'+str(round((datetime.strptime(anime['published']['from'][:19], '%Y-%m-%dT%H:%M:%S')).timestamp()))+':D>') if anime['published']['from'] else 'No time given'} {str('(<t:'+str(round((datetime.strptime(anime['published']['from'][:19], '%Y-%m-%dT%H:%M:%S')).timestamp()))+':R>)') if anime['published']['from'] else ''}",
            f" - **Till -** {str('<t:'+str(round((datetime.strptime(anime['published']['to'][:19], '%Y-%m-%dT%H:%M:%S')).timestamp()))+':D>') if anime['published']['to'] else 'No time given'} {str('(<t:'+str(round((datetime.strptime(anime['published']['to'][:19], '%Y-%m-%dT%H:%M:%S')).timestamp()))+':R>)') if anime['published']['to'] else ''}",
            f"- **Review Score -** {anime['score'] if anime['score'] else 'No Score'} {str('(`'+str(anime['scored_by'])+'` voters)') if anime['scored_by'] else ''}",
            f"- **Rank -** `#{anime['rank'] if anime['rank'] else 'N/A'}`",
            f"- **Genres -** {', '.join(genrestr)}",
        ]
        embed = AiEmbed.default(ctx, title=anime["title"], url=anime["url"])
        if anime["synopsis"]:
            embed.description = anime["synopsis"]
        embed.add_field(name=f"About {anime['title']}", value="\n".join(listing), inline=False)
        listing2 = [f"- **Authors** :"]
        for producer in anime["authors"]:
            listing2.append(f" - [{producer['name']}]({producer['url']})")
        embed.add_field(name="Commercial Info", value="\n".join(listing2), inline=False)
        msg = await ctx.reply(embed=embed)
        view = mangacmdview(animes, ctx, msg)
        embed.set_image(url=anime["images"]["webp"]["large_image_url"] if anime["images"] else None)
        return await msg.edit(view=view)

    @commands.command(name="waifu", description="Shows a picture of a...anime girl?")
    @commands.bot_has_permissions(external_emojis=True, embed_links=True, attach_files=True)
    async def waifu(self, ctx: commands.Context):
        """Shows a picture of a...anime girl?"""
        embed = AiEmbed.default(
            ctx,
            title="Smash or Pass",
            description="<:elysia_yes:1187106328355803156> Smashers - 0\n<:elysia_no:1187109158785405058> Passers - 0",
        )
        cli = waifuim.WaifuAioClient()
        waifu = await cli.search(
            included_tags=["waifu"],
            excluded_tags=["ass", "hentai", "milf", "oral", "paizuri", "ecchi", "ero"],
            is_nsfw=False,
        )
        embed.set_image(url=str(waifu.url))
        embed.colour = discord.Colour.from_str(waifu.dominant_color)
        await cli.close()
        msg = await ctx.reply(embed=embed)
        view = SorPView(ctx, msg, "waifu")
        return await msg.edit(view=view)

    @commands.command(name="maid", description="Shows a picture of a.... anime maid!!!!")
    @commands.bot_has_permissions(external_emojis=True, embed_links=True, attach_files=True)
    async def maid(self, ctx: commands.Context):
        """Shows a picture of a.... anime maid!!!!"""
        embed = AiEmbed.default(
            ctx,
            title="Smash or Pass",
            description="<:elysia_yes:1187106328355803156> Smashers - 0\n<:elysia_no:1187109158785405058> Passers - 0",
        )
        cli = waifuim.WaifuAioClient()
        waifu = await cli.search(
            included_tags=["maid"],
            excluded_tags=["ass", "hentai", "milf", "oral", "paizuri", "ecchi", "ero"],
            is_nsfw=False,
        )
        embed.set_image(url=str(waifu.url))
        embed.colour = discord.Colour.from_str(waifu.dominant_color)
        await cli.close()
        msg = await ctx.reply(embed=embed)
        view = SorPView(ctx, msg, "maid")
        return await msg.edit(view=view)

    @commands.command(name="raiden", description="Raiden Shogun.")
    @commands.bot_has_permissions(external_emojis=True, embed_links=True, attach_files=True)
    async def raiden(self, ctx: commands.Context):
        """Raiden Shogun."""
        embed = AiEmbed.default(
            ctx,
            title="Smash or Pass",
            description="<:elysia_yes:1187106328355803156> Smashers - 0\n<:elysia_no:1187109158785405058> Passers - 0",
        )
        cli = waifuim.WaifuAioClient()
        waifu = await cli.search(
            included_tags=["raiden-shogun"],
            excluded_tags=["ass", "hentai", "milf", "oral", "paizuri", "ecchi", "ero"],
            is_nsfw=False,
        )
        embed.set_image(url=str(waifu.url))
        embed.colour = discord.Colour.from_str(waifu.dominant_color)
        await cli.close()
        msg = await ctx.reply(embed=embed)
        view = SorPView(ctx, msg, "raiden-shogun")
        return await msg.edit(view=view)


async def setup(bot: commands.Bot):
    await bot.add_cog(Anime(bot))
