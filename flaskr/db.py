from flask_login import UserMixin
from peewee import *

db_handle = SqliteDatabase(None)

class BaseModel(Model):
    class Meta:
        database = db_handle


class Role(BaseModel):
    id = IntegerField(primary_key=True)
    title = TextField()


class User(UserMixin, BaseModel):
    name = TextField()
    username = TextField(unique=True, primary_key=True)
    password = TextField()
    role = ForeignKeyField(Role)

    def get_id(self) -> str:
        return self.username


class Material(BaseModel):
    id = CharField(primary_key=True)
    name = TextField()
    desc = TextField()
    thickness = TextField()
    z_offset = TextField()