from typing import Self

from discord.ext import commands

from constants import BOT_OPERATOR_ROLE_NAME, CHARACTER_APPROVALS_CHANNEL_ID, MEMBER_ROLE_NAME
from views.character_application import StartApplicationButton


class CharacterApplicationGenerator(commands.Cog):
    bot: commands.Bot

    def __init__(self: Self, bot: commands.Bot) -> None:
        self.bot = bot
    
    @commands.Cog.listener(name="on_ready")
    async def register_views(self: Self):
        self.bot.add_view(StartApplicationButton())

    @commands.command(name='cca')
    @commands.has_role(BOT_OPERATOR_ROLE_NAME)
    async def create_character_application(self: Self, ctx: commands.Context):
        await ctx.message.delete()
        return await ctx.channel.send("Click this to start your application!", view=StartApplicationButton())


async def setup(bot: commands.Bot):
    await bot.add_cog(CharacterApplicationGenerator(bot))
