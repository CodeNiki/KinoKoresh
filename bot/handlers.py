from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes

# Функция для обработки команды /start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text('Привет! Я бот для рекомендации фильмов. Используй команду /recommend, чтобы получить рекомендацию.')

# Функция для обработки команды /help
async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text('Используй команду /recommend, чтобы получить рекомендацию фильма.')

# Функция для обработки команды /recommend
async def recommend(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text('Пожалуйста, укажите жанр фильма, который вы хотите посмотреть.')

# Функция для запуска бота
def main() -> None:
    application = ApplicationBuilder().token('YOUR_BOT_TOKEN').build()

    # Регистрация обработчиков
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(CommandHandler("recommend", recommend))

    # Запуск бота
    application.run_polling()

if __name__ == '__main__':
    main()
