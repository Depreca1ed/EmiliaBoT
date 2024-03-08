import discord
from typing import List


class ElyPagination(discord.ui.View):
    def __init__(self, embeds: List[discord.Embed], ctx):
        super().__init__(timeout=500)
        self.embeds = embeds
        self.ctx = ctx
        self.index = 0
        for i, embed in enumerate(self.embeds):
            embed.set_footer(text=f"Requested by {str(self.ctx.author)}" + " | " + f"Page {i+1} of {len(self.embeds)}")
            self._update_state()

    def _update_state(self) -> None:
        self.first_page.disabled = self.prev_page.disabled = self.index == 0
        self.last_page.disabled = self.next_page.disabled = self.index == len(self.embeds) - 1

    async def start(self):
        embed = self.embeds[0]
        if len(self.embeds) == 1:
            self.message = await self.ctx.reply(embed=embed)
            return
        self.message = await self.ctx.reply(embed=embed, view=self)

    @discord.ui.button(emoji="<:pagiprevprev:1204333873740124170>", style=discord.ButtonStyle.grey)
    async def first_page(self, inter, button):
        self.index = 0
        self._update_state()
        await inter.response.edit_message(embed=self.embeds[self.index], view=self)

    @discord.ui.button(emoji="<:pagiprev:1204334051918614598>", style=discord.ButtonStyle.secondary)
    async def prev_page(self, inter, button):
        self.index -= 1
        self._update_state()
        await inter.response.edit_message(embed=self.embeds[self.index], view=self)

    @discord.ui.button(emoji="<:pagistop:1204334166800470057>", style=discord.ButtonStyle.grey)
    async def remove(self, inter, button):
        await inter.response.edit_message(view=None)
        self.stop()

    @discord.ui.button(emoji="<:paginext:1204333968460226621>", style=discord.ButtonStyle.secondary)
    async def next_page(self, inter, button):
        self.index += 1
        self._update_state()
        await inter.response.edit_message(embed=self.embeds[self.index], view=self)

    @discord.ui.button(emoji="<:paginextnext:1204333711638921236>", style=discord.ButtonStyle.grey)
    async def last_page(self, inter, button):
        self.index = len(self.embeds) - 1
        self._update_state()
        await inter.response.edit_message(embed=self.embeds[self.index], view=self)

    async def interaction_check(self, interaction):
        if interaction.user.id == self.ctx.author.id:
            return True
        await interaction.response.send_message(
            "This is not your Interaction!",
            ephemeral=True,
        )
        return False

    async def on_timeout(self):
        await self.message.edit(view=None)
        self.stop()
