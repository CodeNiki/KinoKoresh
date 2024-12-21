from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import ContextTypes, ConversationHandler
import requests
import os
import signal
import logging
import time
import json

# Настройка логирования
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)

# Состояния анкеты
ASK_NAME, ASK_SURNAME, ASK_AGE, ASK_GENRES, ASK_ACTORS, ASK_FAVORITE_MOVIE, SHOW_RECOMMENDATIONS = range(7)

# URL вашего API
API_URL = "http://127.0.0.1:8000/recommendations"

# Главное меню
MAIN_MENU = [
    ["Пройти анкету заново", "Получить базовые рекомендации", "Оценить фильм", "Комплексное оценивание фильма"],
]

# Ограничение доступа
REQUEST_LIMIT = 5
REQUEST_INTERVAL = 60  # секунд
user_requests = {}

# Файл для хранения состояния пользователей
USER_STATE_FILE = 'user_states.json'

def load_user_states():
    if os.path.exists(USER_STATE_FILE):
        with open(USER_STATE_FILE, 'r') as file:
            return json.load(file)
    return {}

def save_user_states(user_states):
    with open(USER_STATE_FILE, 'w') as file:
        json.dump(user_states, file)

user_states = load_user_states()

def restrict_access(user_id):
    current_time = time.time()
    if user_id not in user_requests:
        user_requests[user_id] = []

    # Удаляем устаревшие запросы
    user_requests[user_id] = [t for t in user_requests[user_id] if current_time - t < REQUEST_INTERVAL]

    if len(user_requests[user_id]) >= REQUEST_LIMIT:
        return False

    user_requests[user_id].append(current_time)
    return True

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Начало анкеты."""
    user_id = str(update.message.from_user.id)
    if not restrict_access(user_id):
        await update.message.reply_text("Слишком много запросов. Пожалуйста, попробуйте позже.")
        return ConversationHandler.END

    if user_id in user_states:
        await update.message.reply_text("С возвращением! Что вы хотите сделать?")
        reply_markup = ReplyKeyboardMarkup(MAIN_MENU, resize_keyboard=True)
        await update.message.reply_text("Что вы хотите сделать дальше?", reply_markup=reply_markup)
        return ConversationHandler.END
    else:
        await update.message.reply_text("Привет! Я ваш бот. Давайте заполним анкету.\n\nКак вас зовут?")
        return ASK_NAME

async def handle_survey(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Обработка анкеты."""
    user_id = str(update.message.from_user.id)
    user_data = context.user_data
    current_state = context.user_data.get('current_state', ASK_NAME)

    if current_state == ASK_NAME:
        user_data['name'] = update.message.text
        await update.message.reply_text("Отлично! Теперь напишите вашу фамилию:")
        context.user_data['current_state'] = ASK_SURNAME
        return ASK_SURNAME

    elif current_state == ASK_SURNAME:
        user_data['surname'] = update.message.text
        await update.message.reply_text("Хорошо! Сколько вам лет?")
        context.user_data['current_state'] = ASK_AGE
        return ASK_AGE

    elif current_state == ASK_AGE:
        user_data['age'] = update.message.text
        await update.message.reply_text("Какие ваши любимые жанры фильмов? (например, комедия, драма):")
        context.user_data['current_state'] = ASK_GENRES
        return ASK_GENRES

    elif current_state == ASK_GENRES:
        user_data['genres'] = update.message.text
        await update.message.reply_text("Напишите ваших любимых актеров (через запятую):")
        context.user_data['current_state'] = ASK_ACTORS
        return ASK_ACTORS

    elif current_state == ASK_ACTORS:
        user_data['actors'] = update.message.text
        await update.message.reply_text("Какой ваш любимый фильм?")
        context.user_data['current_state'] = ASK_FAVORITE_MOVIE
        return ASK_FAVORITE_MOVIE

    elif current_state == ASK_FAVORITE_MOVIE:
        user_data['favorite_movie'] = update.message.text

        # Сохраняем состояние пользователя
        user_states[user_id] = user_data
        save_user_states(user_states)

        # Отправляем точные рекомендации
        await send_recommendations(update, context)

        # Показываем главное меню
        reply_markup = ReplyKeyboardMarkup(MAIN_MENU, resize_keyboard=True)
        await update.message.reply_text("Что вы хотите сделать дальше?", reply_markup=reply_markup)
        return ConversationHandler.END

async def send_recommendations(update: Update, context: ContextTypes.DEFAULT_TYPE, basic=False) -> None:
    """Функция отправки рекомендаций."""
    url = f"{API_URL}/basic_recommendations" if basic else API_URL
    payload = {}

    if not basic:
        payload = {
            "name": context.user_data.get("name", ""),
            "surname": context.user_data.get("surname", ""),
            "age": context.user_data.get("age", ""),
            "genres": context.user_data.get("genres", ""),
            "actors": context.user_data.get("actors", ""),
            "favorite_movie": context.user_data.get("favorite_movie", ""),
            "num_recommendations": 5,
        }

    try:
        response = requests.post(url, json=payload)
        response.raise_for_status()
        data = response.json()

        if data.get("status") != "success" or not data.get("recommendations"):
            await update.message.reply_text("К сожалению, я не смог найти подходящих рекомендаций.")
            return

        recommendations = data["recommendations"]
        messages = []
        for movie in recommendations:
            title = movie.get("title", "Без названия")
            genres = movie.get("genres_processed", "Жанры не указаны")
            director = movie.get("director", "Режиссер не указан")
            actors = movie.get("actors", "Актеры не указаны")

            message = (
                f"🎬 *{title}*\n"
                f"📖 Жанры: {genres}\n"
                f"🎥 Режиссер: {director}\n"
                f"⭐ Актеры: {actors}\n"
            )
            messages.append(message)

        # Отправляем каждую рекомендацию отдельным сообщением
        for msg in messages:
            await update.message.reply_text(msg, parse_mode="Markdown")
    except requests.RequestException as e:
        logger.error(f"Request error: {e}")
        await update.message.reply_text(f"Произошла ошибка: {e}")

async def show_basic_recommendations(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Показать базовые рекомендации."""
    logger.info("Basic recommendations command received")
    await send_recommendations(update, context, basic=True)

async def restart_survey(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Перезапуск анкеты."""
    await update.message.reply_text("Давайте начнем заново. Как вас зовут?")
    return ASK_NAME

async def stop(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Останавливает бота."""
    await update.message.reply_text("Бот остановлен.")
    os.kill(os.getpid(), signal.SIGINT)

async def rate_movie(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Оценить фильм."""
    await update.message.reply_text("Введите ID фильма и оценку (понравился/не понравился):")
    # Здесь можно добавить логику для обработки оценки фильма

async def complex_rate_movie(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Комплексное оценивание фильма."""
    await update.message.reply_text("Введите ID фильма и оценки по различным критериям (жанр, актеры, режиссер и т.д.):")
    # Здесь можно добавить логику для обработки комплексной оценки фильма

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Показать список команд."""
    help_text = (
        "Доступные команды:\n"
        "/start - Начать анкету\n"
        "/basic_recommendations - Получить базовые рекомендации\n"
        "/restart_survey - Пройти анкету заново\n"
        "/rate_movie - Оценить фильм\n"
        "/complex_rate_movie - Комплексное оценивание фильма\n"
        "/help - Показать список команд\n"
        "/stop - Остановить бота"
    )
    await update.message.reply_text(help_text)
