from dataclasses import dataclass
from typing import Optional, Self

import discord

from . import FakeLifeDate
from .document import FakeLifeDocument, InnerDocument, FLObjectId
from .pronouns import Pronouns


class GeneticStats(InnerDocument):
    physicality: int
    diligence: int
    wit: int
    charisma: int
    luck: int


@dataclass
class User(FakeLifeDocument):
    first_name: str
    last_name: str

    age: int
    birth_month: int
    birth_year: int

    pronouns: Pronouns

    genetics: GeneticStats

    money: float
    gpa: float

    education: Optional[str]
    job: Optional[FLObjectId]

    relationship: Optional[FLObjectId]
    
    traits: list[FLObjectId]

    @property
    def birthday(self: Self) -> FakeLifeDate:
        return FakeLifeDate(
            year=self.birth_year,
            month=self.birth_month
        )

    def as_discord_embed(self: Self) -> discord.Embed:
        return discord.Embed(colour=0x0, title="Character Info")\
                      .add_field(name="Name", value=f"{self.first_name} {self.last_name}")\
                      .add_field(name="Age", value=self.age)\
                      .add_field(name="Pronouns", value=f"{self.pronouns['they']}/{self.pronouns['them']}")\
                      .add_field(name="Birthday", value=str(self.birthday))\
                      .add_field(name="Net Worth", value=f'${self.money:.2f}')\
                      .add_field(name="Relationship Status", value=f"With {self.relationship}"
                                 if self.relationship else "Single")\
                      .add_field(name="Education", value=f'{self.education}')\
                      .add_field(name="Job", value=f"{self.job}")\
                      .add_field(name="Traits", value=self.traits if self.traits else "None")\
                      .add_field(name="Genetic Attributes",
                                 value=f'```Physicality: {self.genetics["physicality"]}\n'
                                       f'Diligence: {self.genetics["diligence"]}\n'
                                       f'Wit: {self.genetics["wit"]}\n'
                                       f'Charisma: {self.genetics["charisma"]}\n'
                                       f'Luck: {self.genetics["luck"]}```',
                                 inline=False)
