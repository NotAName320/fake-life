import logging
import os

from discord.ext import commands


logger = logging.getLogger("fake_life_bot")
logger.setLevel(logging.INFO)
formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')

file_handler = logging.FileHandler("bot.log")
file_handler.setFormatter(formatter)
logger.addHandler(file_handler)

console_handler = logging.StreamHandler()
console_handler.setFormatter(formatter)
console_handler.setLevel(logging.WARN)
logger.addHandler(console_handler)


async def setup(bot: commands.Bot):
    for cog_file in os.listdir(os.path.dirname(__file__)):
        if not cog_file.endswith(".py") or cog_file == "__init__.py":
            continue
        await bot.load_extension(f'cogs.{cog_file[:-3]}')
