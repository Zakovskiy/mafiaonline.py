import requests
import base64
from .structures.enums import Languages, Sex


class WebClient:
    def __init__(self, client) -> None:
        self.client = client
        self.rest_address = f"http://{self.client.address}:8008"

    @property
    def auth_headers(self) -> dict:
        return {
            "Content-Type": "application/x-www-form-urlencoded",
            "Authorization": self.encode_auth_header()
        }

    def encode_auth_header(self) -> str:
        return base64.b64encode(f"{self.client.id}=:={self.client.token}".encode("utf-8")).decode("utf-8").strip()

    def logout(self) -> dict:
        response = requests.post(f"{self.client.rest_address}/user/sign_out", headers=self.auth_headers).json()
        return response

    def sign_up(self, nickname: str, email: str, password, language: Languages = Languages.RUSSIAN) -> dict:
        data = {
            "email": email,
            "username": nickname,
            "password": self.client.md5hash.md5Salt(password),
            "deviceId": None,
            "lang": language
        }
        response = requests.post(f"{self.rest_address}/user/sign_up", data=data,
                                 headers={"Content-Type": "application/x-www-form-urlencoded"}).json()
        return response

    def user_change_sex(self, sex: Sex) -> dict:
        data = {
            "sex": sex
        }
        response = requests.post(f"{self.rest_address}/user/change/sex",
                                 data=data, headers=self.auth_headers).json()
        return response

    def user_email_verify(self, language: Languages = Languages.RUSSIAN) -> None:
        data = {
            "lang": language
        }
        response = requests.post(f"{self.rest_address}/user/email/verify",
                                 ata=data, headers=self.auth_headers).json()
        return response

    def user_get(self, _id: str) -> None:
        data = {
            "userObjectId": _id
        }
        response = requests.post(f"{self.rest_address}/user/get", data=data, headers=self.auth_headers).json()
        return response
