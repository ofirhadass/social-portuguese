from peewee import BooleanField, CompositeKey, ForeignKeyField, Model, SqliteDatabase, TextField


database = SqliteDatabase('spd.db')


class UnknownField(object):
    def __init__(self, *_, **__):
        pass


class BaseModel(Model):
    class Meta:
        database = database


class PartsOfSpeech(BaseModel):
    name = TextField()

    class Meta:
        table_name = 'parts_of_speech'


class Roles(BaseModel):
    name = TextField()

    class Meta:
        table_name = 'roles'


class Users(BaseModel):
    mail = TextField(primary_key=True)
    name = TextField()
    password = TextField()
    role = ForeignKeyField(column_name='role_id', field='id', model=Roles)

    class Meta:
        table_name = 'users'


class Translations(BaseModel):
    confirmed = BooleanField()
    explanation = TextField(null=True)
    part_of_speech = ForeignKeyField(column_name='part_of_speech_id', field='id', model=PartsOfSpeech)
    translation = TextField()
    updated_by = ForeignKeyField(column_name='updated_by', field='mail', model=Users, null=True)
    word = TextField()

    class Meta:
        table_name = 'translations'
        indexes = (
            (('word', 'translation'), True),
        )
        primary_key = CompositeKey('translation', 'word')

