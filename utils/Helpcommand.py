from typing import Any, List, Mapping, Callable
import discord
from discord.ext import commands
from utils.Embed import AiEmbed
import inspect
from jishaku import codeblocks


class ElyPagination(discord.ui.View):
    def __init__(self, cogs, ctx):
        super().__init__(timeout=500)
        self.cogs = cogs
        self.ctx: commands.Context = ctx
        self.index = 0
        self.embeds: List[discord.Embed] = []
        self.dictforcogs: Mapping[str, List[discord.Embed]] = {}
        self.cogselect.placeholder = "Select a category"
        for a in [self.first_page, self.prev_page, self.next_page, self.last_page]:
            a.disabled = True

    async def start(self, cogs: List[commands.Cog], ctx, msg, help_command):
        self.basembed = msg.embeds[0]
        self.remove_item(self.cogselect)
        self.cogs = cogs
        self.ctx = ctx
        for cog in self.cogs:
            if cog and await help_command.filter_commands(cog.get_commands(), sort=True):
                embeds = [
                    AiEmbed.default(
                        self.ctx,
                        title=getattr(cog, "qualified_name", "No Category"),
                        description="\n".join(
                            f"- `{help_command.get_command_signature(cmd)}` - {getattr(cmd, 'description', 'No Category')}"
                            for cmd in cmds
                        ),
                    )
                    for cmds in discord.utils.as_chunks(await help_command.filter_commands(cog.get_commands(), sort=True), 4)
                ]
                self.dictforcogs[getattr(cog, "qualified_name", "No Category")] = embeds
                self.cogselect.add_option(
                    label=getattr(cog, "qualified_name", "No Category"),
                    description=getattr(cog, "description", "No description"),
                )
        self.add_item(self.cogselect)
        self.message = await msg.edit(view=self)

    async def startforgroup(self, group: commands.Group, ctx, basembed, help_command):
        self.remove_item(self.cogselect)
        self.ctx = ctx
        embed: AiEmbed = basembed
        if not group or not await help_command.filter_commands(list(group.commands), sort=True):
            return
        self.embeds = []
        setsofcommands = [
            a for a in discord.utils.as_chunks(await help_command.filter_commands(list(group.commands), sort=True), 4)
        ]
        for listofcommands in setsofcommands:
            embedforreal = AiEmbed.default(help_command.context, title=embed.title, description=embed.description)
            for i, e in enumerate(embed.fields):
                embed.add_field(name=i, value=e)
            embedforreal.add_field(
                name="Subcommands",
                value="\n".join(
                    (
                        f"- `{help_command.get_command_signature(cmd)}` - {getattr(cmd, 'description', 'No description') or 'No description'}"
                        for cmd in listofcommands
                    )
                ),
            )
            self.embeds.append(embedforreal)
            del embedforreal
        self.basembed = self.embeds[0]
        for i, embed in enumerate(self.embeds):
            embed.set_footer(text=f"Requested by {str(self.ctx.author)}" + " | " + f"Page {i+1} of {len(self.embeds)}")
        await self._update_state()
        self.message = await ctx.reply(embed=self.basembed, view=self)

    async def interaction_check(self, interaction):
        if interaction.user.id == self.ctx.author.id:
            return True
        await interaction.response.send_message("This is not your Interaction!", ephemeral=True)
        return False

    async def on_timeout(self):
        await self.message.edit(view=None)

    @discord.ui.select(placeholder="Select a category")
    async def cogselect(self, inter: discord.Interaction, select: discord.ui.Select):
        val = select.values[0]
        self.embeds = self.dictforcogs[val]
        for i, embed in enumerate(self.embeds):
            embed.set_footer(text=f"Requested by {str(self.ctx.author)}" + " | " + f"Page {i+1} of {len(self.embeds)}")

        self.index = 0
        await self._update_state()
        await inter.response.edit_message(embed=self.embeds[self.index], view=self)

    @discord.ui.button(emoji="<:pagiprevprev:1204333873740124170>", style=discord.ButtonStyle.grey)
    async def first_page(self, interaction: discord.Interaction, button: discord.ui.Button):
        self.index = 0
        await self._update_state()
        await interaction.response.edit_message(embed=self.embeds[self.index], view=self)

    @discord.ui.button(emoji="<:pagiprev:1204334051918614598>", style=discord.ButtonStyle.secondary)
    async def prev_page(self, interaction: discord.Interaction, button: discord.ui.Button):
        self.index -= 1
        await self._update_state()
        await interaction.response.edit_message(embed=self.embeds[self.index], view=self)

    @discord.ui.button(emoji="<:paginext:1204333968460226621>", style=discord.ButtonStyle.secondary)
    async def next_page(self, interaction: discord.Interaction, button: discord.ui.Button):
        self.index += 1
        await self._update_state()
        await interaction.response.edit_message(embed=self.embeds[self.index], view=self)

    @discord.ui.button(emoji="<:paginextnext:1204333711638921236>", style=discord.ButtonStyle.grey)
    async def last_page(self, interaction: discord.Interaction, button: discord.ui.Button):
        self.index = len(self.embeds) - 1
        await self._update_state()
        await interaction.response.edit_message(embed=self.embeds[self.index], view=self)

    async def _update_state(self):
        self.first_page.disabled = self.prev_page.disabled = self.index == 0
        self.last_page.disabled = self.next_page.disabled = self.index == len(self.embeds) - 1

    @discord.ui.button(emoji="<:pagistop:1204334166800470057>", style=discord.ButtonStyle.red, row=3)
    async def remove(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.edit_message(view=None)

    @discord.ui.button(emoji="<:emilia_sexy:1208447436536811592>", style=discord.ButtonStyle.blurple, row=3)
    async def homebutton(self, interaction: discord.Interaction, button: discord.ui.Button):
        if isinstance(self.cogs, commands.Group):
            self.index = 0
            await self._update_state()
            return await interaction.response.edit_message(embed=self.basembed, view=self)
        self.embeds = []
        self.index = 0
        await interaction.response.edit_message(embed=self.basembed, view=self)

    @discord.ui.button(emoji="<:info4512:1208451924211269693>", style=discord.ButtonStyle.blurple, row=3)
    async def infoabouthelpbutton(self, interaction: discord.Interaction, button: discord.ui.Button):
        embed = AiEmbed.default(self.ctx, title="How to use the help command?")
        embed.description = inspect.cleandoc(
            f"""
            ```py
            Use "{self.ctx.clean_prefix}help command" for more info on a command.
            Use "{self.ctx.clean_prefix}help category" for more info on a category.
            Use the dropdown menu below to select a category or module.```
            """
        )
        entries = (
            ("<argument>", "This means the argument is __**required**__."),
            ("[argument]", "This means the argument is __**optional**__."),
            ("[A|B]", "This means that it can be __**either A or B**__."),
            (
                "[argument...]",
                "This means you can have multiple arguments.\n"
                "Now that you know the basics, it should be noted that...\n"
                "__**You do not type in the brackets!**__",
            ),
        )

        for name, value in entries:
            embed.add_field(name=name, value=value, inline=False)
        if isinstance(self.cogs, commands.Group):
            for a in [self.first_page, self.prev_page, self.next_page, self.last_page]:
                a.disabled = True
            return await interaction.response.edit_message(embed=embed, view=self)
        self.embeds = []
        self.index = 0
        for a in [self.first_page, self.prev_page, self.next_page, self.last_page]:
            a.disabled = True
        await interaction.response.edit_message(embed=embed, view=self)


class MyHelpCommand(commands.HelpCommand):
    async def send_bot_help(
        self, mapping: Mapping[commands.Cog | None, List[commands.Command[Any, Callable[..., Any], Any]]]
    ) -> None:
        embed = AiEmbed.default(self.context, title="Help Menu", description=self.context.bot.description)
        listing = []
        for cog in mapping:
            if cog and await self.filter_commands(cog.get_commands(), sort=True):
                filtered = await self.filter_commands(cog.get_commands(), sort=True)
                listing.append(
                    f"- **{getattr(cog, 'qualified_name', 'No Category')} -** `{len(filtered)} {'commands' if len(filtered) > 1 else 'command'}`\n    - {getattr(cog, 'description', 'No description')}"
                )
        embed.add_field(name="<:folder:1208470227088834702> Modules", value="\n".join(listing), inline=False)
        embed.set_thumbnail(url=self.context.bot.user.avatar.url)
        msg = await self.context.reply(embed=embed)
        pagination = ElyPagination(self.context, mapping)
        return await pagination.start(mapping, self.context, msg, self)

    async def send_command_help(self, command: commands.Command[Any, Callable[..., Any], Any]) -> None:
        embed = AiEmbed.default(self.context, title=self.get_command_signature(command))
        embed.description = getattr(command, "description", "No description")
        embed.add_field(name="Usage", value=command.brief or "No usage has been written for this command yet", inline=False)
        return await self.context.reply(embed=embed)

    async def send_group_help(self, group: commands.Group[Any, Callable[..., Any], Any]) -> None:
        embed = AiEmbed.default(self.context, title=self.get_command_signature(group))
        embed.description = getattr(group, "description", "No description")
        embed.add_field(name="Usage", value=group.brief or "No usage has been written for this command yet", inline=False)
        view = ElyPagination(group, self.context)
        await view.startforgroup(group, self.context, embed, self)
