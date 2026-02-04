import logging
from typing import Type, Self, Optional

from discord import app_commands, Guild
from discord.ext import commands
from pymongo import AsyncMongoClient
from pymongo.asynchronous.collection import AsyncCollection

from constants import MONGODB_DATABASE_NAME
from models import FakeLifeDocument, FakeLifeDate, FLObjectId


logger = logging.getLogger('fake_life_bot')


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

    async def get_document[T: FakeLifeDocument](self: Self, document_type: Type[T], query: dict) -> Optional[T]:
        collection: AsyncCollection = self.database[document_type.__name__]
        found_document = await collection.find_one(query)
        if not found_document:
            return None
        
        return document_type.from_mongo_document(found_document)
    
    async def get_document_by_id[T: FakeLifeDocument](self: Self, document_type: Type[T], _id: FLObjectId) -> Optional[T]:
        return await self.get_document(document_type, {'_id': _id})
    
    async def insert_document[T: FakeLifeDocument](self: Self, document_to_insert: T):
        collection: AsyncCollection = self.database[type(document_to_insert).__name__]
        logger.info(f"Inserting {document_to_insert._id} into database {type(document_to_insert).__name__}")
        await collection.insert_one(vars(document_to_insert))
    
    async def delete_document[T: FakeLifeDocument](self: Self, document_type: Type[T], query: dict):
        collection: AsyncCollection = self.database[document_type.__name__]
        logger.info(f"Deleting any documents in {document_type.__name__} that meet query {query}")
        await collection.delete_one(query)
    
    async def delete_document_by_id[T: FakeLifeDocument](self: Self, document_type: Type[T], _id: FLObjectId):
        return await self.delete_document(document_type, {'_id': _id})
    
    async def get_current_date(self: Self) -> FakeLifeDate:
        collection = self.database["Metadata"]

        metadata_document = await collection.find_one()
        assert metadata_document is not None

        months_since_2010 = metadata_document["date"]
        return FakeLifeDate(
            year=months_since_2010 // 12 + 2010,
            month=months_since_2010 % 12 + 1
        )
