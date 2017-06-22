from peewee import *

db = SqliteDatabase('calculator.db')

class Profile(Model):
    """Profile Model holds name and GPA, has a one-to-many relationship with
    Course"""
    name = CharField(max_length=255, unique=True)
    GPA = DecimalField(default=0.0)

    class Meta:
        database = db

class Course(Model):
    """Course Model holds name, grade, hours, and has a many-to-one relationship
    with Profile"""
    name = CharField(max_length=255)
    grade = CharField(max_length=2)
    hours = IntegerField()
    profile = ForeignKeyField(Profile)

    class Meta:
        database = db
