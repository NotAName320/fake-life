import asyncio
import os
from os import getenv
from sys import stderr

from discord import Intents
from dotenv import load_dotenv
from pymongo import AsyncMongoClient

from mongo_extended_bot import MongoExtendedBot


load_dotenv()
DISCORD_BOT_TOKEN = getenv("DISCORD_BOT_TOKEN")
HOME_GUILD_ID = getenv("HOME_GUILD_ID")
MONGODB_CONNECTION_STRING = getenv("MONGODB_CONNECTION_STRING")


async def main():
    # Remove old log file
    os.remove("bot.log")

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

    await bot.load_extension("cogs")

    @bot.event
    async def on_ready():
        bot.home_guild = bot.get_guild(int(HOME_GUILD_ID or 0)) or exit(1)

    try:
        await bot.start(DISCORD_BOT_TOKEN)
    finally:
        await mongo_client.close()


if __name__ == '__main__':
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        raise SystemExit(0)
