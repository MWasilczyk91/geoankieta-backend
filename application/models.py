# coding: utf-8

from peewee import (SqliteDatabase, Model, ForeignKeyField,
    PrimaryKeyField, IntegerField, DoubleField, TextField)
from os import path

backend = path.dirname(path.dirname(__file__))
db = SqliteDatabase(path.join(backend, 'geoankieta.db'), pragmas={
            'journal_mode': 'wal',
            'cache_size': -1 * 64000,  # 64MB
            'foreign_keys': 1,
            'ignore_check_constraints': 0,
            'synchronous': 0
        },
        autocommit = True,
        autorollback = True)

class BaseModel(Model):
    """Model bazowy dla bazy danych SQLite"""
    class Meta:
        database = db

class Users(BaseModel):
    """ Tabela z danymi o użytkowniku """
    id = PrimaryKeyField()
    email = TextField(unique=True)
    imie = TextField()
    nazwisko = TextField()
    specjalnosc = TextField()
    tytul = TextField()
    screen = TextField(null=True)
    obszary = TextField()

    class Meta:
        db_table = 'uzytkownicy'

class Surveys(BaseModel):
    """ Tabela z jednostkami ankiet (obszar ankietowy) """
    id = PrimaryKeyField()
    mapa = TextField()
    obszar = TextField()
    uzasadnienie = TextField()
    uzytkownik = ForeignKeyField(db_column='uzytkownik', model=Users, to_field='id')

    class Meta:
        db_table = 'ankiety'

class Answers(BaseModel):
    """ Tabela z odpowiedziami dla danej jednostki ankietowej """
    id = PrimaryKeyField()
    ankieta_id = ForeignKeyField(db_column='ankieta_id', model=Surveys, to_field='id')
    czynnik = TextField()
    ocena = IntegerField()
    pewnosc = DoubleField()
    waga = DoubleField(null=True)

    class Meta:
        db_table = 'odpowiedzi'