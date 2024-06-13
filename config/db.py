from peewee import BooleanField as _BooleanField
from peewee import CharField as _CharField
from peewee import DateTimeField as _DateTimeField
from peewee import ForeignKeyField as _ForeignKeyField
from peewee import IntegerField as _IntegerField
from peewee import Model as _Model
from peewee import TextField as _TextField
from peewee import UUIDField as _UUIDField
from playhouse.postgres_ext import PostgresqlExtDatabase as _Database

from config import settings


class Singleton(type):
    _instances = {}

    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            cls._instances[cls] = super(Singleton, cls).__call__(*args, **kwargs)
        return cls._instances[cls]


class Database(_Database, metaclass=Singleton):
    pass


def get_db():
    return Database(
        settings.DB_NAME,
        user=settings.DB_USER,
        password=settings.DB_PASSWORD,
        host=settings.DB_HOST,
        port=settings.DB_PORT,
    )


Model = _Model
UUIDField = _UUIDField
CharField = _CharField
DateTimeField = _DateTimeField
TextField = _TextField
ForeignKeyField = _ForeignKeyField
BooleanField = _BooleanField
IntegerField = _IntegerField
