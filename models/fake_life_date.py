from dataclasses import dataclass
from typing import Self


@dataclass
class FakeLifeDate:
    year: int
    month: int

    def __str__(self: Self):
        word_month = ["", "January", "Febuary", "March", "April",
                      "May", "June", "July", "August", "September",
                      "October", "November", "December"][self.month]
        return f"{word_month} {self.year}"
