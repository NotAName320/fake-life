import asyncio

from discord import Intents
from pymongo import AsyncMongoClient

from constants import DISCORD_BOT_TOKEN, HOME_GUILD_ID, MONGODB_CONNECTION_STRING
from logger import logging_setup
from mongo_extended_bot import MongoExtendedBot


async def main():
    logging_setup()

    intents = Intents.default()
    intents.message_content = True
    intents.members = True
    mongo_client = AsyncMongoClient(MONGODB_CONNECTION_STRING)

    bot = MongoExtendedBot(command_prefix='!', db_client=mongo_client, intents=intents)

    await bot.load_extension("cogs")

    @bot.event
    async def on_ready():
        bot.home_guild = bot.get_guild(HOME_GUILD_ID)

    try:
        await bot.start(DISCORD_BOT_TOKEN)
    finally:
        await mongo_client.close()


if __name__ == '__main__':
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        raise SystemExit(0)
