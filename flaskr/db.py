from peewee import *

db_handle = SqliteDatabase(None)

class BaseModel(Model):
    class Meta:
        database = db_handle


class Role(BaseModel):
    id = IntegerField(primary_key=True)
    title = TextField()


class User(BaseModel):
    name = TextField()
    username = TextField(unique=True, primary_key=True)
    password = TextField()
    role = ForeignKeyField(Role)