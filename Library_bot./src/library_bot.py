# Test commit 123
import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Application, CommandHandler, CallbackQueryHandler,
    MessageHandler, filters, ContextTypes, ConversationHandler)
from dotenv import load_dotenv
from os import getenv

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

REG_NAME, REG_SURNAME, REG_PHONE, REG_EMAIL = range(4)
SEARCH_TYPE, SEARCH_QUERY = range(2)

# Данные для тестирования
user_data_storage = {}

TEST_LIBRARIES = {
    1: {
        'name': 'Центральная библиотека',
        'address': 'ул. Ленина, 10',
        'phone': '88005553535',
        'work_hours': '9:00-20:00'
    },
    2: {
        'name': 'Библиотека искусств',
        'address': 'ул. Пушкина, 25',
        'phone': '88005553536',
        'work_hours': '10:00-19:00'
    }
}

TEST_BOOKS = [
    {'title': 'Мастер и Маргарита', 'author': 'Булгаков', 'library_id': 1,
     'available': True},
    {'title': 'Преступление и наказание', 'author': 'Достоевский',
     'library_id': 1, 'available': True},
    {'title': 'Война и мир', 'author': 'Толстой',
     'library_id': 2, 'available': True},
    {'title': '1984', 'author': 'Оруэлл', 'library_id': 2, 'available': True}
]


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id

    if user_id not in user_data_storage:
        await update.message.reply_text(
            "Здравствуй) С вами бот 'Твой библиотекарь'\n"
            "Для начала работы необходима авторизация\n\n"
            "Для начала введите ваше имя:"
        )
        return REG_NAME
    else:
        user = user_data_storage[user_id]
        keyboard = [
            [InlineKeyboardButton("Список библиотек",
                                  callback_data='libraries_list')],
            [InlineKeyboardButton("Поиск книг", callback_data='search_books')],
            [InlineKeyboardButton("Ваши книги", callback_data='my_books')]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)

        await update.message.reply_text(
            f"Добро пожаловать, {user['name']}!\nВыберите действие:",
            reply_markup=reply_markup
        )
        return ConversationHandler.END


