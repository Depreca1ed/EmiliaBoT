import discord, random
from discord.ext import commands
from utils.dataset import *
from utils.Embed import AiEmbed
from typing import Optional


class Fun(commands.Cog):
    """All Fun commands"""

    def __init__(self, bot: commands.Bot):
        self.bot: commands.Bot = bot

    @commands.command(name="fact", description="Get to know a cool fact")
    @commands.bot_has_permissions(external_emojis=True, embed_links=True, attach_files=True)
    async def fact(self, ctx: commands.Context):
        fact = random.choice(facts)
        await ctx.reply(embed=AiEmbed.default(ctx, title="Cool fact!", description=fact))

    @commands.command(name="roast", description="Roast someone (no grudges)")
    @commands.bot_has_permissions(external_emojis=True, embed_links=True, attach_files=True)
    async def roast(self, ctx: commands.Context, user: Optional[discord.Member] = None):
        if user and user.id in ctx.bot.owner_ids:
            return await ctx.reply("Nope :D")
        roast = random.choice(roasts)
        embed = (
            AiEmbed.default(ctx, title=f"YO {str(user)}", description=roast)
            if user
            else AiEmbed.default(
                ctx, title=f"You really wanna roast yourself {str(ctx.author)}? Okay then...", description=roast
            )
        )
        await ctx.reply(embed=embed)

    @commands.command(name="yomama", description="Yomama so helpful she made this help command possible")
    @commands.bot_has_permissions(external_emojis=True, embed_links=True, attach_files=True)
    async def yomamacmd(self, ctx: commands.Context, user: discord.Member):
        if user.id in ctx.bot.owner_ids:
            return await ctx.reply("Nope :D")
        yomamaobj = random.choice(yomama)
        embed = AiEmbed.default(ctx, title=f"Ayo, {str(user)}", description=yomamaobj)
        await ctx.reply(embed=embed)


async def setup(bot: commands.Bot):
    await bot.add_cog(Fun(bot))
