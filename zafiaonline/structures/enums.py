from enum import IntEnum, Enum


class Sex(IntEnum):
    WOMEN = 0
    MEN = 1


class Languages(str, Enum):
    UNSELECTED = ""
    RUSSIAN = "ru"
    ENGLISH = "en"


class Roles(IntEnum):
    NO_ROLE = -1
    UNKNOWN = 0
    CIVILIAN = 1
    DOCTOR = 2
    SHERIFF = 3
    MAFIA = 4
    LOVER = 5
    TERRORIST = 6
    JOURNALIST = 7
    BODYGUARD = 8
    BARMAN = 9
    SPY = 10
    INFORMER = 11

class RatingMode(str, Enum):
    ALL_TIME = "all_time"
    TODAY = "today"
    YESTERDAY = "yesterday"


class RatingType(str, Enum):
    GAMES = "games"
    EXPERIENCE = "experience"
    AUTHORITY = "authority"
    WINS = "wins"
