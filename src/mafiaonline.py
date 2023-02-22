import requests
import socket
import json
import threading
import base64
from enum import IntEnum
from utils import md5hash


class Client:
    def __init__(self):
        self.account = None
        self.token = None
        self.id = None
        self.md5hash = md5hash.Client()
        self.data = []
        self.account = {}
        self.address = "37.143.8.68"
        self.rest_address = f"http://{self.address}:8008"
        self.alive = True
        self.create_connection()

    def encode_auth_header(self):
        return base64.b64encode(f"{self.id}=:={self.token}".encode("utf-8")).decode("utf-8").strip()
    
    def logout(self):
        response = requests.post(f"{self.rest_address}/user/sign_out",
            headers={
                "Content-Type": "application/x-www-form-urlencoded",
                "Authorization": self.encode_auth_header()
            }
        ).json()
        return response

    def sign_in(self, email: str, password: str):
        """
        Sign in into account

        **Parametrs**
            - **email** : Email of the account
            - **password** : Password of the account

        **Returns**
            - **Success** : list
        """
        data = {
            "d": "zxc90as090-d90p-so",
            "ty": "sin",
            "e": email,
            "pw": self.md5hash.md5Salt(password)
        }
        self.send_server(data)
        self.account = self.listen()["uu"]
        self.token = self.account["t"]
        self.id = self.account["o"]
        return self

    def sign_up(self, nickname, email, password, lang: str = "RUS"):
        data = {
            "email": email,
            "username": nickname,
            "password": self.md5hash.md5Salt(password),
            "deviceId": None,
            "lang": lang
        }
        response = requests.post(f"{self.rest_address}/user/sign_up",
            data=data,
            headers={
                "Content-Type": "application/x-www-form-urlencoded"
            }
        ).json()
        return response

    def user_change_sex(self, sex: int = 1):
        response = requests.post(f"{self.rest_address}/user/change/sex",
            data = {"sex": sex},
            headers={
                "Content-Type": "application/x-www-form-urlencoded",
                "Authorization":self.encode_auth_header()
            }
        ).json()
        return response

    def kick_user_vote(self, room_id, value: bool = True):
        self.send_server(
            {
                "ty": "kuv",
                "ro": room_id,
                "v": value
            }
        )
        
    def user_email_verify(self, lang: str = "RU"):
        response = requests.post(f"{self.rest_address}/user/email/verify",
            data = {"lang": lang},
            headers={
                "Content-Type": "application/x-www-form-urlencoded",
                "Authorization":self.encode_auth_header()
            }
        ).json()
        return response

    def user_get(self, id: str):
        response = requests.post(f"{self.rest_address}/user/get",
            data = {"userObjectId": id},
            headers={
                "Content-Type": "application/x-www-form-urlencoded",
                "Authorization":self.encode_auth_header()
            }
        ).json()
        return response

    def uns(self, nickname):
        self.send_server({"ty": "uns", "u": nickname})

    def select_language(self, language: str = "ru"):
        self.send_server({"ty": "usls", "slc": language})
        return self.listen()

    def vote_player_list(self, user, room_Id):
        self.send_server({"ty": "vpl", "uo": user, "ro": room_Id})

    def create_room(self, selected_roles: list = [11, 10], tt: str = "", d: int = 0, mxp: int = 8,
        mnp: int = 5, pw: str = "123", mnl: int = 1, vip: bool = False):
        self.send_server({"ty": "rc",
            "rr": {
                "mnp": mnp,
                "mxp": mxp,
                "pw": self.md5hash.md5Salt(pw) if pw else "",
                "d": d,
                "sr": selected_roles,
                "mnl": mnl,
                "tt": tt,
                "venb": vip
            }
        })
        return self._get_data("rcd")

    def friend_list(self):
        self.send_server({"ty":  "acfl"})
        return self.listen()

    def remove_friend(self, friend_Id):
        self.send_server({"ty": "rf", "f": friend_Id})
        return self.listen()

    def update_photo(self, file):
        self.send_server({"ty": "upp", "f": base64.encodebytes(file).decode()})
        return self.listen()

    def update_photo_server(self, file):
        self.send_server({"ty": "ups", "f": base64.encodebytes(file).decode()})
        return self.listen()

    def update_sex(self, id: int = 0):
        self.send_server({"ty": "ucs", "s": id})
        return self.listen()

    def message_complaint(self, text, screenshot_Id, user_Id):
        self.send_server({"ty": "mc", "uo": user_Id, "r": text, "sc": screenshot_Id})
        return self.listen()

    def get_messages(self, friend_id):
        self.send_server({"ty": "acpc", "fp": friend_id})
        return self.listen()

    def remove_player(self, room: str):
        self.send_server({"tu": "rp", "ro": room})

    def cp(self, room_Id):
        self.send_server({"ty": "cp", "ro": room_Id})
        return self.listen()

    def join_room(self, room_id: str, password: str = ""):
        self.send_server({"ty": "re", "psw": self.md5hash.md5Salt(password) if password else "", "ro": room_id})
        return self.listen()

    def leave_room(self, room_id: str):
        self.send_server({"ty": "rp", "ro": room_id})
        return self.listen()

    def join_global_chat(self):
        self.send_server({"ty": "acc"})

    def leave_global_chat(self):
        self.dashboard()

    def dashboard(self):
        self.send_server({"ty": "acd"})

    def send_message_friend(self, friend_id, content):
        self.send_server({"ty": "ac", "fp": friend_id})
        self.send_server({"ty": "pmc", "m": {"fp": friend_id, "tx": content}})
        return self.listen()

    def role_action(self, user: str, room: str) -> None:
        self.send_server({"ty": "ra", "uo": user, "ro": room}, True)

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

    def get_user(self, user_id):
        self.send_server({"ty": "gup", "uo": user_id})
        return self.listen()

    def create_connection(self):
        self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.client_socket.connect((self.address, 8090))
        self.listener = threading.Thread(target=self.__listener).start()

    def __listener(self):
        while self.alive:
            buffer = bytes()
            while self.alive:
                try:
                    r = self.client_socket.recv(2084)
                except:
                    del self
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
                                    self.client_socket.send("p\n".encode())
                                    continue
                                self.data.append(str)
                    else:
                        buffer = buffer + r
                else:
                    return

    def send_server(self, j: list, remove_token_from_object: bool = False):
        if not remove_token_from_object:
            j["t"] = self.token
        if "uo" not in j: j["uo"] = self.id
        self.client_socket.send((json.dumps(j)+"\n").encode())

    def listen(self, force: bool = False):
        while not self.data and self.alive:
            if force:
                return {"ty": "empty"}
        res = self.data[0]
        del self.data[0]
        return json.loads(res)

    def _get_data(self, type, force: bool = False):
        data = self.listen(force=force)
        while self.alive:
            if data.get("ty") in [type, "empty"]:
                return data
            data = self.listen(force=force)

    def __del__(self):
        self.alive = False
        self.client_socket.close()

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
