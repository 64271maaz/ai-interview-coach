import os
from dotenv import load_dotenv

# .env file se variables load karo
load_dotenv()

# is file ka current directory
basedir = os.path.abspath(os.path.dirname(__file__))

class Config:
    # Flask secret key - sessions/cookies secure karne ke liye
    SECRET_KEY = os.environ.get('SECRET_KEY')

    # SQLite database - instance folder ke andar banegi
    SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.join(basedir, 'instance', 'interview_coach.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # Gemini API key
    GEMINI_API_KEY = os.environ.get('GEMINI_API_KEY')