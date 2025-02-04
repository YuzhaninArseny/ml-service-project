import hashlib
import os

class User:
    def __init__(self, id: int, login: str, password: str, balance: float = 0.0, is_admin: bool = False) -> None:
        self.id = id
        self.login = login
        self._salt = os.urandom(32)
        self.password = self._hash_password(password)
        self.balance = balance
        self.is_admin = is_admin

    def _hash_password(self, password: str) -> str:
        key = hashlib.pbkdf2_hmac(
            'sha256',
            password.encode('utf-8'),
            self._salt,
            100000
        )
        return key.hex()

    def verify_password(self, password: str) -> bool:
        new_key = hashlib.pbkdf2_hmac(
            'sha256',
            password.encode('utf-8'),
            self._salt,
            100000
        )
        return new_key.hex() == self.password