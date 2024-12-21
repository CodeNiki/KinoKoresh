from telegram.ext import (
    Application, CommandHandler, MessageHandler, filters,
    ConversationHandler
)
from handlers import (
    start, handle_survey, help_command, show_basic_recommendations,
    restart_survey, stop, rate_movie, complex_rate_movie
)
from config import TOKEN

# Определяем состояния анкеты
ASK_NAME, ASK_SURNAME, ASK_AGE, ASK_GENRES, ASK_ACTORS, ASK_FAVORITE_MOVIE, SHOW_RECOMMENDATIONS = range(7)

def main():
    application = Application.builder().token(TOKEN).build()

    # Создаем ConversationHandler
    conv_handler = ConversationHandler(
        entry_points=[CommandHandler("start", start)],
        states={
            ASK_NAME: [MessageHandler(filters.TEXT & ~filters.COMMAND, handle_survey)],
            ASK_SURNAME: [MessageHandler(filters.TEXT & ~filters.COMMAND, handle_survey)],
            ASK_AGE: [MessageHandler(filters.TEXT & ~filters.COMMAND, handle_survey)],
            ASK_GENRES: [MessageHandler(filters.TEXT & ~filters.COMMAND, handle_survey)],
            ASK_ACTORS: [MessageHandler(filters.TEXT & ~filters.COMMAND, handle_survey)],
            ASK_FAVORITE_MOVIE: [MessageHandler(filters.TEXT & ~filters.COMMAND, handle_survey)],
        },
        fallbacks=[CommandHandler("stop", stop)],
    )

    # Добавляем обработчики в приложение
    application.add_handler(conv_handler)
    application.add_handler(CommandHandler("basic_recommendations", show_basic_recommendations))
    application.add_handler(CommandHandler("restart_survey", restart_survey))
    application.add_handler(CommandHandler("rate_movie", rate_movie))
    application.add_handler(CommandHandler("complex_rate_movie", complex_rate_movie))
    application.add_handler(CommandHandler("help", help_command))

    application.run_polling()

if __name__ == "__main__":
    main()
