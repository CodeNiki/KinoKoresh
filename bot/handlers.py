from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import ContextTypes, ConversationHandler
import requests
import os
import signal
import logging
from bot.db import get_connection  # Если не используется база, удалите эту строку.

# Настройка логирования
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)

# Состояния анкеты
ASK_NAME, ASK_SURNAME, ASK_AGE, ASK_GENRES, ASK_ACTORS, ASK_FAVORITE_MOVIE, SHOW_RECOMMENDATIONS = range(7)

# URL вашего API
API_URL = "http://127.0.0.1:8000/recommendations"

# Главное меню
MAIN_MENU = [
    ["Пройти анкету заново", "Получить базовые рекомендации"],
]

async def set_main_menu(application):
    """Устанавливает главное меню кнопок."""
    await application.bot.set_my_commands([
        ("restart_survey", "Пройти анкету заново"),
        ("basic_recommendations", "Получить базовые рекомендации"),
    ])

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Начало анкеты."""
    logger.info("Start command received")
    await update.message.reply_text("Привет! Я ваш бот. Давайте заполним анкету.\n\nКак вас зовут?")
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
    """Спросить предпочтительные жанры."""
    context.user_data['age'] = update.message.text
    await update.message.reply_text("Какие ваши любимые жанры фильмов? (например, комедия, драма):")
    return ASK_GENRES

async def ask_actors(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Спросить любимых актёров."""
    context.user_data['genres'] = update.message.text
    await update.message.reply_text("Напишите ваших любимых актеров (через запятую):")
    return ASK_ACTORS

async def ask_favorite_movie(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Спросить любимый фильм."""
    context.user_data['actors'] = update.message.text
    await update.message.reply_text("Какой ваш любимый фильм?")
    return ASK_FAVORITE_MOVIE

async def finish(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Завершить анкету и отправить точные рекомендации."""
    context.user_data['favorite_movie'] = update.message.text

    # Отправляем точные рекомендации
    await send_recommendations(update, context)

    # Показываем главное меню
    reply_markup = ReplyKeyboardMarkup(MAIN_MENU, resize_keyboard=True)
    await update.message.reply_text(
        "Что вы хотите сделать дальше?",
        reply_markup=reply_markup
    )
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
        response = requests.post(url, json=payload) if not basic else requests.get(url)
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
