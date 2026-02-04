from dataclasses import dataclass
from typing import TypedDict

from bson import ObjectId


class FLObjectId(ObjectId):
    def __init__(self, oid: str | int) -> None:
        if isinstance(oid, int):
            oid = str(oid)
        if len(oid) < 24:
            oid = "0" * (24 - len(oid)) + oid
        super().__init__(oid)

@dataclass
class FakeLifeDocument:
    _id: FLObjectId

    @classmethod
    def from_mongo_document(cls, document: dict):
        return cls(**document)

class InnerDocument(TypedDict):
    pass