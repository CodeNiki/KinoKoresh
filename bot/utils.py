from sqlalchemy import create_engine, Column, Integer, String, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
from dotenv import load_dotenv
import os
from loguru import logger

# Загрузка переменных окружения из .env файла
load_dotenv()

# Настройка базы данных
DATABASE_URL = os.getenv("DATABASE_URL")
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# Определение моделей
class User(Base):
    __tablename__ = 'users'
    user_id = Column(Integer, primary_key=True, index=True)
    first_name = Column(String, index=True)
    genre = Column(String)
    favorite_movies = Column(String)
    favorite_actors = Column(String)
    favorite_directors = Column(String)

class Rating(Base):
    __tablename__ = 'ratings'
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey('users.user_id'))
    movie_id = Column(Integer)
    rating = Column(Integer)
    user = relationship("User", back_populates="ratings")

User.ratings = relationship("Rating", order_by=Rating.id, back_populates="user")

# Создание таблиц
Base.metadata.create_all(bind=engine)

def initialize_user(user_id: int, first_name: str) -> None:
    db = SessionLocal()
    user = db.query(User).filter(User.user_id == user_id).first()
    if not user:
        user = User(user_id=user_id, first_name=first_name)
        db.add(user)
        db.commit()
    db.close()

def send_survey(update: Update, context: CallbackContext) -> None:
    keyboard = [
        [InlineKeyboardButton("Да", callback_data='survey_yes')],
        [InlineKeyboardButton("Нет", callback_data='survey_no')]
    ]
    reply_markup = InlineKeyboardMark
