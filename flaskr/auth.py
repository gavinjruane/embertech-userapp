from dataclasses import dataclass
from enum import IntEnum

import bcrypt

from flaskr import db


class Role(IntEnum):
    ADMIN = 1
    STANDARD = 2


def credentials_from_tuple(t: list) -> Credential:
    return Credential(
        name=t[0],
        username=t[1],
        password=t[2],
        role=t[3]
    )


@dataclass
class Credential:
    def __init__(self, name: str, username: str, password: str, role: Role = Role.STANDARD):
        self.name: str = name
        self.username: str = username
        self.hashed_password: bytes = hash_password(password)
        self.role: Role = Role.STANDARD


def hash_password(password: str) -> bytes:
    return bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt())

def get_credentials(username: str, password: str) -> Credential:
    matches = db.select(f"SELECT * FROM Users WHERE username = {username}")

    if len(matches) > 0:
        credential = credentials_from_tuple(matches[0])
        is_correct: bool = bcrypt.checkpw(password.encode("utf-8"), credential.hashed_password)

    return Credential(username, username, password)
