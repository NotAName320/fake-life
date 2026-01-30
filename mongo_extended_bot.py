from typing import Type, Self

from discord import app_commands, Guild
from discord.ext import commands
from dotenv import load_dotenv
from pymongo import AsyncMongoClient
from pymongo.asynchronous.collection import AsyncCollection

from models import FakeLifeDocument
from utils import getenv_or_exit


load_dotenv()
MONGODB_DATABASE_NAME = getenv_or_exit("MONGODB_DATABASE_NAME")


class MongoExtendedBot(commands.Bot):
    db_client: AsyncMongoClient
    home_guild: Guild

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

    async def get_document[T: FakeLifeDocument](self: Self, document_type: Type[T], query: dict) -> T | None:
        database = self.db_client[MONGODB_DATABASE_NAME]
        collection: AsyncCollection[T] = database[document_type.__name__]
        return await collection.find_one(query)
    
    async def insert_document(self: Self, document_to_insert: FakeLifeDocument):
        database = self.db_client[MONGODB_DATABASE_NAME]
        collection: AsyncCollection[FakeLifeDocument] = database[type(document_to_insert).__name__]
        await collection.insert_one(document_to_insert)
