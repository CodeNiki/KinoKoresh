from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import ContextTypes, ConversationHandler

# Состояния анкеты
ASK_NAME, ASK_SURNAME, ASK_AGE, ASK_GENRES, ASK_ACTORS = range(5)

# Жанры фильмов для выбора
GENRES = ["Комедия", "Драма", "Фантастика", "Ужасы", "Боевик", "Мелодрама", "Аниме"]

# Популярные актёры
ACTORS = ["Роберт Дауни мл.", "Джонни Депп", "Леонардо ДиКаприо", "Скарлетт Йоханссон",
          "Том Круз", "Эмма Уотсон", "Киану Ривз"]

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Приветственное сообщение и начало анкеты."""
    await update.message.reply_text(
        "Привет! Я ваш бот. Давайте заполним анкету.\n\nКак вас зовут?"
    )
    return ASK_NAME

async def ask_surname(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Спросить фамилию."""
    context.user_data['name'] = update.message.text
    await update.message.reply_text("Отлично! Теперь напишите вашу фамилию:")
    return ASK_SURNAME

async def ask_age(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Спросить возраст."""
    context.user_data['surname'] = update.message.text
    await update.message.reply_text("Хорошо! Сколько вам лет?")
    return ASK_AGE

async def ask_genres(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Спросить любимые жанры фильмов."""
    context.user_data['age'] = update.message.text
    genres_keyboard = [[genre] for genre in GENRES] + [["Готово"]]
    reply_markup = ReplyKeyboardMarkup(genres_keyboard, one_time_keyboard=True, resize_keyboard=True)

    await update.message.reply_text(
        "Теперь выберите ваши любимые жанры фильмов. Вы можете выбрать несколько. "
        "Нажмите 'Готово', когда закончите:",
        reply_markup=reply_markup,
    )
    return ASK_GENRES

async def ask_actors(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Спросить любимых актёров."""
    chosen_genre = update.message.text

    # Если нажата кнопка "Готово", переходим к следующему вопросу
    if chosen_genre == "Готово":
        actors_keyboard = [[actor] for actor in ACTORS] + [["Готово"]]
        reply_markup = ReplyKeyboardMarkup(actors_keyboard, one_time_keyboard=True, resize_keyboard=True)

        await update.message.reply_text(
            "Теперь выберите ваших любимых актёров. Вы можете выбрать несколько. "
            "Нажмите 'Готово', когда закончите:",
            reply_markup=reply_markup,
        )
        return ASK_ACTORS

    # Добавляем жанр в список
    if "genres" not in context.user_data:
        context.user_data["genres"] = []
    context.user_data["genres"].append(chosen_genre)

    # Продолжаем собирать жанры
    return ASK_GENRES

async def finish(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Сохранить выбранных актёров и завершить анкету."""
    chosen_actor = update.message.text

    # Если нажата кнопка "Готово", завершаем анкету
    if chosen_actor == "Готово":
        name = context.user_data.get('name')
        surname = context.user_data.get('surname')
        age = context.user_data.get('age')
        genres = ', '.join(context.user_data.get('genres', []))
        actors = ', '.join(context.user_data.get('actors', []))

        await update.message.reply_text(
            f"Спасибо за заполнение анкеты!\n\nВот ваши данные:\n"
            f"Имя: {name}\nФамилия: {surname}\nВозраст: {age}\n"
            f"Любимые жанры: {genres}\nЛюбимые актёры: {actors}",
            reply_markup=None
        )
        return ConversationHandler.END

    # Добавляем актёра в список
    if "actors" not in context.user_data:
        context.user_data["actors"] = []
    context.user_data["actors"].append(chosen_actor)

    # Продолжаем собирать актёров
    return ASK_ACTORS
