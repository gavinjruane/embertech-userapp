from dataclasses import dataclass
from enum import IntEnum

import bcrypt
from peewee import DoesNotExist

from flaskr.db import User


class Role(IntEnum):
    ADMIN = 1
    STANDARD = 2


@dataclass
class Credential:
    username: str
    password: str


def hash_password(password: str) -> bytes:
    return bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt())


def check_password(credential: Credential) -> bool:
    try:
        candidate: User = User.get(User.username == credential.username)
    except DoesNotExist:
        return False

    return bcrypt.checkpw(credential.password.encode("utf-8"), candidate.password.encode("utf-8"))

