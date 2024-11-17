import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Updater, CommandHandler, CallbackQueryHandler, MessageHandler, Filters, CallbackContext
import utils
from loguru import logger
from dotenv import load_dotenv
import os

# Загрузка переменных окружения из .env файла
load_dotenv()

# Настройка логирования
logger.add("bot.log", rotation="500 MB")

# Функция для обработки команды /start
def start(update: Update, context: CallbackContext) -> None:
    user = update.message.from_user
    utils.initialize_user(user.id, user.first_name)
    update.message.reply_text('Привет! Я бот для рекомендаций фильмов и сериалов. Начнем с анкетирования.')
    utils.send_survey(update, context)

# Функция для обработки команды /help
def help_command(update: Update, context: CallbackContext) -> None:
    update.message.reply_text('Доступные команды:\n/start - Начать\n/help - Помощь\n/recommend - Получить рекомендации')

# Функция для обработки команды /recommend
def recommend(update: Update, context: CallbackContext) -> None:
    user_id = update.message.from_user.id
    recommendations = utils.get_recommendations(user_id)
    update.message.reply_text('\n'.join(recommendations))

# Функция для обработки входящих сообщений
def handle_message(update: Update, context: CallbackContext) -> None:
    user_id = update.message.from_user.id
    message_text = update.message.text
    utils.process_message(user_id, message_text)
    update.message.reply_text('Спасибо за ваш ответ!')

# Функция для обработки нажатий на кнопки
def button(update: Update, context: CallbackContext) -> None:
    query = update.callback_query
    query.answer()
    data = query.data
    utils.process_button_click(query.from_user.id, data)
    query.edit_message_text(text=f"Вы выбрали: {data}")

def main() -> None:
    # Вставьте ваш токен Telegram API
    updater = Updater(os.getenv("7709530617:AAEW6grdu8pHMOLHv8l7YBXgDfe3vGSgmHY"))

    dispatcher = updater.dispatcher

    dispatcher.add_handler(CommandHandler("start", start))
    dispatcher.add_handler(CommandHandler("help", help_command))
    dispatcher.add_handler(CommandHandler("recommend", recommend))
    dispatcher.add_handler(MessageHandler(Filters.text & ~Filters.command, handle_message))
    dispatcher.add_handler(CallbackQueryHandler(button))

    updater.start_polling()
    updater.idle()

if __name__ == '__main__':
    main()
