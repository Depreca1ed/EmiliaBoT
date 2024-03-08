import discord
from discord.ext import commands
from utils.Embed import AiEmbed
from typing import Optional
import traceback


def emiemiserver(ctx: commands.Context):
    if ctx.guild.id == 1178597884774580274:
        return True
    return False


class suggestionconfig(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)
        self.modal = discord.ui.Modal(title="Denial Reason")
        self.modal.descriptionin = discord.ui.TextInput(
            label="Your suggestion denial reason",
            placeholder="Enter your suggestion denial reason here. Discord markdowns are enabled",
            style=discord.TextStyle.long,
            required=True,
            max_length=1800,
            min_length=5,
        )
        self.modal.add_item(self.modal.descriptionin)
        self.modal.on_submit = self.on_modal_submit

    async def on_modal_submit(self, interaction: discord.Interaction):
        await interaction.client.db.suggestions.find_one_and_update(
            {"_id": interaction.message.id},
            {"$set": {"Status": "Denied", "Reason": str(self.modal.descriptionin)}},
        )
        dbdata = await interaction.client.db.suggestions.find_one({"_id": interaction.message.id})
        user = await interaction.client.fetch_user(dbdata["User"])
        guild = (
            (await interaction.client.fetch_guild(dbdata["Guild"])).name
            if isinstance(dbdata["Guild"], int)
            else "Direct Messages"
        )
        embed = interaction.message.embeds[0]
        embed.clear_fields()
        embed.add_field(
            name="Suggestion's information",
            value=f"- Status - `{dbdata['Status']}`\n- Suggester - {str(user)} (`{user.id}`)\n- From - {guild}",
        )
        embed.add_field(name="Denial Reason", value=self.modal.descriptionin, inline=False)
        await interaction.message.clear_reactions()
        await interaction.response.edit_message(embed=embed, view=None)

    @discord.ui.button(label="Accept", style=discord.ButtonStyle.blurple, custom_id="AcceptSubButtonEmi")
    async def sugaccbutton(self, interaction: discord.Interaction, button):
        await interaction.client.db.suggestions.find_one_and_update(
            {"_id": interaction.message.id}, {"$set": {"Status": "Accepted"}}
        )
        dbdata = await interaction.client.db.suggestions.find_one({"_id": interaction.message.id})
        user = await interaction.client.fetch_user(dbdata["User"])
        guild = (
            (await interaction.client.fetch_guild(dbdata["Guild"])).name
            if isinstance(dbdata["Guild"], int)
            else "Direct Messages"
        )
        embed = interaction.message.embeds[0]
        embed.clear_fields()
        embed.add_field(
            name="Suggestion's information",
            value=f"- Status - `{dbdata['Status']}`\n- Suggester - {str(user)} (`{user.id}`)\n- From - {guild}",
        )
        await interaction.message.clear_reactions()
        await interaction.response.edit_message(embed=embed, view=None)

    @discord.ui.button(
        label="Under Review",
        style=discord.ButtonStyle.blurple,
        custom_id="ReviewSubButtonEmi",
    )
    async def sugrevbutton(self, interaction, button):
        await interaction.client.db.suggestions.find_one_and_update(
            {"_id": interaction.message.id}, {"$set": {"Status": "Under Review"}}
        )
        dbdata = await interaction.client.db.suggestions.find_one({"_id": interaction.message.id})
        user = await interaction.client.fetch_user(dbdata["User"])
        guild = (
            (await interaction.client.fetch_guild(dbdata["Guild"])).name
            if isinstance(dbdata["Guild"], int)
            else "Direct Messages"
        )
        embed = interaction.message.embeds[0]
        embed.clear_fields()
        embed.add_field(
            name="Suggestion's information",
            value=f"- Status - `{dbdata['Status']}`\n- Suggester - {str(user)} (`{user.id}`)\n- From - {guild}",
        )
        embed.add_field(name="Note", value="The buttons are for moderators only")
        await interaction.response.edit_message(embed=embed, view=self)

    @discord.ui.button(
        label="Implementing",
        style=discord.ButtonStyle.blurple,
        custom_id="ImplementingSugButtonEmi",
    )
    async def sugimpbutton(self, interaction, button):
        await interaction.client.db.suggestions.find_one_and_update(
            {"_id": interaction.message.id}, {"$set": {"Status": "Implementing"}}
        )
        dbdata = await interaction.client.db.suggestions.find_one({"_id": interaction.message.id})
        user = await interaction.client.fetch_user(dbdata["User"])
        guild = (
            (await interaction.client.fetch_guild(dbdata["Guild"])).name
            if isinstance(dbdata["Guild"], int)
            else "Direct Messages"
        )
        embed = interaction.message.embeds[0]
        embed.clear_fields()
        embed.add_field(
            name="Suggestion's information",
            value=f"- Status - `{dbdata['Status']}`\n- Suggester - {str(user)} (`{user.id}`)\n- From - {guild}",
        )
        embed.add_field(name="Note", value="The buttons are for moderators only")
        await interaction.response.edit_message(embed=embed, view=self)

    @discord.ui.button(label="Denied", style=discord.ButtonStyle.blurple, custom_id="DeniedSugButtonEmi")
    async def sugdenbutton(self, interaction, button):
        await interaction.response.send_modal(self.modal)

    async def interaction_check(self, interaction: discord.Interaction[discord.Client]) -> bool:
        if interaction.user.id in interaction.client.owner_ids:
            return True
        await interaction.response.send_message("Only moderators can use the buttons", ephemeral=True)
        return False


