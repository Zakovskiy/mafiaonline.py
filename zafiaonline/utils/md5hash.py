import hashlib

class Md5:
    @staticmethod
    def md5_hash(string: str) -> str:
        return hashlib.md5(string.encode()).hexdigest()

    @staticmethod
    def md5salt(string: str, salt="azxsw", iterations=5) -> str:
        for _ in range(iterations):
            string = Md5.md5_hash(string + salt)
        return string
