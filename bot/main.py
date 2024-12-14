from telegram.ext import (
    Application, CommandHandler, MessageHandler, filters,
    ConversationHandler
)
from handlers import (
    start, ask_surname, ask_age, ask_genres, ask_actors,
    ask_favorite_movie, finish, show_basic_recommendations,
    restart_survey, stop, set_main_menu
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
            ASK_NAME: [MessageHandler(filters.TEXT & ~filters.COMMAND, ask_surname)],
            ASK_SURNAME: [MessageHandler(filters.TEXT & ~filters.COMMAND, ask_age)],
            ASK_AGE: [MessageHandler(filters.TEXT & ~filters.COMMAND, ask_genres)],
            ASK_GENRES: [MessageHandler(filters.TEXT & ~filters.COMMAND, ask_actors)],
            ASK_ACTORS: [MessageHandler(filters.TEXT & ~filters.COMMAND, ask_favorite_movie)],
            ASK_FAVORITE_MOVIE: [MessageHandler(filters.TEXT & ~filters.COMMAND, finish)],
        },
        fallbacks=[CommandHandler("stop", stop)],
    )

    # Добавляем обработчики в приложение
    application.add_handler(conv_handler)
    application.add_handler(CommandHandler("basic_recommendations", show_basic_recommendations))
    application.add_handler(CommandHandler("restart_survey", restart_survey))

    # Устанавливаем главное меню
    application.post_init = set_main_menu

    application.run_polling()

if __name__ == "__main__":
    main()
