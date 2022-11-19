from os import getenv
from secrets import token_hex

from dotenv import load_dotenv


load_dotenv()


DEBUG = True
SECRET_KEY = token_hex()

DATABASE_NAME = getenv('DATABASE_NAME', 'online-chat-db')
DATABASE_PATH = getenv('DATABASE_PATH', 'localhost:5432')
DATABASE_USERNAME = getenv('DATABASE_USERNAME', 'postgres')
USER_DATABASE_PASSWORD = getenv('USER_DATABASE_PASSWORD')

SQLALCHEMY_DATABASE_URI = f"postgresql://{DATABASE_USERNAME}:{USER_DATABASE_PASSWORD}@{DATABASE_PATH}/{DATABASE_NAME}"
SQLALCHEMY_TRACK_MODIFICATIONS = False


if USER_DATABASE_PASSWORD is None:
    raise ValueError("Environment variable USER_DATABASE_PASSWORD not set")
