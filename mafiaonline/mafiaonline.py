import socket
import json
import threading
import base64
import time
from .utils.md5hash import Md5
from .structures.packet_data_keys import PacketDataKeys
from .structures.models import ModelUser, ModelServerConfig, ModelRoom, ModelFriend, ModelMessage
from .structures.enums import Languages, Roles, Sex
from typing import List
from secrets import token_hex
from msgspec.json import decode
from .web import WebClient


class Client(WebClient):
    def __init__(self):
        self.token: str = None
        self.id: str = None
        self.md5hash = Md5()
        self.user: ModelUser = ModelUser()
        self.server_config: ModelServerConfig = ModelServerConfig()
        self.address = "37.143.8.68"
        self.alive = True
        self.data = []
        self.client_socket = None
        super().__init__(self)
        self.create_connection()

    def sign_in(self, email: str = None, password: str = None, token: str = None, user_id: str = None) -> ModelUser:
        """
        Sign in into user

        **Parametrs**
            - **email** : Email of the user
            - **password** : Password of the user
            - **token** : Token of the user
        **Returns**
            - **Success** : list
        """
        data = {
            "d": token_hex(10),
            "ty": PacketDataKeys.SIGN_IN_KEY
        }
        if not token:
            data["e"] = email
            data["pw"] = self.md5hash.md5Salt(password)
        else:
            data["o"] = user_id
            data["t"] = token
        self.send_server(data)
        data = self._get_data("usi")
        self.user = decode(json.dumps(data["uu"]), type=ModelUser)
        self.server_config = decode(json.dumps(data["scfg"]), type=ModelServerConfig)
        self.token = self.user.token
        self.id = self.user.user_id
        return self.user

    def kick_user_vote(self, room_id: str, value: bool = True) -> None:
        data = {
            "ty": "kuv",
            "ro": room_id,
            "v": value
        }
        self.send_server(data)

    def uns(self, nickname: str) -> None:
        data = {
            "ty": "uns",
            "u": nickname
        }
        self.send_server(data)

    def select_language(self, language: Languages = Languages.RUSSIAN) -> None:
        data = {
            "ty": "usls",
            "slc": language
        }
        self.send_server(data)

    def vote_player_list(self, user_id: str, room_id: str) -> None:
        data = {
            "ty": "vpl",
            "uo": user_id,
            "ro": room_id
        }
        self.send_server(data)

    def create_room(self, selected_roles: List[Roles] = [0], title: str = "", max_players: int = 8,
        min_players: int = 5, password: str = "", min_level: int = 1, vip_enabled: bool = False) -> ModelRoom:
        request_data = {
            "ty": "rc",
            "rr": {
                "mnp": min_players,
                "mxp": max_players,
                "pw": self.md5hash.md5Salt(password) if password else "",
                "d": 0,
                "sr": selected_roles,
                "mnl": min_level,
                "tt": title,
                "venb": vip_enabled
            }
        }
        self.send_server(request_data)
        time.sleep(1)
        data = self._get_data("rcd", True)
        while data["ty"] != "rcd":
            self.send_server(request_data)
            time.sleep(1)
            data = self._get_data("rcd", True)
            print("rerecvier")
        return decode(json.dumps(data["rr"]), type=ModelRoom)

    def friend_list(self) -> List[ModelFriend]:
        data = {
            "ty":  "acfl"
        }
        self.send_server(data)
        data = self._get_data("frl")
        friends: List[ModelFriend] = []
        for friend in data["frl"]:
            friends.append(decode(json.dumps(friend), type=ModelFriend))
        return friends

    def remove_friend(self, friend_id: str) -> None:
        data = {
            "ty": "rf",
            "f": friend_id
        }
        self.send_server(data)

    def update_photo(self, file: bytes) -> None:
        data = {
            "ty": "upp",
            "f": base64.encodebytes(file).decode()
        }
        self.send_server(data)

    def update_photo_server(self, file: bytes) -> None:
        data = {
            "ty": "ups",
            "f": base64.encodebytes(file).decode()
        }
        self.send_server(data)

    def update_sex(self, sex: Sex) -> dict:
        data = {
            "ty": "ucs",
            "s": sex
        }
        self.send_server(data)
        return self.listen()

    def message_complaint(self, reason: str, screenshot_id: int, user_id: str) -> dict:
        data = {
            "ty": "mc",
            "uo": user_id,
            "r": reason,
            "sc": screenshot_id  # get from update_photo_server()
        }
        self.send_server(data)
        return self.listen()

    def get_messages(self, friend_id: str) -> List[ModelMessage]:
        data = {
            "ty": "acpc",
            "fp": friend_id
        }
        self.send_server(data)
        data = self._get_data("pclms")
        messages: List[ModelMessage] = []
        for message in data["ms"]:
            messages.append(decode(json.dumps(message), type=ModelMessage))
        return messages

    def remove_player(self, room_id: str) -> None:
        data = {
            "ty": "rp",
            "ro": room_id
        }
        self.send_server(data)

    def create_player(self, room_id: str) -> None:
        """
        need run after join_room()

        :param room_id: id into room
        :return: None
        """
        data = {
            "ty": "cp",
            "ro": room_id
        }
        self.send_server(data)

    def join_room(self, room_id: str, password: str = "") -> None:
        data = {
            "ty": "re",
            "psw": self.md5hash.md5Salt(password) if password else "",
            "ro": room_id
        }
        self.send_server(data)

    def leave_room(self, room_id: str) -> None:
        data = {
            "ty": "rp",
            "ro": room_id
        }
        self.send_server(data)

    def role_action(self, user_id: str, room_id: str) -> None:
        data = {
            "ty": "ra",
            "uo": user_id,
            "ro": room_id
        }
        self.send_server(data, True)

    def acrl(self) -> None:
        data = {
            "ty": "acrl"
        }
        self.send_server(data)

    def join_global_chat(self) -> None:
        data = {
            "ty": "acc"
        }
        self.send_server(data)

    def leave_from_global_chat(self) -> None:
        self.dashboard()

    def dashboard(self) -> None:
        data = {
            "ty": "acd"
        }
        self.send_server(data)

    def send_message_friend(self, friend_id: str, content: str) -> None:
        data = {
            "ty": "pmc",
            "m": {
                "fp": friend_id,
                "tx": content
            }
        }
        self.send_server(data)

    def send_message_room(self, content: str, room_id: str, message_style: int = 0) -> None:
        data = {
            "ty": "rmc",
            "m": {
                "tx": content,
                "mstl": message_style
            },
            "ro": room_id
        }
        self.send_server(data)

    def send_message_global(self, content: str, message_style: int = 0):
        """
        Send message to global chat

        **Parametrs**
            - **content** - Content of message
            - **message_style** - Style of message
        """
        data = {
            "ty": "cmc",
            "m": {
                "tx": content,
                "mstl": message_style,
            }
        }
        self.send_server(data)

    def get_user(self, user_id: str) -> dict:
        data = {
            "ty": "gup",
            "uo": user_id
        }
        self.send_server(data)
        return self.listen()

    def create_connection(self) -> None:
        self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.client_socket.connect((self.address, 8090))
        self.listener = threading.Thread(target=self.__listener).start()

    def __listener(self) -> None:
        while self.alive:
            buffer = bytes()
            while self.alive:
                try:
                    r = self.client_socket.recv(2084)
                except:
                    print("error get data")
                    return
                read = len(r)
                if read not in [-1, 0, 1]:
                    i = read - 1
                    if r[i] == 0:
                        buffer = buffer + r
                        d = buffer.decode()
                        buffer = bytes()
                        for str in d.strip().split("\x00"):
                            if str not in ["", " "]:
                                if str == "p":
                                    try:
                                        self.client_socket.send("p\n".encode())
                                    except:
                                        return
                                    continue
                                #print(f"{self.user.username}: {str}")
                                self.data.append(str)
                    else:
                        buffer = buffer + r
                else:
                    return

    def send_server(self, data: dict, remove_token_from_object: bool = False) -> None:
        if not remove_token_from_object:
            data[PacketDataKeys.TOKEN_KEY] = self.token
        data[PacketDataKeys.USER_OBJECT_ID_KEY] = data.get(PacketDataKeys.USER_OBJECT_ID_KEY, self.id)
        self.client_socket.send((json.dumps(data)+"\n").encode())

    def listen(self, force: bool = False) -> dict:
        while not self.data and self.alive:
            if force:
                return {"ty": "empty"}
        res = self.data[0]
        del self.data[0]
        return json.loads(res)

    def _get_data(self, type: str, force: bool = False) -> dict:
        data = self.listen(force=force)
        while self.alive:
            if data.get("ty") in [type, "empty"]:
                return data
            data = self.listen(force=force)

    def __del__(self):
        self.alive = False
        self.client_socket.close()
