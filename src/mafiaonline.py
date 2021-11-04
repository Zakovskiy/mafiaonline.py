import requests
import socket
import json
import threading
from utils import tags
from utils import md5hash

class Client:
    def __init__(self, email, password, device_Id: str = "1316eefdd6dc27a9"):
        self.account = None
        self.token = None
        self.id = None
        self.device_Id = device_Id
        self.md5hash = md5hash.Client()
        self.data = []
        self.ip = "37.143.8.68"
        self.create_connection()
        self.sign_in(self.device_Id, email, password)

    def sign_in(self, device_Id, email, password):
        self.send_server({"d": device_Id, "ty": "sin",
                         "e": email, "pw": self.md5hash.md5Salt(password)})
        self.account = self.listen()["uu"]
        self.token = self.account["t"]
        self.id = self.account["o"]
        return self.account

    def sign_up(self, nickname, email, password, lang: str = "RUS"):
        data = {
            "email": email,
            "username": "",
            "password": self.md5hash.md5Salt(password),
            "deviceId": self.device_Id,
            "lang": lang}
        request = requests.post(
            f"http://{self.ip}:8008/user/sign_up",
            data=data,
            headers={
                "Content-Type": "application/x-www-form-urlencoded"}).json()
        if ("o" in request):
            self.send_server(
                {"t": request["t"], "ty": "uns", "u": nickname, "uo": request["o"]})
        return request

    def uns(self, nickname):
        self.send_server({"ty": "uns", "u": nickname, "uo": self.id})
        return self.listen()

    def vote_player_list(self, user, room_Id):
        self.send_server({"ty": "vpl", "uo": user, "ro": room_Id})
        return self.listen()

    def create_room(
        self,
        tt: str,
        vip: bool = True,
        br: bool = True,
        bd: bool = True,
        d: int = 0,
        dc: bool = True,
        jr: bool = True,
        lv: bool = True,
        sp: bool = True,
        tr: bool = True,
        mxp: int = 8,
        mnp: int = 1,
        pw: str = "",
            t: int = 0):
        self.send_server({"ty": "rc",
                          "uo": self.id,
                          "rr": {"br": br,
                                 "bd": bd,
                                 "d": d,
                                 "dc": dc,
                                 "jr": jr,
                                 "lv": lv,
                                 "mxp": mxp,
                                 "mnp": mnp,
                                 "pw": self.md5hash.md5Salt(pw),
                                 "sp": sp,
                                 "tr": tr,
                                 "t": t,
                                 "tt": tt,
                                 "venb": vip}})
        return self.listen()

    def friend_list(self):
        self.send_server({"ty": "acfl", "uo": self.id})
        return self.listen()

    def remove_friend(self, friend_Id):
        self.send_server({"ty": "rf", "f": friend_Id})
        return self.listen()

    def update_photo(self, file):
        self.send_server({"ty": "upp", "uo": self.id,
                         "f": base64.encodebytes(file).decode()})
        return self.listen()

    def update_photo_server(self, file):
        self.send_server({"ty": "ups", "f": base64.encodebytes(file).decode()})
        return self.listen()

    def update_sex(self, id: int = 0):
        self.send_server({"ty": "ucs", "uo": self.id, "s": id})
        return self.listen()

    def message_complaint(self, text, screenshot_Id, user_Id):
        self.send_server({"ty": "mc", "uo": user_Id,
                         "r": text, "sc": screenshot_Id})
        return self.listen()

    def get_room_list(self):
        self.send_server({"ty": "acrl", "uo": self.id})
        return self.listen()

    def get_messages(self, friend_Id):
        self.send_server({"ty": "acpc", "uo": self.id, "fp": friend_Id})
        return self.listen()

    def join_global_chat(self):
        self.send_server({"ty": "acc", "uo": self.id})
        return self.listen()

    def leave_global_chat(self):
        self.dashboard()

    def leave_room(self, room_Id):
        self.send_server({"ty": "rp", "ro": room_Id})

    def join_room(self, room_Id, password):
        self.send_server(
            {"ty": "re", "psw": self.md5hash.md5Salt(password), "ro": room_Id})
        return self.listen()

    def cp(self, room_Id):
        self.send_server({"ty": "cp", "uo": self.id, "ro": room_Id})
        return self.listen()

    def dashboard(self):
        self.send_server({"ty": "acd", "uo": self.id})

    def send_message_friend(self, friend_Id, content):
        self.send_server({"ty": "ac", "fp": friend_Id})
        self.send_server({"ty": "pmc", "m": {"fp": friend_Id, "tx": content}})
        return self.listen()

    def message(self):
        self.send_server({"ty": "m", "m": {"t": 1, "tx": "a"}})

    def send_message_global(self, content, style: int = 2):
        self.send_server(
            {"ty": "cmc", "m": {"c": 0, "tx": content, "mstl": style}})
        return self.listen()

    def send_message_room(self, content, room_Id, type: int = 1):
        self.send_server({"ty": "rmc",
                          "m": {"c": 1,
                                "ro": room_Id,
                                "tx": content,
                                "t": type,
                                "uu": {"u": "aaa"}}})
        return self.listen()

    def get_user(self, user_Id):
        self.send_server({"ty": "gup", "uo": user_Id})
        return self.listen()

    def get_room_players(self, room_Id):
        self.send_server({"ty": "gp", "ro": room_Id})
        return self.listen()

    def create_connection(self):
        self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.client_socket.connect((self.ip, 8090))
        self.live = True
        self.listener = threading.Thread(target=self.__listener).start()

    def __listener(self):
        while (self.live):
            bytes = bytes()
            while (True):
                recv = self.client_socket.recv(2048)
                read = len(recv)
                if read != -1:
                    i = read - 1
                    if r[i] == 0:
                        bytes = bytes + recv
                        decode = bytes.decode()
                        bytes = bytes()
                        for string in decode.strip().split("[\u0000]"):
                            string = string.strip()[0:-1]
                            if string != "p":
                                self.data.append(string)
                    else:
                        bytes = bytes + recv
                else:
                    return

    def send_server(self, j):
        j["t"] = self.token
        self.client_socket.sendall((json.dumps(j) + "\n").encode())

    def listen(self):
        while len(self.data) <= 0:
            pass
        response = self.data[0]
        del self.data[0]
        try:
            data = json.loads(response)
        except BaseException:
            data = {}
        return data

# There was github.com/deluvsushi
# Здесь был github.com/deluvsushi