class suggestionview(discord.ui.View):
    def __init__(self, ctx: commands.Context, message: discord.Message, suggestion: str):
        super().__init__(timeout=1200.0)
        self.ctx: commands.Context = ctx
        self.message: discord.Message = message
        self.suggestion: str = suggestion
        self.notified: bool = False
        self.clear_items()
        if self.suggestion is None:
            self.add_item(self.sugbutton)
            self.modal = discord.ui.Modal(title="Suggest")
            self.modal.titlein = discord.ui.TextInput(
                label="Your suggestion title",
                placeholder="Enter your suggestion title here",
                style=discord.TextStyle.short,
                required=True,
                max_length=100,
                min_length=3,
            )
            self.modal.add_item(self.modal.titlein)
            self.modal.descriptionin = discord.ui.TextInput(
                label="Your suggestion description",
                placeholder="Enter your suggestion description here. Discord markdowns are enabled",
                style=discord.TextStyle.long,
                required=True,
                max_length=1800,
                min_length=5,
            )
            self.modal.add_item(self.modal.descriptionin)
            self.modal.on_submit = self.on_modal_submit
            return
        if self.suggestion is not None:
            self.suggestembed = AiEmbed.default(
                self.ctx,
                title=f"{str(self.ctx.author)}'s Suggestion",
                description=f"### Suggestion\n\n{self.suggestion}",
            )
            self.suggestembed.add_field(
                name="Before you confirm",
                value="Please make sure your suggestion follows the discord Terms of Service and Privacy Policy. A semi-exact copy of this embed will be sent to the developers of the Ely, the bot and to you in your DMs, if you have them enabled. Make sure everything you wanted to suggest is clearly stated. Once you're done, click the confirm button and the suggestion will be sent",
            )
            self.add_item(self.confirmbutton)
            self.add_item(self.deny_button)
            return

    @discord.ui.button(
        label="Suggest",
        emoji="<:arrow:1199090483096453161>",
        style=discord.ButtonStyle.blurple,
    )
    async def sugbutton(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_modal(self.modal)

    async def on_modal_submit(self, interaction: discord.Interaction):
        embed = AiEmbed.default(
            self.ctx,
            title=f"{str(self.ctx.author)}'s Suggestion",
            description=f"### {self.modal.titlein}\n\n{self.modal.descriptionin}",
        )
        embed.add_field(
            name="Before you confirm",
            value="Please make sure your suggestion follows the discord Terms of Service and Privacy Policy. A semi-exact copy of this embed will be sent to the developers of the Ely, the bot and to you in your DMs, if you have them enabled. Make sure everything you wanted to suggest is clearly stated. Once you're done, click the confirm button and the suggestion will be sent",
        )
        self.remove_item(self.sugbutton)
        self.add_item(self.confirmbutton)
        self.add_item(self.deny_button)
        self.suggestembed = embed
        await interaction.response.edit_message(content=None, embed=embed, view=self)

    @discord.ui.button(
        emoji="<:checkedcheckbox512:1191470926827630662>",
        style=discord.ButtonStyle.green,
    )
    async def confirmbutton(self, interaction, button):
        embed = self.suggestembed
        embed.clear_fields()
        statusvar = "Unchecked"
        embed.add_field(
            name="Suggestion's information",
            value=f"- Status - `{statusvar}`\n- Suggester - {str(self.ctx.author)} (`{self.ctx.author.id}`)\n- From - {self.ctx.guild if self.ctx.guild else 'Direct Messages'}",
        )
        embed.add_field(name="Note", value="The buttons are for moderators only")
        cch = self.ctx.bot.get_channel(1212445730615337040) or await self.ctx.bot.fetch_channel(1212445730615337040)
        msgdb = await cch.send(embed=embed, view=suggestionconfig())
        await msgdb.add_reaction("<:checkedcheckbox512:1191470926827630662>")
        await msgdb.add_reaction("<:xmark4512:1191470897811431465>")
        await self.ctx.bot.db.suggestions.insert_one(
            {
                "_id": msgdb.id,
                "Status": statusvar,
                "User": self.ctx.author.id,
                "Guild": self.ctx.guild.id if self.ctx.guild else "Direct Messages",
                "Notified": self.notified,
            }
        )
        await interaction.response.edit_message(content="Successfully sent the suggestion", embed=None, view=None)
        self.stop()

    @discord.ui.button(emoji="<:xmark4512:1191470897811431465>", style=discord.ButtonStyle.red)
    async def deny_button(self, interaction, button):
        await interaction.response.edit_message(
            content="Cancelled",
            embed=None,
            view=None,
        )
        self.stop()

    async def on_timeout(self):
        await self.message.edit(view=None)
        self.stop()

    async def on_error(self, inter, error, item):
        if inter.response.is_done():
            func = inter.followup.send
        else:
            func = inter.response.send_message
        errormsg = "```py\n" + "".join(traceback.format_exception(type(error), error, error.__traceback__)) + "```"
        return await func(f"Error(Send this to developer):\n{str(errormsg)}", ephemeral=False)

    async def interaction_check(self, interaction):
        if interaction.user.id == self.ctx.author.id:
            return True
        await interaction.response.send_message(
            "This is not your Interaction!",
            ephemeral=True,
        )
        return False


class EmiEmi(commands.Cog):
    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot

    @commands.Cog.listener()
    async def on_member_join(self, member: discord.Member):
        if not member or member.guild.id != 1178597884774580274:
            return
        if member.bot is True:
            role = member.guild.get_role(1212439683603107980)
            await member.add_roles(role)
            return
        channel = self.bot.get_channel(1212366162063794176) or await self.bot.fetch_channel(1212366162063794176)
        embed = AiEmbed(
            title=f"{str(member)} Joined!",
            description=f"Welcome to **{member.guild.name}**. Have fun! <:EmiliaRee:1208447880537571338><:EmiliaRee:1208447880537571338><:EmiliaRee:1208447880537571338>",
        )
        embed.set_thumbnail(url="https://i.imgur.com/MRPkCRu.jpeg")
        return await channel.send(content=member.mention, embed=embed)

    @commands.Cog.listener()
    async def on_member_remove(self, member: discord.Member):
        if not member or member.guild.id != 1178597884774580274:
            return
        channel = self.bot.get_channel(1212366162063794176) or await self.bot.fetch_channel(1212366162063794176)
        return await channel.send(content=f"Goodbye **{str(member)}**. We will miss you <:EmiliaCry:1208447886338170890>")

    @commands.group(
        name="emi", description="All commands for the beautifull server called EmiEmi", invoke_without_command=True
    )
    @commands.check(emiemiserver)
    async def emi(self, ctx: commands.Context):
        await ctx.send_help(ctx.command)

    @emi.command(name="addbot", description="To request addition of a bot")
    @commands.check(emiemiserver)
    async def addbot(self, ctx: commands.Context, bot: discord.User):
        if bot.id in [mem.id for mem in ctx.guild.members]:
            return await ctx.reply("Already in the server.")
        bot = await self.bot.fetch_user(bot.id)
        if not bot or bot.bot is False:
            return await ctx.reply("This user is not a bot.")
        desc = [
            f"- **Requested By -** {ctx.author}",
            f"- **Name -** [{bot.name}]({discord.utils.oauth_url(bot.id)})",
        ]
        embed = AiEmbed.default(ctx, title="Addition of a bot requested", description="\n".join(desc))
        embed.set_thumbnail(url=bot.avatar.url if bot.avatar else None)
        channel = self.bot.get_channel(1212435838680572014) or await self.bot.fetch_channel(1212435838680572014)
        await channel.send(embed=embed)
        return await ctx.reply(content="Done! The bot will be reviewed by our staff team and may get added to the server")

    @emi.command(name="suggest", description="Give suggestions for EmiEmi the server")
    @commands.check(emiemiserver)
    async def suggest(self, ctx, *, message: Optional[str] = None):
        if message and len(message) > 1800:
            return await ctx.reply("The suggestion exceeds the required character limit")
        if ctx.message.reference is None and message is None:
            msg = await ctx.reply("Click the button below to write your suggestion")
            view = suggestionview(ctx, msg, message)
            return await msg.edit(view=view)
        embed = AiEmbed.default(
            ctx,
            title=f"{str(ctx.author)}'s Suggestion",
            description=f"### Suggestion\n\n{message}",
        )
        embed.add_field(
            name="Before you confirm",
            value="Please make sure your suggestion follows the discord Terms of Service and Privacy Policy. A semi-exact copy of this embed will be sent to the developers of the Ely, the bot and to you in your DMs, if you have them enabled. Make sure everything you wanted to suggest is clearly stated. Once you're done, click the confirm button and the suggestion will be sent",
        )
        msg: discord.Message = await ctx.reply(embed=embed)
        view = suggestionview(ctx, msg, message)
        return await msg.edit(view=view)


async def setup(bot: commands.Bot):
    await bot.add_cog(EmiEmi(bot))
