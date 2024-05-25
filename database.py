from peewee import SqliteDatabase, Model, CharField, DateTimeField
import datetime

db = SqliteDatabase('bot_history.db')


class BaseModel(Model):
    class Meta:
        database = db


class UserQuery(BaseModel):
    username = CharField()
    query = CharField()
    response = CharField()
    timestamp = DateTimeField(default=datetime.datetime.now)


db.connect()
db.create_tables([UserQuery])
