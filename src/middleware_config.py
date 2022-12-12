from flask_middlewares.standard.error_handling import CustomHandlerErrorMiddleware, CustomJSONResponseErrorFormatter
from flask_middlewares.standard.status_code import AbortBadStatusCodeMiddleware, StatusCodeRedirectorMiddleware
from flask_middlewares.standard.sql_alchemy import SQLAlchemySessionFinisherMiddleware

from config import DEFAULT_JWT_SERIALIZATOR_FACTORY
from models import db
from services.middlewares import AccessTokenRequiredMiddleware
from services.utils import get_status_code_from_error


GLOBAL_MIDDLEWARES = (
    CustomHandlerErrorMiddleware(CustomJSONResponseErrorFormatter(
        (Exception, ),
        get_status_code_from_error,
        is_format_type=False
    )),
    SQLAlchemySessionFinisherMiddleware(db),
    AccessTokenRequiredMiddleware(DEFAULT_JWT_SERIALIZATOR_FACTORY())
)

MIDDLEWARES = (AbortBadStatusCodeMiddleware(), StatusCodeRedirectorMiddleware('views.login'))

IS_GLOBAL_MIDDLEWARES_HIGHER = False

MIDDLEWARE_ENVIRONMENTS = {
    'api': dict()
}