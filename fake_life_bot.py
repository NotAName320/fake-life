import asyncio
import os

from discord import Intents
from dotenv import load_dotenv
from pymongo import AsyncMongoClient

from mongo_extended_bot import MongoExtendedBot
from utils import getenv_or_exit


load_dotenv()
DISCORD_BOT_TOKEN = getenv_or_exit("DISCORD_BOT_TOKEN")
HOME_GUILD_ID = getenv_or_exit("HOME_GUILD_ID")
MONGODB_CONNECTION_STRING = getenv_or_exit("MONGODB_CONNECTION_STRING")


async def main():
    # Remove old log file
    try:
        os.remove("bot.log")
    except FileNotFoundError:
        pass

    intents = Intents.default()
    intents.message_content = True
    mongo_client = AsyncMongoClient(MONGODB_CONNECTION_STRING)

    bot = MongoExtendedBot(command_prefix='!', db_client=mongo_client, intents=intents)

    await bot.load_extension("cogs")

    @bot.event
    async def on_ready():
        bot.home_guild = bot.get_guild(int(HOME_GUILD_ID)) or exit(1)

    try:
        await bot.start(DISCORD_BOT_TOKEN)
    finally:
        await mongo_client.close()


if __name__ == '__main__':
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        raise SystemExit(0)
