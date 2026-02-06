from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Self, TypedDict

from bson import ObjectId
from discord import Embed


class FLObjectId(ObjectId):
    def __init__(self, oid: str | int) -> None:
        if isinstance(oid, int):
            oid = str(oid)
        if len(oid) < 24:
            oid = "0" * (24 - len(oid)) + oid
        super().__init__(oid)

@dataclass
class FakeLifeDocument(ABC):
    _id: FLObjectId

    @classmethod
    def from_mongo_document(cls, document: dict):
        return cls(**document)
    
    @property
    @abstractmethod
    def as_embed(self: Self) -> Embed:
        return Embed(colour=0x0,
                     title="No Embed",
                     description="This object has no designated embed!")

class InnerDocument(TypedDict):
    pass