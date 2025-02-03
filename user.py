

class User:
    def __init__(self, id: int, login: str, password: str, balance: float = 0.0, is_admin: bool = False) -> None:
        self.id = id
        self.login = login
        self.password = password
        self.balance = balance
        self.is_admin = is_admin