from abc import ABC, abstractmethod
import logging
from typing import Type, Self
from os import getenv

from discord import app_commands
from discord.ext import commands
from dotenv import load_dotenv
from pymongo import AsyncMongoClient
from pymongo.asynchronous.database import AsyncDatabase


logger = logging.getLogger("Mongo")
logger.setLevel(logging.WARN)
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')

file_handler = logging.FileHandler("bot.log")
file_handler.setFormatter(formatter)
logger.addHandler(file_handler)

console_handler = logging.StreamHandler()
console_handler.setFormatter(formatter)
console_handler.setLevel(logging.WARN)
logger.addHandler(console_handler)


load_dotenv()
MONGODB_DATABASE_NAME = getenv("MONGODB_DATABASE_NAME")


class FakeLifeDocument(ABC):
    @classmethod
    @abstractmethod
    def retrieve(cls, db: AsyncDatabase) -> Self:
        pass


class MongoExtendedBot(commands.Bot):
    db_client: AsyncMongoClient

    def __init__(self,
                 command_prefix,
                 *,
                 help_command = commands.DefaultHelpCommand(),
                 tree_cls = app_commands.CommandTree,
                 description = None,
                 allowed_contexts = app_commands.AppCommandContext(),
                 allowed_installs = app_commands.AppInstallationType(),
                 intents,
                 db_client,
                 **options):
        self.db_client = db_client
        super().__init__(command_prefix,
                         help_command=help_command,
                         tree_cls=tree_cls,
                         description=description,
                         allowed_contexts=allowed_contexts,
                         allowed_installs=allowed_installs,
                         intents=intents,
                         **options)

    def get_document[T: FakeLifeDocument](self: Self, document_type: Type[T]) -> T:
        database = self.db_client.get_database(MONGODB_DATABASE_NAME)
        try:
            return document_type.retrieve(database)
        except Exception as e:
            logger.error("Encountered error whle performing database lookup", exc_info=True)
            raise e