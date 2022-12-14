from os import getenv
from secrets import token_hex
from functools import partial

from dotenv import load_dotenv

from orm.models import UserSession
from infrastructure.services.factories import UserAccessTokenFactory, CustomMinuteUserSessionFactory
from tools.jwt_serializers import JWTSerializator


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


DEFAULT_JWT_SERIALIZATOR_FACTORY = partial(JWTSerializator, SECRET_KEY)

DEFAULT_ACCESS_TOKEN_FACTORY = UserAccessTokenFactory(
    DEFAULT_JWT_SERIALIZATOR_FACTORY(),
    ACCESS_TOKEN_LIFE_MINUTES
)

DEFAULT_USER_SESSION_FACTORY = CustomMinuteUserSessionFactory(
    REFRESH_TOKEN_LIFE_DAYS*24*60,
    partial(token_hex, UserSession.token.comparator.type.length // 2)
)
