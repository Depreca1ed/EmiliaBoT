import os, discord, aiohttp, mystbin, random, jishaku, topgg, datetime, configparser, json

from discord.ext import commands, tasks
from typing import List, Optional
from characterai import PyAsyncCAI
from itertools import product
from motor.motor_asyncio import AsyncIOMotorClient
import asqlite


def get_prefix(bot, message):
    prefix = "e!"
    if message.author.id in bot.owner_ids and bot.tempvars["Prefixless"] is True:
        return ""
    elif bot.user.id in [u.id for u in message.mentions]:
        prefixes = ["".join(capitalization) for capitalization in product(*zip(prefix.lower(), prefix.upper()))]
        prefixes.append("")
        return prefixes
    prefixes = ["".join(capitalization) for capitalization in product(*zip(prefix.lower(), prefix.upper()))]
    return prefixes


class Ely(commands.Bot):
    def __init__(self):
        intents = discord.Intents.all()
        intents.presences = False
        super().__init__(
            command_prefix=get_prefix,
            description=f"Hello!!!! I am **Emilia**. A purpose-less non-unique discord bot created with the help of a soul of a mistake found by `deprecating`.",
            case_insensitive=True,
            strip_after_prefix=True,
            intents=intents,
            owner_ids=[688293803613880334],
        )
        self.mystbin: mystbin.Client = mystbin.Client()
        self.load_time = datetime.datetime.now(datetime.UTC)
        self.artist = json.loads(open("config/users.json", "r").read())["artists"]
        self.testers = json.loads(open("config/users.json", "r").read())["testers"]
        self.blacklistedusers = json.loads(open("config/users.json", "r").read())["blacklisted"]
        self.tempvars = {"Roleplay": True, "Prefixless": True}
        self.charAI = PyAsyncCAI(str(self.config.get("TOKENS", "character_AI")))
        self.token = str(self.config.get("TOKENS", "bot"))

    @property
    def dep(self) -> Optional[discord.User]:
        """Returns discord.User of the owner"""
        return self.get_user(688293803613880334)

    @property
    def owners(self) -> List[discord.User]:
        """Returns list of owners"""
        return [self.get_user(owner) for owner in self.owner_ids]

    @property
    def artists(self) -> List[discord.User]:
        """Returns list of artists"""
        return [self.get_user(artist) for artist in self.artist]

    @classmethod
    async def blacklistcheck(self, ctx: commands.Context) -> bool:
        if ctx.author.id not in ctx.bot.blacklistedusers:
            return True
        return False

    @property
    def config(self) -> configparser.ConfigParser:
        config = configparser.ConfigParser()
        config.read("config/config.ini")
        return config

    @property
    async def usage(self) -> int:
        async with self.pool.bot.acquire() as conn:
            val = await conn.fetchone(
                """SELECT amount FROM BotInfo WHERE command_usage = 'all'""",
            )

        self.usagecount = val[0] if val else 0
        return self.usagecount

    async def setup_hook(self):
        print("SETUP Started")
        await self.setup_database()
        self.session = aiohttp.ClientSession()
        await self.setup_cogs()
        await self.setup_topgg()
        self.add_check(self.blacklistcheck)
        self.activitystatus.start()
        print("SETUP Completed")

    async def setup_database(self) -> None:
        print("DATABASE Loading")
        self.dbcli = AsyncIOMotorClient(str(self.config.get("TOKENS", "mongodb")))
        self.db = self.dbcli["Ely"]
        self.db.suggestions = self.db["Suggestions"]
        self.db.rpg = self.db["RPG"]
        self.pool = type("pool", (object,), {})
        self.pool.bot = await asqlite.create_pool("database/botinfo.db")
        self.pool.fun = await asqlite.create_pool("database/fundata.db")
        # Now its time to set the vars
        async with self.pool.bot.acquire() as db:
            async with db.execute("SELECT * FROM blacklisted_users") as cursor:
                blacklisted_users = await cursor.fetchall()
            async with db.execute("SELECT * FROM blacklisted_guilds") as cursor:
                blacklisted_guilds = await cursor.fetchall()
        self.blacklistedusers = [blacklist[0] for blacklist in blacklisted_users]
        self.blacklistedguilds = [blacklist[0] for blacklist in blacklisted_guilds]
        print("DATABASE Loaded")
        return

    async def setup_jishaku(self) -> None:
        jishaku.Flags.HIDE = True
        jishaku.Flags.RETAIN = True
        await self.load_extension("jishaku")
        jishaku.Flags.NO_UNDERSCORE = True
        jishaku.Flags.FORCE_PAGINATOR = True
        jishaku.Flags.NO_DM_TRACEBACK = True
        jishaku.Flags.USE_ANSI_ALWAYS = True
        print("EXT Jishaku loaded")

    async def setup_topgg(self) -> None:
        self.topggcli = topgg.DBLClient(self, str(self.config.get("TOKENS", "topgg")), autopost=True, post_shard_count=True)
        self.topggwebhook = topgg.WebhookManager(self).dbl_webhook("/webhook", auth_key="pass")
        await self.topggwebhook.run(20708)
        print("WEBHOOK Topgg loaded")
        return

    async def setup_cogs(self) -> None:
        print("EXT Loading")
        for cog in os.listdir("./cogs"):
            if cog.endswith(".py"):
                await self.load_extension(f"cogs.{cog[:-3]}")
                print(f"EXT {cog} Loaded")
        await self.setup_jishaku()

    @tasks.loop(minutes=1)
    async def activitystatus(self):
        activities = [
            "I must do something to thank you...",
            "It's more satisfying to hear a single \U00000022thank you\U00000022 than a lot of \U00000022sorrys.\U00000022",
            "My name is Emilia. Just Emilia.",
            "It's been rough, hasn't it?",
            "I can't imagine this will make things any easier, but this is all I can do.",
        ]
        await self.change_presence(activity=discord.CustomActivity(name=random.choice(activities)))

    @activitystatus.before_loop
    async def beforethatloopy(self):
        await self.wait_until_ready()

    async def close(self):
        await self.pool.bot.close()
        await super().close()


Ely().run(Ely().token)
