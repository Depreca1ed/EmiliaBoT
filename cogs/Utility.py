from typing import Literal, Union, NamedTuple, Optional, List
import discord
from discord.ext import commands
from utils.Embed import AiEmbed
import traceback


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
        if dbdata["Notified"] is True:
            await user.send(embed=embed)
        await interaction.response.edit_message(embed=embed, view=None)

    @discord.ui.button(label="Accept", style=discord.ButtonStyle.blurple, custom_id="AcceptSubButton")
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
        if dbdata["Notified"] is True:
            await user.send(embed=embed)
        await interaction.response.edit_message(embed=embed, view=None)

    @discord.ui.button(
        label="Under Review",
        style=discord.ButtonStyle.blurple,
        custom_id="ReviewSubButton",
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
        if dbdata["Notified"] is True:
            await user.send(embed=embed)
        await interaction.response.edit_message(embed=embed, view=self)

    @discord.ui.button(
        label="Implementing",
        style=discord.ButtonStyle.blurple,
        custom_id="ImplementingSugButton",
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
        if dbdata["Notified"] is True:
            await user.send(embed=embed)
        await interaction.response.edit_message(embed=embed, view=self)

    @discord.ui.button(label="Denied", style=discord.ButtonStyle.blurple, custom_id="DeniedSugButton")
    async def sugdenbutton(self, interaction, button):
        await interaction.response.send_modal(self.modal)


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
            self.add_item(self.notifybutton)
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
        self.add_item(self.notifybutton)
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
        try:
            await self.ctx.author.send(embed=embed)
        except:
            pass
        msgdb = await self.ctx.bot.dep.send(embed=embed, view=suggestionconfig())
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

    @discord.ui.button(emoji="🔔", label="Notify", style=discord.ButtonStyle.gray)
    async def notifybutton(self, interaction, button):
        if self.notified is True:
            self.notified = False
            await interaction.response.send_message(
                "You will now no longer be notified when your suggestion state is changed",
                ephemeral=True,
            )
        elif self.notified is False:
            self.notified = True
            await interaction.response.send_message(
                "You will now be notified when your suggestion state is changed",
                ephemeral=True,
            )

    async def interaction_check(self, interaction):
        if interaction.user.id == self.ctx.author.id:
            return True
        await interaction.response.send_message(
            "This is not your Interaction!",
            ephemeral=True,
        )
        return False


class Utility(commands.Cog):
    """All Utility related commands"""

    def __init__(self, bot):
        self.bot = bot
        self.persistent_view = suggestionconfig()

    async def cog_load(self):
        self.bot.add_view(self.persistent_view)

    async def cog_unload(self):
        self.persistent_view.stop()

    @commands.command(name="suggest", description="Give suggestions for Ely, the bot")
    @commands.bot_has_permissions(external_emojis=True, embed_links=True, attach_files=True)
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
        msg = await ctx.reply(embed=embed)
        view = suggestionview(ctx, msg, message)
        return await msg.edit(view=view)


async def setup(bot):
    await bot.add_cog(Utility(bot))
