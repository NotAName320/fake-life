from dataclasses import dataclass
from datetime import datetime
from typing import Optional, Self
import discord

from . import pronouns
from .document import FakeLifeDocument, FLObjectId
from .fake_life_date import FakeLifeDate
from .user import GeneticStats, User


@dataclass
class CharacterApplication(FakeLifeDocument):
    user: discord.User
    first_name: str
    last_name: str
    pronouns: str
    genetics: Optional[GeneticStats] = None

    @property
    def as_embed(self: Self) -> discord.Embed:
        retval = discord.Embed(colour=0x0, title="New Application", timestamp=datetime.now())
        retval.add_field(name="Applicant", value=self.user.mention)
        retval.add_field(name="First Name", value=self.first_name)
        retval.add_field(name="Last Name", value=self.last_name)
        retval.add_field(name="Pronouns", value=self.pronouns)
        retval.add_field(name="Physicality", value=self.genetics["physicality"])
        retval.add_field(name="Diligence", value=self.genetics["diligence"])
        retval.add_field(name="Wit", value=self.genetics["wit"])
        retval.add_field(name="Charisma", value=self.genetics["charisma"])
        retval.add_field(name="Luck", value=self.genetics["luck"])

        return retval
    
    def as_user_document(self: Self, current_date: FakeLifeDate) -> User:
        return User(
            _id=FLObjectId(str(self.user.id)),
            first_name=self.first_name,
            last_name=self.last_name,
            pronouns=pronouns.from_string(self.pronouns),
            genetics=self.genetics,

            # defaults
            age=18,
            birth_month=current_date.month,
            birth_year=current_date.year - 18,
            money=20.0,
            gpa=3.0,
            education=None,
            job=None,
            traits=[],
            relationship=None
        )
