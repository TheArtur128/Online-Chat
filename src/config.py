from functools import partial
from os import getenv
from secrets import token_hex

from dotenv import load_dotenv


load_dotenv()


DEBUG = True
SECRET_KEY = token_hex()

DATABASE_NAME = getenv('DATABASE_NAME', 'online-chat-db')
DATABASE_PATH = getenv('DATABASE_PATH', 'localhost:5432')
DATABASE_USERNAME = getenv('DATABASE_USERNAME', 'postgres')
DATABASE_PASSWORD = getenv('DATABASE_PASSWORD')

if DATABASE_PASSWORD is None:
    raise ValueError("Environment variable DATABASE_PASSWORD not set")


SQLALCHEMY_DATABASE_URI = f"postgresql://{DATABASE_USERNAME}:{DATABASE_PASSWORD}@{DATABASE_PATH}/{DATABASE_NAME}"
SQLALCHEMY_TRACK_MODIFICATIONS = False


ACCESS_TOKEN_LIFE_MINUTES = 15
REFRESH_TOKEN_LIFE_DAYS = 30
