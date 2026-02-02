import logging
import os

from discord.ext import commands


async def setup(bot: commands.Bot):
    for cog_file in os.listdir(os.path.dirname(__file__)):
        if not cog_file.endswith(".py") or cog_file == "__init__.py":
            continue
        await bot.load_extension(f'cogs.{cog_file[:-3]}')
