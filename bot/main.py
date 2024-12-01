from telegram.ext import Application, CommandHandler, MessageHandler, filters, ConversationHandler
from config import TOKEN
from handlers import start, ask_surname, ask_age, ask_genres, ask_actors, finish

# Состояния анкеты
ASK_NAME, ASK_SURNAME, ASK_AGE, ASK_GENRES, ASK_ACTORS = range(5)

def main():
    # Создаем приложение Telegram
    application = Application.builder().token(TOKEN).build()

    # Создаем ConversationHandler
    conv_handler = ConversationHandler(
        entry_points=[CommandHandler("start", start)],
        states={
            ASK_NAME: [MessageHandler(filters.TEXT & ~filters.COMMAND, ask_surname)],
            ASK_SURNAME: [MessageHandler(filters.TEXT & ~filters.COMMAND, ask_age)],
            ASK_AGE: [MessageHandler(filters.TEXT & ~filters.COMMAND, ask_genres)],
            ASK_GENRES: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, ask_actors)
            ],
            ASK_ACTORS: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, finish),
            ],
        },
        fallbacks=[],
    )

    # Регистрируем обработчики
    application.add_handler(conv_handler)

    # Запускаем бота
    application.run_polling()

if __name__ == "__main__":
    main()
