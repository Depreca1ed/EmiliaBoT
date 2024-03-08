from typing import (
    Any,
    AsyncGenerator,
    Awaitable,
    Callable,
    Dict,
    Iterable,
    Iterator,
    List,
    Optional,
    Sequence,
    Tuple,
    Type,
    TypeVar,
    Union,
)
import discord
import datetime
from discord.ext import commands


class AiEmbed(discord.Embed):
    """Main purpose is to get the usual setup of Embed for a command or an error embed"""

    def __init__(
        self,
        color: Union[discord.Color, int] = 0xFFFFFF,
        timestamp: Optional[datetime.datetime] = None,
        fields: Iterable[Tuple[str, str]] = (),
        field_inline: bool = False,
        **kwargs: Any,
    ):
        super().__init__(color=color, timestamp=timestamp or discord.utils.utcnow(), **kwargs)
        for n, v in fields:
            self.add_field(name=n, value=v, inline=field_inline)

    @classmethod
    def default(
        cls,
        ctx: commands.Context,
        colour: Optional[Union[discord.Colour, int]] = None,
        color: Optional[Union[discord.Colour, int]] = None,
        **kwargs: Any,
    ):
        instance = cls(**kwargs)
        instance.set_footer(
            text=f"Requested by {ctx.author if isinstance(ctx, commands.Context) else ctx.user}",
            icon_url=ctx.guild.icon.url if ctx.guild and ctx.guild.icon else None,
        )
        instance.set_author(
            name=f"{ctx.command.qualified_name.title()}",
            icon_url=(ctx.author.display_avatar.url if isinstance(ctx, commands.Context) else ctx.user.display_avatar.url),
        )
        if (colour is not None) or (color is not None):
            instance.colour = colour
        elif (ctx.author if isinstance(ctx, commands.Context) else ctx.user).id in (
            ctx.bot.owner_ids if isinstance(ctx, commands.Context) else ctx.client.owner_ids
        ):
            instance.colour = 0x210633
        elif (ctx.author if isinstance(ctx, commands.Context) else ctx.user).id in (
            ctx.bot.artist if isinstance(ctx, commands.Context) else ctx.client.artist
        ):
            instance.colour = 0x18312B
        else:
            instance.colour = instance.colour
        return instance
