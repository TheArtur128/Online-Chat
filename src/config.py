from os import getenv
from secrets import token_hex

from dotenv import load_dotenv

from models import Token
from services.factories import CustomArgumentFactory, UserAccessTokenFactory, CustomMinuteTokenFactory
from services.jwt_serializers import JWTSerializator
from services.middlewares import ServiceErrorFormatterMiddleware

load_dotenv()


DEBUG = True
SECRET_KEY = token_hex()

DATABASE_NAME = getenv('DATABASE_NAME', 'online-chat-db')
DATABASE_PATH = getenv('DATABASE_PATH', 'localhost:5432')
DATABASE_USERNAME = getenv('DATABASE_USERNAME', 'postgres')
USER_DATABASE_PASSWORD = getenv('USER_DATABASE_PASSWORD')

if USER_DATABASE_PASSWORD is None:
    raise ValueError("Environment variable USER_DATABASE_PASSWORD not set")


SQLALCHEMY_DATABASE_URI = f"postgresql://{DATABASE_USERNAME}:{USER_DATABASE_PASSWORD}@{DATABASE_PATH}/{DATABASE_NAME}"
SQLALCHEMY_TRACK_MODIFICATIONS = False

ACCESS_TOKEN_LIFE_MINUTES = 15
REFRESH_TOKEN_LIFE_DAYS = 30


DEFAULT_JWT_SERIALIZATOR_FACTORY = CustomArgumentFactory(JWTSerializator, SECRET_KEY)

DEFAULT_ACCESS_TOKEN_FACTORY = UserAccessTokenFactory(
    DEFAULT_JWT_SERIALIZATOR_FACTORY(),
    ACCESS_TOKEN_LIFE_MINUTES
)

DEFAULT_REFRESH_TOKEN_FACTORY = CustomMinuteTokenFactory(
    REFRESH_TOKEN_LIFE_DAYS*24*60,
    CustomArgumentFactory(token_hex, Token.body.comparator.type.length // 2)
)

