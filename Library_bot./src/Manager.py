# from datetime import date, time
from pony.orm import db_session, select, count
from models import Book, User, Userbook, Library, \
    Librarybook


class DBManager:
    """Менеджер для работы с базой данных библиотеки"""

    # Книги

    @db_session
    def add_book(self, isbn, title, author=None, publishing=None, year=None,
                 language=None, tags=None, pages=None):
        """Добавить книгу в базу"""
        try:
            book = Book(
                ISBN=isbn,
                title=title,
                Author=author,
                publishing=publishing,
                year=year,
                Language=language,
                Tags=tags,
                pages=pages
            )
            return f"✅ Книга '{title}' добавлена с ISBN: {isbn}"
        except Exception as e:
            return f"❌ Ошибка: {e}"

    @db_session
    def get_all_books(self):
        """Получить все книги"""
        books = select(b for b in Book)[:]
        return books

    @db_session
    def get_book_by_isbn(self, isbn):
        """Найти книгу по ISBN"""
        return Book.get(ISBN=isbn)

    @db_session
    def search_books(self, search_term):
        """Поиск книг по названию, автору или тегам"""
        books = select(
            b for b in Book
            if search_term.lower() in b.title.lower()
            or search_term.lower() in (b.Author or "").lower()
            or search_term.lower() in (b.Tags or "").lower()
        )[:]
        return books

    @db_session
    def get_book_fields(self, isbn):
        """Получить все поля книги по ISBN"""
        book = Book.get(ISBN=isbn)
        if book:
            return {
                'ISBN': book.ISBN,
                'title': book.title,
                'Author': book.Author,
                'publishing': book.publishing,
                'year': book.year,
                'Language': book.Language,
                'Tags': book.Tags,
                'pages': book.pages
            }
        return None

    # Пользователь

    @db_session
    def add_user(self, id, name, second_name, phone=None, email=None):
        '''Добавляет нового пользователя.

        Параметры:
            id (int): telegram-id пользователя (user.id)
            name (str): имя пользователя
            second_name (str): фамилия пользователя
            phone (str): номер телефона пользователя
            email (str): адрес электронной почты пользователя
        '''
        try:
            user = User(
                tg_id=id,
                Name=name,
                Second_name=second_name,
                phone=phone,
                email=email
            )
            return f"✅ Пользователь {name} {second_name} "
            f"добавлен с ID: {user.id}"
        except Exception as e:
            return f"❌ Ошибка: {e}"

    @db_session
    def get_all_users(self):
        """Получить всех пользователей"""
        users = select(u for u in User)[:]
        return users

    @db_session
    def get_user_fields(self, user_id):
        """Получить все поля пользователя"""
        user = User.get(id=user_id)
        if user:
            return {
                'id': user.id,
                'Name': user.Name,
                'Second_name': user.Second_name,
                'phone': user.phone,
                'email': user.email
            }
        return None

    # Библиотеки

    @db_session
    def add_library(self, name, address, phone=None, vk_id=None):
        """Добавить библиотеку"""
        try:
            library = Library(
                Name=name,
                Address=address,
                phone=phone,
                vk_id=vk_id
            )
            return f"✅ Библиотека '{name}' добавлена "
            f"с ID: {library.id_library}"
        except Exception as e:
            return f"❌ Ошибка: {e}"

    @db_session
    def get_all_libraries(self):
        """Возвращает данные по библиотекам

        Возвращаемое значение:
            libraries (list): Данные библиотек

        """
        libraries = select(i for i in Library)[:]
        return libraries

    @db_session
    def get_library_fields(self, library_id):
        """Получить все поля библиотеки"""
        library = Library.get(id_library=library_id)
        if library:
            return {
                'id_library': library.id_library,
                'Name': library.Name,
                'Address': library.Address,
                'phone': library.phone,
                'vk_id': library.vk_id
            }
        return None

    # Экземпляры книг

    @db_session
    def add_book_to_library(self, isbn, library_id, count_book="1"):
        """Добавить книгу в библиотеку"""
        try:
            book = Book.get(ISBN=isbn)
            library = Library.get(id_library=library_id)

            if not book:
                return "❌ Книга не найдена"
            if not library:
                return "❌ Библиотека не найдена"

            library_book = Librarybook(
                book=book,
                library=library,
                count_book=count_book
            )
            return f"✅ Книга '{book.title}' добавлена "
            f"в библиотеку '{library.Name}'"
        except Exception as e:
            return f"❌ Ошибка: {e}"

    @db_session
    def get_books_in_library(self, library_id):
        """Получить все книги в библиотеке"""
        library = Library.get(id_library=library_id)
        if library:
            return library.librarybooks
        return []

    # Брать книги

    @db_session
    def borrow_book(self, user_id, isbn):
        """Пользователь берет книгу"""
        try:
            user = User.get(id=user_id)
            book = Book.get(ISBN=isbn)

            if not user:
                return "❌ Пользователь не найден"
            if not book:
                return "❌ Книга не найдена"

            # Создаем или получаем Userbook для пользователя
            userbook = user.userbook
            if not userbook:
                userbook = Userbook(user=user)

            userbook.books.add(book)
            return f"✅ Пользователь {user.Name} взял книгу '{book.title}'"
        except Exception as e:
            return f"❌ Ошибка: {e}"

    @db_session
    def get_user_books(self, user_id):
        """Получить книги пользователя"""
        user = User.get(id=user_id)
        if user and user.userbook:
            return user.userbook.books
        return []

    # Статистика

    @db_session
    def get_statistics(self):
        """Получить статистику по базе"""
        stats = {
            'total_books': count(b for b in Book),
            'total_users': count(u for u in User),
            'total_libraries': count(i for i in Library),
            'books_in_libraries': count(lb for lb in Librarybook),
            'borrowed_books': count(ub for ub in Userbook if ub.books)
        }
        return stats

    # Удаление

    @db_session
    def delete_book(self, isbn):
        """Удалить книгу"""
        book = Book.get(ISBN=isbn)
        if book:
            book_title = book.title
            book.delete()
            return f"✅ Книга '{book_title}' удалена"
        return "❌ Книга не найдена"

    @db_session
    def delete_user(self, user_id):
        """Удалить пользователя"""
        user = User.get(id=user_id)
        if user:
            user_name = f"{user.Name} {user.Second_name}"
            user.delete()
            return f"✅ Пользователь {user_name} удален"
        return "❌ Пользователь не найден"


# Экземпляр
db_manager = DBManager()
