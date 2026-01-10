import enum


class ActivityTypes(str, enum.Enum):
    SLEEP = "SLEEP"
    WORK = "WORK"
    STUDY = "STUDY"
    FAMILY = "FAMILY"
    FRIENDS = "FRIENDS"
    RELAX = "RELAX"
    SPORT = "SPORT"
    GAMES = "GAMES"
