from msgspec import Struct
from .packet_data_keys import Renaming
from .enums import Sex, Languages, Roles
from typing import List


class ModelUser(Struct, rename=Renaming.USER):
    user_id: str = None
    username: str = None
    updated: int = None
    photo: str = None
    experience: int = None
    next_level_experience: int = None
    previous_level_experience: int = None
    level: int = None
    authority: int = None
    gold: int = None
    money: int = None
    is_vip: int = None
    vip_updated: int = None
    played_games: int = None
    score: int = None
    sex: Sex = Sex.MEN
    wins_as_killer: int = None
    wins_as_mafia: int = None
    wins_as_peaceful: int = None
    token: str = None
    accept_messages: int = None
    rank: int = None
    selected_language: Languages = Languages.RUSSIAN
    online: int = None
    player_role_statistics: dict = None
    match_making_score: int = None


class ModelServerConfig(Struct, rename=Renaming.SERVER_CONFIG):
    kick_user_price: int = None
    set_room_password_min_authority: int = None
    price_username_set: int = None
    server_language_change_time: int = None
    show_password_room_info_button: bool = None


class ModelRoom(Struct, rename=Renaming.ROOM):
    room_id: str = None
    min_players: int = None
    max_players: int = None
    min_level: int = None
    vip_enabled: bool = None
    status: int = None
    selected_roles: List[Roles] = None
    title: str = None
    password: str = None


class ModelShortUser(Struct, rename=Renaming.SHORT_USER):
    user_id: str = None
    username: str = None
    updated: int = None
    photo: str = None
    online: int = None
    is_vip: int = None
    vip_updated: int = None
    sex: Sex = Sex.MEN


class ModelFriend(Struct, rename=Renaming.FRIEND):
    friend_id: str = None
    updated: int = None
    user: ModelShortUser = None
    new_messages: int = None


class ModelMessage(Struct, rename=Renaming.MESSAGE):
    user_id: str = None
    friend_id: str = None
    created: int = None
    text: str = None
    message_style: int = None
    accepted: int = None
    message_type: int = None
