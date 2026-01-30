from .document import FakeLifeDocument
from .pronouns import Pronouns


class GeneticStats(FakeLifeDocument):
    physicality: int
    diligence: int
    wit: int
    charisma: int
    luck: int


class FakeLifeUser(FakeLifeDocument):
    first_name: str
    last_name: str

    age: int
    birthday: int

    pronouns: Pronouns

    genetics: GeneticStats

    money: float
    gpa: float
