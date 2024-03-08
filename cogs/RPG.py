import discord
from discord.ext import commands
from utils.Embed import AiEmbed
from typing import Optional
import random


def get_exp_to_level(level):
    exp_to_level = [0] * 250
    for i in range(1, 100):
        exp_to_level[i] = exp_to_level[i - 1] + 1000 * i
    exp_to_level[99] = 10000000
    return exp_to_level[level - 1]


class BetaTestHandler(commands.CheckFailure):
    pass


def betatesters(ctx: commands.Context):
    if ctx.author.id in ctx.bot.testers:
        return True
    raise BetaTestHandler()


class RPG(commands.Cog):
    """All RPG related commands"""

    def __init__(self, bot: commands.Bot):
        self.bot: commands.Bot = bot

    @commands.group(name="RPG", description="Base RPG command", invoke_without_command=False)
    @commands.check(betatesters)
    @commands.bot_has_permissions(external_emojis=True, embed_links=True, attach_files=True)
    async def rpg(self, ctx: commands.Context):
        pass

    @rpg.command(name="start", description="start RPG command")
    @commands.bot_has_permissions(external_emojis=True, embed_links=True, attach_files=True)
    async def rpgstart(self, ctx: commands.Context):
        if await self.bot.db.rpg.find_one({"_id": ctx.author.id}):
            return await ctx.reply("You already have a profile")
        message: discord.Message = await ctx.reply("Creating your RPG profile...")
        await self.bot.db.rpg.insert_one(
            {
                "_id": ctx.author.id,
                "level": 1,
                "experience": 0,
                "health": 100,
                "max_health": 100,
                "mana": 0,
                "max_mana": 0,
                "strength": 10,
                "luck": 1,
                "memory_fragments": [],
                "memory_unlocked": [],
                "skills": [],
                "inventory": [],
                "money": 1000,
                "quests": [],
                "location": "Starting Area",
                "version": "0.0.1",
            }
        )
        return await message.edit(
            content=f"I've created your RPG profile now! Run `{ctx.clean_prefix}rpg profile` to view your profile!"
        )

    @rpg.command(name="profile", description="Look at your RPG profile")
    @commands.bot_has_permissions(external_emojis=True, embed_links=True, attach_files=True)
    async def rpgprofile(self, ctx: commands.Context, user: Optional[discord.Member] = None):
        user = user or ctx.author
        data = await self.bot.db.rpg.find_one({"_id": user.id})
        if not data:
            return await ctx.reply("The user doesn't have a RPG profile")
        expbar = [str("<:progress_empty2:1211650758525722654>") for a in range(10)]
        for i in range(int((data["health"] / data["max_health"]) * 10)):
            expbar[i] = "<a:Untitled_Project_V11:1211352778925023244>"
        expbar[0] = (
            "<a:Untitled_Project_V3:1211353406480842853>"
            if expbar[0] != "<a:Untitled_Project_V11:1211352778925023244>"
            else "<:progress_empty_left:1211656588604211290>"
        )
        expbar[9] = (
            "<a:Untitled_Project_V2:1211353422591168562>"
            if expbar[9] != "<a:Untitled_Project_V3:1211353406480842853>"
            else "<:progress_empty3:1211650745577902110>"
        )
        expbar1 = [str("<:Emoji:1199098030289322026>") for a in range(10)]
        if data["mana"] and data["max_mana"]:
            for i in range(int((data["mana"] / data["max_mana"]) * 10)):
                expbar[i] = "<:Emoji:1199098002795659315>"
        listing = [
            f"- **Level -** {data['level']}",
            f"  - `{data['experience']}/{get_exp_to_level(data['level'] + 1)}`",
            f"- **Health -** `{data['health']}/{data['max_health']}`",
            f"  - {''.join(expbar)}",
            f"- **Mana -** `{data['mana']}/{data['max_mana']}`",
            f"  - {''.join(expbar1)}",
            f"- **Strength -** {data['strength']}",
            f"- **Luck -** {data['luck']}",
            f"- **Money -** {data['money']}",
        ]
        embed = AiEmbed.default(ctx, title=str(user), description="\n".join(listing))
        return await ctx.reply(embed=embed)

    @rpg.command(name="adventure", description="Fight someone lmao")
    @commands.bot_has_permissions(external_emojis=True, embed_links=True, attach_files=True)
    async def rppgadventure(self, ctx: commands.Context):
        await self.bot.db.rpg.find_one_and_update({"_id": ctx.author.id}, {"$inc": {"health": -10, "experience": +10}})
        return await ctx.reply(
            f'{random.choice(["Legi", "Down Bad", "Hiroshi", "Stanko", "Stanich", "Zimin", "Vegeta"])} died. You got exp and lost health'
        )


async def setup(bot: commands.Bot):
    await bot.add_cog(RPG(bot))
