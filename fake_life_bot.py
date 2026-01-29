import asyncio
import logging
import os
# delete old logs before importing other files that make use of log files
os.remove("bot.log")
from os import listdir, getenv
from sys import stderr

from discord import Intents
from dotenv import load_dotenv
from pymongo import AsyncMongoClient

from mongo_extended_bot import MongoExtendedBot


logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')

file_handler = logging.FileHandler("bot.log")
file_handler.setFormatter(formatter)
logger.addHandler(file_handler)

console_handler = logging.StreamHandler()
console_handler.setFormatter(formatter)
console_handler.setLevel(logging.WARN)
logger.addHandler(console_handler)


load_dotenv()
DISCORD_BOT_TOKEN = getenv("DISCORD_BOT_TOKEN")
MONGODB_CONNECTION_STRING = getenv("MONGODB_CONNECTION_STRING")


async def main():
    if not DISCORD_BOT_TOKEN:
        print("No DISCORD_BOT_TOKEN defined in .env", file=stderr)
        exit(1)
    if not MONGODB_CONNECTION_STRING:
        print("No MONGODB_CONNECTION_STRING defined in .env", file=stderr)
        exit(1)

    intents = Intents.default()
    intents.message_content = True
    mongo_client = AsyncMongoClient(MONGODB_CONNECTION_STRING)

    bot = MongoExtendedBot(command_prefix='!', db_client=mongo_client, intents=intents)

    for cog_file in listdir("cogs"):
        if not cog_file.endswith(".py") or cog_file == "__init__.py":
            continue
        await bot.load_extension(f'cogs.{cog_file[:-3]}')

    try:
        await bot.start(DISCORD_BOT_TOKEN)
    finally:
        await mongo_client.close()


if __name__ == '__main__':
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        raise SystemExit(0)
