from enum import IntEnum, StrEnum


class Sex(IntEnum):
    WOMEN = 0
    MEN = 1


class Languages(StrEnum):
    RUSSIAN = "ru"
    ENGLISH = "en"


class Roles(IntEnum):
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
