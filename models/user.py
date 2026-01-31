from typing import Optional

from .document import FakeLifeDocument, InnerDocument, FLObjectId
from .pronouns import Pronouns


class GeneticStats(InnerDocument):
    physicality: int
    diligence: int
    wit: int
    charisma: int
    luck: int


class User(FakeLifeDocument):
    first_name: str
    last_name: str

    age: int
    birthday: int

    pronouns: Pronouns

    genetics: GeneticStats

    money: float
    gpa: float

    education: Optional[str]
    job: Optional[FLObjectId]
    
    traits: list[FLObjectId]
