from datetime import date, time
from pony.orm import Optional, PrimaryKey, Set, Database, Required

db = Database()


class Book(db.Entity):
    ISBN = PrimaryKey(str, 17)
    Author = Optional(str, 30)
    title = Optional(str, 50)
    publishing = Optional(str)
    year = Optional(int)
    Language = Optional(str, 3)
    Tags = Optional(str, 200)
    pages = Optional(int)
    userbooks = Set('Userbook')
    librarybooks = Set('Librarybook')


class User(db.Entity):
    id = PrimaryKey(int, auto=True)
    tg_id = PrimaryKey(int)
    Name = Optional(str, 10)
    Second_name = Optional(str, 15)
    phone = Optional(str, 16)
    email = Optional(str, 30)
    userbook = Optional('Userbook')


class Userbook(db.Entity):
    id = PrimaryKey(int, auto=True)
    user = Required(User)
    books = Set(Book)
    status = Optional(bool)
    # 0 - бронь 1 - на руках
    end_date = Optional(date)
    dop_time = Optional(bool)
    # 0  - не продлевалась
    # 1 - продлевалась


class Library(db.Entity):
    id_library = PrimaryKey(int, auto=True)
    Name = Optional(str, 100)
    Address = Optional(str, 100)
    phone = Optional(str, 16)
    vk_id = Optional(str, 20)
    librarybooks = Set('Librarybook')


class Library_hours(db.Entity):
    day_of_week = PrimaryKey(int, auto=True)
    open_time = Optional(time)
    close_time = Optional(time)
    is_active = Optional(bool)


class Library_exceptions(db.Entity):
    exception_id = PrimaryKey(int, auto=True)
    Date = Optional(date, unique=True)
    is_closed = Optional(bool)
    open_time = Optional(time)
    close_time = Optional(time)
    reason = Optional(str, 255)


class Library_recurring_exceptions(db.Entity):
    rule_id = PrimaryKey(int, auto=True)
    day_of_week = Optional(int)
    occurrence = Optional(int)
    is_closed = Optional(bool)
    open_time = Optional(time)
    close_time = Optional(time)
    reason = Optional(str, 255)
    start_date = Optional(date)
    end_date = Optional(date)


class Librarybook(db.Entity):
    id = PrimaryKey(int, auto=True)
    count_book = Optional(str)
    book = Required(Book)
    library = Required(Library)


# 💾 Привязка к SQLite файлу
db.bind(provider='sqlite', filename='library.sqlite', create_db=True)

# 🗂️ Создание таблиц
db.generate_mapping(create_tables=True)
