from dataclasses import dataclass
from enum import IntEnum

import bcrypt
from flask_login import current_user
from peewee import DoesNotExist, PeeweeException

from flaskr.db import User


class Role(IntEnum):
    ADMIN = 1
    STANDARD = 2


@dataclass
class LoginCredential:
    username: str
    password: str


@dataclass
class SignupCredential:
    name: str
    username: str
    hashed_password: bytes
    role: Role = Role.STANDARD


def hash_password(password: str) -> bytes:
    return bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt())


def check_password(credential: LoginCredential) -> tuple[bool, User | None]:
    try:
        candidate: User = User.get(User.username == credential.username)
    except DoesNotExist:
        return False, None

    stored_password = candidate.password or ""
    if stored_password.startswith("$2"):
        # Bcrypt-hashed password
        if bcrypt.checkpw(credential.password.encode("utf-8"), stored_password.encode("utf-8")):
            return True, candidate
        return False, None
    # Legacy plaintext password fallback for sample / dev data
    if credential.password == stored_password:
        return True, candidate
    return False, None


def create_user(credential: SignupCredential) -> bool:
    try:
        candidate: User = User.create(
            name=credential.name,
            username=credential.username,
            password=credential.hashed_password,
            role=credential.role
        )
        return True if candidate else False
    except PeeweeException:
        return False


def require_admin(current_user):
    if not current_user.is_authenticated or getattr(current_user, 'role_id', None) != 1:
        return False
    return True
