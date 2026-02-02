import logging
import traceback
from typing import Self

from discord import Embed
from discord.ext import commands
from discord.ext.commands import Context


logger = logging.getLogger("fake_life_bot")


class Admin(commands.Cog):
    bot: commands.Bot

    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot

    @commands.Cog.listener("on_ready")
    async def print_when_ready(self: Self):
        logger.info(f"Successfully logged in as {self.bot.user}")
        # Redundant, but also the only info-level event we also want in terminal, so it's ok
        print(f"Successfully logged in as {self.bot.user}")

    @commands.Cog.listener()
    async def on_command_error(self: Self, ctx: Context, error: commands.CommandError):
        """Basic error handling, including generic messages to send for common errors"""
        unwrapped_error: Exception = getattr(error, 'original', error)

        if isinstance(error, commands.CommandNotFound):
            return await ctx.reply(f"Your command was not recognized. Please refer to {self.bot.command_prefix}help for more info.")
        if isinstance(error, commands.MissingRequiredArgument):
            return await ctx.reply("Error: you did not provide the required argument(s). Make sure you typed the command correctly.")
        if isinstance(error, commands.CheckFailure):
            return await ctx.reply("Error: You do not have permission to use this command.")

        else:
            formatted_error = "".join(traceback.format_exception(type(unwrapped_error), unwrapped_error, tb=unwrapped_error.__traceback__))

            # put error in log
            logger.error(formatted_error)

            # put error in chat
            errordesc = f'```py\n{formatted_error}\n```'
            embed = Embed(title='Error', description=errordesc, color=0)
            app_info = await self.bot.application_info()
            embed.set_footer(text=f'Please contact {app_info.owner} for help.')
            await ctx.send(embed=embed)

    @commands.command()
    async def ping(self: Self, ctx: Context):
        return await ctx.reply("Pong!")


async def setup(bot: commands.Bot):
    await bot.add_cog(Admin(bot))
