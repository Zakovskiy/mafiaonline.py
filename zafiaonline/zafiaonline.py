import json
import threading
import base64
import time

from typing import List, Optional, Union
from secrets import token_hex
from msgspec.json import decode
from queue import Queue
from websocket import create_connection

from zafiaonline import ListenDataException
from zafiaonline.utils.md5hash import Md5
from zafiaonline.structures.packet_data_keys import PacketDataKeys
from zafiaonline.structures.models import ModelUser, ModelServerConfig, ModelRoom, ModelFriend, ModelMessage
from zafiaonline.structures.enums import Languages, Roles, Sex, RatingMode, RatingType
from zafiaonline.web import WebClient

class Client(WebClient):
    def __init__(self, proxy: Optional[list] = None, debug: Optional[bool] = False) -> None:
        self.proxy = proxy if proxy is not None else []
        self.debug = debug
        self.token: Optional[str] = None
        self.id: Optional[str] = None
        self.md5hash = Md5()
        self.user: ModelUser = ModelUser()
        self.server_config: ModelServerConfig = ModelServerConfig()
        self.address = "37.143.8.68"
        self.port = "7090"
        self.alive = True
        self.data = Queue()
        self.ws = None
        super().__init__(self)
        self.create_connection()
        self.listener = None

    def sign_in(self, email: str = "", password: str = "",
                token: str = "", user_id: str = "") -> Union[ModelUser, bool]:
        """
        Sign in into user

        **Parameters**
            - **email** : Email of the user
            - **password** : Password of the user
            - **token** : Token of the user
        **Returns**
            - **Success** : list
        """
        data = dict()
        data[PacketDataKeys.DEVICE_ID] = token_hex(10)
        data[PacketDataKeys.TYPE] = PacketDataKeys.SIGN_IN
        data[PacketDataKeys.EMAIL] = email
        data[PacketDataKeys.PASSWORD] = self.md5hash.md5salt(password) if password else ""
        data[PacketDataKeys.OBJECT_ID] = user_id
        data[PacketDataKeys.TOKEN] = token
        self.send_server(data)
        time.sleep(.5)
        data = self._get_data(PacketDataKeys.USER_SIGN_IN)
        while data[PacketDataKeys.TYPE] != PacketDataKeys.USER_SIGN_IN:
            return False
        self.user = decode(json.dumps(data[PacketDataKeys.USER]), type=ModelUser)
        self.server_config = decode(json.dumps(data[PacketDataKeys.SERVER_CONFIG]), type=ModelServerConfig)
        self.token = self.user.token
        self.id = self.user.user_id
        return self.user
        
    def get_rating(self, rating_type: RatingType = RatingType.AUTHORITY,
                   rating_mode: RatingMode = RatingMode.ALL_TIME) -> dict:
        data: dict = {
            PacketDataKeys.TYPE: PacketDataKeys.GET_RATING,
            PacketDataKeys.RATING_TYPE: rating_type,
            PacketDataKeys.RATING_MODE: rating_mode
        }
        self.send_server(data)
        return self._get_data(PacketDataKeys.RATING)

    def kick_user_vote(self, room_id: str, value: bool = True) -> None:
        data: dict = {
            PacketDataKeys.TYPE: PacketDataKeys.KICK_USER_VOTE,
            PacketDataKeys.ROOM_OBJECT_ID: room_id,
            PacketDataKeys.VOTE: value
        }
        self.send_server(data)
        
    def kick_user(self, user_id: str, room_id: str) -> None:
        data: dict = {
            PacketDataKeys.TYPE: PacketDataKeys.KICK_USER,
            PacketDataKeys.ROOM_OBJECT_ID: room_id,
            PacketDataKeys.USER_OBJECT_ID: user_id
        }
        self.send_server(data)

    def username_set(self, nickname: str) -> None:
        data: dict = {
            PacketDataKeys.TYPE: PacketDataKeys.USERNAME_SET,
            PacketDataKeys.USERNAME: nickname
        }
        self.send_server(data)

    def select_language(self, language: Languages = Languages.RUSSIAN) -> None:
        data: dict = {
            PacketDataKeys.TYPE: PacketDataKeys.USER_SET_SERVER_LANGUAGE,
            PacketDataKeys.SERVER_LANGUAGE: language
        }
        self.send_server(data)

    def vote_player_list(self, user_id: str, room_id: str) -> None:
        data: dict = {
            PacketDataKeys.TYPE: PacketDataKeys.VOTE_PLAYER_LIST,
            PacketDataKeys.USER_OBJECT_ID: user_id,
            PacketDataKeys.ROOM_OBJECT_ID: room_id
        }
        self.send_server(data)

    def create_room(self, selected_roles: Optional[List[Roles]] = None,
                    title: str = "", max_players: int = 8,
                    min_players: int = 5, password: str = "", min_level: int = 1,
                    vip_enabled: bool = False) -> ModelRoom:
        if selected_roles is None:
            selected_roles = [0]
        request_data: dict = {
            PacketDataKeys.TYPE: PacketDataKeys.ROOM_CREATE,
            PacketDataKeys.ROOM: {
                PacketDataKeys.MIN_PLAYERS: min_players,
                PacketDataKeys.MAX_PLAYERS: max_players,
                PacketDataKeys.PASSWORD: self.md5hash.md5salt(password) if password else "",
                PacketDataKeys.DEVICE_ID: 0,
                PacketDataKeys.SELECTED_ROLES: selected_roles,
                PacketDataKeys.MIN_LEVEL: min_level,
                PacketDataKeys.TITLE: title,
                PacketDataKeys.VIP_ENABLED: vip_enabled
            }
        }
        self.send_server(request_data)
        time.sleep(.5)
        data = self._get_data(PacketDataKeys.ROOM_CREATED)
        while data[PacketDataKeys.TYPE] != PacketDataKeys.ROOM_CREATED:
            self.send_server(request_data)
            time.sleep(.5)
            data = self._get_data(PacketDataKeys.ROOM_CREATED)
            print("receiver")
        return decode(json.dumps(data[PacketDataKeys.ROOM]), type=ModelRoom)

    def friend_list(self) -> List[ModelFriend]:
        data: dict = {
            PacketDataKeys.TYPE:  PacketDataKeys.ADD_CLIENT_TO_FRIENDSHIP_LIST
        }
        self.send_server(data)
        data = self._get_data(PacketDataKeys.FRIENDSHIP_LIST)
        friends: List[ModelFriend] = []
        for friend in data[PacketDataKeys.FRIENDSHIP_LIST]:
            friends.append(decode(json.dumps(friend), type=ModelFriend))
        return friends
    
    def search_player(self, nickname:str) -> dict:
        data: dict = {
            PacketDataKeys.TYPE: PacketDataKeys.SEARCH_USER,
            PacketDataKeys.SEARCH_TEXT: nickname
        }
        self.send_server(data)
        return self._get_data(PacketDataKeys.SEARCH_USER)

    def remove_friend(self, friend_id: str) -> None:
        data: dict = {
            PacketDataKeys.TYPE: PacketDataKeys.REMOVE_FRIEND,
            PacketDataKeys.FRIEND_USER_OBJECT_ID: friend_id
        }
        self.send_server(data)

    def update_photo(self, file: bytes) -> None:
        data: dict = {
            PacketDataKeys.TYPE: PacketDataKeys.UPLOAD_PHOTO,
            PacketDataKeys.FILE: base64.encodebytes(file).decode()
        }
        self.send_server(data)

    def update_photo_server(self, file: bytes) -> None:
        data: dict = {
            PacketDataKeys.TYPE: PacketDataKeys.UPLOAD_SCREENSHOT,
            PacketDataKeys.FILE: base64.encodebytes(file).decode()
        }
        self.send_server(data)

    def update_sex(self, sex: Sex) -> dict:
        data: dict = {
            PacketDataKeys.TYPE: PacketDataKeys.USER_CHANGE_SEX,
            PacketDataKeys.SEX: sex
        }
        self.send_server(data)
        return self.listen()

    def message_complaint(self, reason: str, screenshot_id: int, user_id: str) -> dict:
        data: dict = {
            PacketDataKeys.TYPE: PacketDataKeys.MAKE_COMPLAINT,
            PacketDataKeys.USER_OBJECT_ID: user_id,
            PacketDataKeys.REASON: reason,
            PacketDataKeys.SCREENSHOT: screenshot_id  # get from update_photo_server()
        }
        self.send_server(data)
        return self.listen()

    def get_messages(self, friend_id: str) -> List[ModelMessage]:
        data: dict = {
            PacketDataKeys.TYPE: PacketDataKeys.ADD_CLIENT_TO_PRIVATE_CHAT,
            PacketDataKeys.FRIENDSHIP: friend_id
        }
        self.send_server(data)
        data = self._get_data(PacketDataKeys.PRIVATE_CHAT_LIST_MESSAGES)
        messages: List[ModelMessage] = []
        for message in data[PacketDataKeys.MESSAGES]:
            messages.append(decode(json.dumps(message), type=ModelMessage))
        return messages

    def remove_player(self, room_id: str) -> None:
        data: dict = {
            PacketDataKeys.TYPE: PacketDataKeys.REMOVE_PLAYER,
            PacketDataKeys.ROOM_OBJECT_ID: room_id
        }
        self.send_server(data)
    

    def create_player(self, room_id: str) -> Optional[dict]:
        """
        need run after join_room()

        :param room_id: id into room
        :return: None
        """
        data: dict = {
            PacketDataKeys.TYPE: PacketDataKeys.CREATE_PLAYER,
            PacketDataKeys.ROOM_OBJECT_ID: room_id
        }
        self.send_server(data)
        return self._get_data(PacketDataKeys.PLAYERS)

    def join_room(self, room_id: str, password: str = "") -> None:
        data: dict = {
            PacketDataKeys.TYPE: PacketDataKeys.ROOM_ENTER,
            PacketDataKeys.ROOM_PASS: self.md5hash.md5salt(password) if password else "",
            PacketDataKeys.ROOM_OBJECT_ID: room_id
        }
        self.send_server(data)
        

    def leave_room(self, room_id: str) -> None:
        data: dict = {
            PacketDataKeys.TYPE: PacketDataKeys.REMOVE_PLAYER,
            PacketDataKeys.ROOM_OBJECT_ID: room_id
        }
        self.send_server(data)

    def role_action(self, user_id: str, room_id: str, room_model_type: int = 0) -> None:
        data: dict = {
            PacketDataKeys.TYPE: PacketDataKeys.ROLE_ACTION,
            PacketDataKeys.USER_OBJECT_ID: user_id,
            PacketDataKeys.ROOM_OBJECT_ID: room_id,
            PacketDataKeys.ROOM_MODEL_TYPE: room_model_type
        }
        self.send_server(data, True)

    def add_client_to_rooms_list(self) -> None:
        data: dict = {
            PacketDataKeys.TYPE: PacketDataKeys.ADD_CLIENT_TO_ROOMS_LIST
        }
        self.send_server(data)

    def join_global_chat(self) -> None:
        data: dict = {
            PacketDataKeys.TYPE: PacketDataKeys.ADD_CLIENT_TO_CHAT
        }
        self.send_server(data)

    def leave_from_global_chat(self) -> None:
        self.dashboard()

    def dashboard(self) -> None:
        data: dict = {
            PacketDataKeys.TYPE: PacketDataKeys.ADD_CLIENT_TO_DASHBOARD
        }
        self.send_server(data)

    def send_message_friend(self, friend_id: str, content: str) -> None:
        data: dict = {
            PacketDataKeys.TYPE: PacketDataKeys.PRIVATE_CHAT_MESSAGE_CREATE,
            PacketDataKeys.MESSAGE: {
                PacketDataKeys.FRIENDSHIP: friend_id,
                PacketDataKeys.TEXT: content
            }
        }
        self.send_server(data)

    def send_message_room(self, content: str, room_id: str, message_style: int = 0) -> None:
        data: dict = {
            PacketDataKeys.TYPE: PacketDataKeys.ROOM_MESSAGE_CREATE,
            PacketDataKeys.MESSAGE: {
                PacketDataKeys.TEXT: content,
                PacketDataKeys.MESSAGE_STYLE: message_style
            },
            PacketDataKeys.ROOM_OBJECT_ID: room_id
        }
        self.send_server(data)

    def send_message_global(self, content: str, message_style: int = 0) -> None:
        """
        Send message to global chat

        **Parameters**
            - **content** - Content of message
            - **message_style** - Style of message
        """
        data: dict = {
            PacketDataKeys.TYPE: PacketDataKeys.CHAT_MESSAGE_CREATE,
            PacketDataKeys.MESSAGE: {
                PacketDataKeys.TEXT: content,
                PacketDataKeys.MESSAGE_STYLE: message_style,
            }
        }
        self.send_server(data)

    def get_user(self, user_id: str) -> dict:
        data: dict = {
            PacketDataKeys.TYPE: PacketDataKeys.GET_USER_PROFILE,
            PacketDataKeys.USER_OBJECT_ID: user_id
        }
        self.send_server(data)
        return self._get_data(PacketDataKeys.USER_PROFILE)

    def match_making_get_status(self) -> dict:
        data: dict = {
            PacketDataKeys.TYPE: PacketDataKeys.MATCH_MAKING_GET_STATUS
        }
        self.send_server(data)
        return self._get_data("mmms")

    def match_making_get_users_waits_count(self, players_size: int = 8) -> dict:
        data: dict = {
            PacketDataKeys.TYPE: "mmguiabk",
            "mmbpa": players_size
        }
        self.send_server(data)
        return self._get_data("mmuiabk")

    def match_making_add_user(self, players_size: int = 8) -> None:
        data: dict = {
            PacketDataKeys.TYPE: PacketDataKeys.MATCH_MAKING_ADD_USER,
            "mmbpa": players_size
        }
        self.send_server(data)

    def match_making_remove_user(self) -> None:
        data: dict = {
            PacketDataKeys.TYPE: "mmruk"
        }
        self.send_server(data)

    def remove_type(self, room_model_type: int) -> None:
        data: dict = {
            PacketDataKeys.TYPE: PacketDataKeys.GIVE_UP,
            PacketDataKeys.ROOM_MODEL_TYPE: room_model_type
        }
        self.send_server(data)

    def create_connection(self) -> None:
        self.ws = create_connection(f"ws://{self.address}:{self.port}")
        self.listener = threading.Thread(target=self.__listener).start()

    def __listener(self) -> None:
        while self.alive:
            try:
                get_string_data = self.ws.recv()
                self.data.put(get_string_data)
                self.ws.ping()
            except ListenDataException as e:
                print("error get data", e)

    def send_server(self, data: dict, remove_token_from_object: bool = False) -> None:
        if not remove_token_from_object:
            data[PacketDataKeys.TOKEN] = self.token
        data[PacketDataKeys.USER_OBJECT_ID] = data.get(PacketDataKeys.USER_OBJECT_ID, self.id)
        self.ws.send((json.dumps(data)+"\n").encode())

    def listen(self) -> dict:
        response = self.data.get(timeout=5)
        return json.loads(response)

    def _get_data(self, mafia_type: str) -> dict:
        data: dict = self.listen()
        while self.alive:
            if data.get(PacketDataKeys.TYPE) in [mafia_type, "empty", PacketDataKeys.ERROR_OCCUR]:
                return data
            data: dict = self.listen()

    def give_up(self, room_id: str, room_model_type: int = 0) -> None:
        data: dict = {
            PacketDataKeys.TYPE: PacketDataKeys.GIVE_UP,
            PacketDataKeys.ROOM_OBJECT_ID: room_id,
            PacketDataKeys.ROOM_MODEL_TYPE: room_model_type
        }
        self.send_server(data)

    def __del__(self) -> None:
        self.alive = False
        self.ws.close()