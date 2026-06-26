from datetime import date
from datetime import time
from pony.orm import *


db = Database()


class Book(db.Entity):
    ISBN = PrimaryKey(str, 17, auto=True)
    Author = Optional(str, 30)
    title = Optional(str, 50)
    publishing = Optional(str)
    year = Optional(int, size=8)
    Language = Optional(str, 3)
    Tags = Optional(str, 200)
    pages = Optional(int, size=8)
    userbooks = Set('Userbook')
    librarybooks = Set('Librarybook')


class User(db.Entity):
    id = PrimaryKey(int, auto=True)
    Name = Optional(str, 10)
    Second_name = Optional(str, 15)
    phone = Optional(int, size=16)
    email = Optional(str, 30)
    userbook = Optional('Userbook')


class Userbook(db.Entity):
    id = PrimaryKey(int, auto=True)
    user = Required(User)
    books = Set(Book)


class Library(db.Entity):
    id_library = PrimaryKey(int, auto=True)
    Name = Optional(str, 100)
    Address = Optional(str, 100)
    phone = Optional(int, size=16)
    vk_id = Optional(str, 20)
    librarybooks = Set('Librarybook')
    library_hours = Optional('Library_hours')


class Library_hours(db.Entity):
    day_of_week = PrimaryKey(int, size=8, auto=True)
    open_time = Optional(time)
    close_time = Optional(time)
    is_active = Optional(bool)
    library = Required(Library)


class Library_exceptions(db.Entity):
    exception_id = PrimaryKey(int, auto=True)
    date = Optional(date)
    is_closed = Optional(bool)
    open_time = Optional(time)
    close_time = Optional(time)
    reason = Optional(str, 255)
    UNIQUE = Optional(date)


class Ibrary_recurring_exceptions(db.Entity):
    rule_id = PrimaryKey(int, size=64, auto=True)
    day_of_week = Optional(int, size=8)
    occurrence = Optional(int, size=8)
    is_closed = Optional(bool)
    open_time = Optional(time)
    close_time = Optional(time)
    reason = Optional(str, 255)
    start_date = Optional(date)
    end_date = Optional(date)


class Librarybook(db.Entity):
    id = PrimaryKey(int, auto=True)
    count_book = Optional(str)
    books = Set(Book)
    librarys = Set(Library)



db.generate_mapping()
