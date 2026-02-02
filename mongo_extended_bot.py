from typing import Type, Self

from discord import app_commands, Guild
from discord.ext import commands
from pymongo import AsyncMongoClient
from pymongo.asynchronous.collection import AsyncCollection

from constants import MONGODB_DATABASE_NAME
import models
from models import FakeLifeDocument, FakeLifeDate


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
    
    @property
    def database(self: Self):
        return self.db_client[MONGODB_DATABASE_NAME]

    async def get_document[T: FakeLifeDocument](self: Self, document_type: Type[T], query: dict) -> T | None:
        collection: AsyncCollection[T] = self.database[document_type.__name__]
        return await collection.find_one(query)
    
    async def insert_document[T: FakeLifeDocument](self: Self, document_type: Type[T], document_to_insert: T):
        collection: AsyncCollection[FakeLifeDocument] = self.database[document_type.__name__]
        await collection.insert_one(document_to_insert)
    
    async def delete_document[T: FakeLifeDocument](self: Self, document_type: Type[T], query: dict):
        collection: AsyncCollection[FakeLifeDocument] = self.database[document_type.__name__]
        await collection.delete_one(query)
    
    async def get_current_date(self: Self) -> FakeLifeDate:
        collection = self.database["Metadata"]

        metadata_document = await collection.find_one()
        assert metadata_document is not None

        months_since_2010 = metadata_document["date"]
        return FakeLifeDate(
            year=months_since_2010 // 12 + 2010,
            month=months_since_2010 % 12 + 1
        )
    
    async def calculate_birthday(self: Self, user: models.User) -> FakeLifeDate:
        current_date = await self.get_current_date()
        age, birth_month = user["age"], user["birthday"]

        birth_year = current_date.year - age
        # birth month is yet to come in the year
        # e.g. if someone is born June 2025, in January 2026 they will
        # be 0, so a simple current year - age will only give 0,
        # necessitating subtracting one more year
        if current_date.month > birth_month:
            birth_year -= 1
        return FakeLifeDate(
            year=birth_year,
            month=birth_month
        )
