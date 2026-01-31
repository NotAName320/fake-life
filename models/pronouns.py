from .document import InnerDocument, FLObjectId


class Pronouns(InnerDocument):
    they: str
    them: str
    their: str
    theirs: str
    themselves: str


HE_HIM = Pronouns(
    they="he",
    them="him",
    their="his",
    theirs="his",
    themselves="himself"
)


SHE_HER = Pronouns(
    they="she",
    them="her",
    their="her",
    theirs="hers",
    themselves="herself"
)


THEY_THEM = Pronouns(
    they="they",
    them="them",
    their="their",
    theirs="theirs",
    themselves="themselves"
)


def from_string(string: str) -> Pronouns:
    match string:
        case "He/Him":
            return HE_HIM
        case "She/Her":
            return SHE_HER
        case "They/Them":
            return THEY_THEM
        case _:
            raise ValueError("Invalid pronoun string")