# Функции регистрации (такие же как в версии 2.0)
async def register_name(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data['name'] = update.message.text
    await update.message.reply_text("Ваша фамилия:")
    return REG_SURNAME


async def register_surname(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data['surname'] = update.message.text
    await update.message.reply_text("Номер телефона:")
    return REG_PHONE


async def register_phone(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data['phone'] = update.message.text
    await update.message.reply_text("Электронная почта:")
    return REG_EMAIL


async def register_email(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    email = update.message.text

    user_data_storage[user_id] = {
        'name': context.user_data['name'],
        'surname': context.user_data['surname'],
        'phone': context.user_data['phone'],
        'email': email
    }

    keyboard = [
        [InlineKeyboardButton("Список библиотек",
                              callback_data='libraries_list')],
        [InlineKeyboardButton("Поиск книг", callback_data='search_books')],
        [InlineKeyboardButton("Ваши книги", callback_data='my_books')]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    await update.message.reply_text(
        "Регистрация завершена!\nТеперь вы можете пользоваться ботом.",
        reply_markup=reply_markup
    )

    context.user_data.clear()
    return ConversationHandler.END


async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Версия 3.0: Добавлен каталог книг и поиск"""
    query = update.callback_query
    await query.answer()

    data = query.data

    if data == 'libraries_list':
        await show_libraries_list(update, context)
    elif data == 'search_books':
        await show_search_options(update, context)
    elif data == 'my_books':
        await query.edit_message_text("Функция 'Ваши книги' в разработке")
    elif data.startswith('library_'):
        library_id = int(data.split('_')[1])
        await show_library_details(update, context, library_id)
    elif data.startswith('catalog_'):
        library_id = int(data.split('_')[1])
        await show_catalog(update, context, library_id)
    elif data in ['search_title', 'search_author']:
        await start_search(update, context, data)
    elif data == 'back_to_main':
        await return_to_main_menu(update, context)
    elif data == 'back_to_libraries':
        await show_libraries_list(update, context)


async def show_libraries_list(update: Update,
                              context: ContextTypes.DEFAULT_TYPE):
    keyboard = []

    for lib_id, lib_info in TEST_LIBRARIES.items():
        keyboard.append([
            InlineKeyboardButton(
                f"{lib_id}. {lib_info['name']}",
                callback_data=f'library_{lib_id}'
            )
        ])

    keyboard.append([InlineKeyboardButton("Назад",
                                          callback_data='back_to_main')])
    reply_markup = InlineKeyboardMarkup(keyboard)

    await update.callback_query.edit_message_text(
        "Список библиотек:\n\nВыберите библиотеку:",
        reply_markup=reply_markup
    )


async def show_library_details(update: Update,
                               context: ContextTypes.DEFAULT_TYPE,
                               library_id: int):
    lib_info = TEST_LIBRARIES.get(library_id)

    text = (
        f"{lib_info['name']}\n"
        f"Адрес: {lib_info['address']}\n"
        f"Телефон: {lib_info['phone']}\n"
        f"Часы работы: {lib_info['work_hours']}"
    )

    keyboard = [
        [InlineKeyboardButton("Открыть каталог книг",
                              callback_data=f'catalog_{library_id}')],
        [
            InlineKeyboardButton("Назад", callback_data='libraries_list'),
            InlineKeyboardButton("В начало", callback_data='back_to_main')
        ]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    await update.callback_query.edit_message_text(text,
                                                  reply_markup=reply_markup)


async def show_catalog(update: Update, context: ContextTypes.DEFAULT_TYPE,
                       library_id: int):
    """Показать каталог книг библиотеки"""
    library_books = [book for book in TEST_BOOKS if book['library_id'] ==
                     library_id]

    text = "Каталог книг:\n\n"

    for i, book in enumerate(library_books, 1):
        status = "Доступна" if book['available'] else "Занята"
        text += f"{i}. {book['title']}\n"
        text += f"   Автор: {book['author']} | {status}\n\n"

    keyboard = [
        [InlineKeyboardButton("Поиск по каталогу",
                              callback_data='search_books')],
        [
            InlineKeyboardButton("Назад",
                                 callback_data=f'library_{library_id}'),
            InlineKeyboardButton("В начало", callback_data='back_to_main')
        ]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    await update.callback_query.edit_message_text(text,
                                                  reply_markup=reply_markup)


async def show_search_options(update: Update,
                              context: ContextTypes.DEFAULT_TYPE):
    """Показать варианты поиска"""
    keyboard = [
        [InlineKeyboardButton("По названию", callback_data='search_title')],
        [InlineKeyboardButton("✍По автору", callback_data='search_author')],
        [InlineKeyboardButton("Назад", callback_data='back_to_main')]
    ]

    reply_markup = InlineKeyboardMarkup(keyboard)

    await update.callback_query.edit_message_text(
        "Поиск книг\n\nВыберите критерий поиска:",
        reply_markup=reply_markup
    )


async def start_search(update: Update, context: ContextTypes.DEFAULT_TYPE,
                       search_type: str):
    """Начать процесс поиска"""
    context.user_data['search_type'] = search_type
    search_text = "по названию" if search_type == \
        'search_title' else "по автору"

    await update.callback_query.edit_message_text(
        f"Введите текст для поиска {search_text}:"
    )


async def handle_search_query(update: Update,
                              context: ContextTypes.DEFAULT_TYPE):
    """Обработка поискового запроса"""
    query = update.message.text
    search_type = context.user_data.get('search_type')

    results = []
    for book in TEST_BOOKS:
        if search_type == 'search_title' and query.lower() in \
                book['title'].lower():
            results.append(book)
        elif search_type == 'search_author' and query.lower() in \
                book['author'].lower():
            results.append(book)

    if results:
        text = f"Найдено {len(results)} книг:\n\n"
        for i, book in enumerate(results, 1):
            status = "Доступна" if book['available'] else "Занята"
            text += f"{i}. {book['title']}\n"
            text += f"   Автор: {book['author']} | {status}\n\n"
    else:
        text = "Книги по вашему запросу не найдены."

    keyboard = [
        [InlineKeyboardButton("Новый поиск", callback_data='search_books')],
        [InlineKeyboardButton("В начало", callback_data='back_to_main')]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    await update.message.reply_text(text, reply_markup=reply_markup)


async def return_to_main_menu(update: Update,
                              context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id

    if user_id in user_data_storage:
        user = user_data_storage[user_id]
        keyboard = [
            [InlineKeyboardButton("Список библиотек",
                                  callback_data='libraries_list')],
            [InlineKeyboardButton("Поиск книг", callback_data='search_books')],
            [InlineKeyboardButton("Ваши книги", callback_data='my_books')]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)

        await update.callback_query.edit_message_text(
            f"Главное меню\nДобро пожаловать, {user['name']}!",
            reply_markup=reply_markup
        )


async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Операция отменена.")
    return ConversationHandler.END


def main():
    load_dotenv()
    BOT_TOKEN = getenv('TELEGRAM_BOT_TOKEN')
    app = Application.builder().token(BOT_TOKEN).build()

    conv_handler = ConversationHandler(
        entry_points=[CommandHandler('start', start)],
        states={
            REG_NAME: [MessageHandler(filters.TEXT & ~filters.COMMAND,
                                      register_name)],
            REG_SURNAME: [MessageHandler(filters.TEXT & ~filters.COMMAND,
                                         register_surname)],
            REG_PHONE: [MessageHandler(filters.TEXT & ~filters.COMMAND,
                                       register_phone)],
            REG_EMAIL: [MessageHandler(filters.TEXT & ~filters.COMMAND,
                                       register_email)]
        },
        fallbacks=[CommandHandler('cancel', cancel)]
    )

    search_handler = MessageHandler(filters.TEXT & ~filters.COMMAND,
                                    handle_search_query)

    app.add_handler(conv_handler)
    app.add_handler(CallbackQueryHandler(button_handler))
    app.add_handler(search_handler)

    app.run_polling()


if __name__ == '__main__':
    main()
