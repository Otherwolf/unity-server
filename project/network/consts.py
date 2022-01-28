from dataclasses import dataclass

@dataclass
class ServerSystemActions:
    USER_DISCONNECT: int = 2311
    USER_LOGOUT: int = 2345
