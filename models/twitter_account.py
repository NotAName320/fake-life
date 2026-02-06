from dataclasses import dataclass, field
from typing import Self, Optional

from .document import FakeLifeDocument


@dataclass
class TwitterAccount(FakeLifeDocument):
    handle: str
    display_name: str
    banned: bool = False
    profile_picture: Optional[str] = None

    @property
    def as_embed(self: Self):
        return super().as_embed
