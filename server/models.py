from peewee import *

db = SqliteDatabase('sqlite3.db')

class User(Model):
    name = CharField()
    chat_id = BigIntegerField(unique = True)

    class Meta:
        database = db 

class Fee(Model):
    wallet = CharField()
    chat_id = BigIntegerField()

    class Meta:
        database = db 

class Jettons(Model):
    wallet = CharField()
    total = BigIntegerField()

    class Meta:
        database = db 

class JettonsTransaction(Model):
    bos = CharField()
    wallet = CharField()


    class Meta:
        database = db 


db.connect()
db.create_tables([User ,Fee ,Jettons ,JettonsTransaction])