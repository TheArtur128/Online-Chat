from flask_middlewares.standard.error_handling import CustomHandlerErrorMiddleware, CustomJSONResponseErrorFormatter
from flask_middlewares.standard.status_code import AbortBadStatusCodeMiddleware, StatusCodeRedirectorMiddleware
from flask_middlewares.standard.sql_alchemy import SQLAlchemySessionFinisherMiddleware

from config import DEFAULT_JWT_SERIALIZATOR_FACTORY
from frameworks.flask import FlaskAccessTokenGetter, get_flask_response_by_controller_response
from infrastructure.middlewares import AccessTokenRequiredMiddleware, DocumentaryErrorJSONResponseFormatter, ControllerResponseFormatterMiddleware
from orm import db
from tools.utils import get_status_code_from_error


IS_GLOBAL_MIDDLEWARES_HIGHER = False

MIDDLEWARES = (
    AbortBadStatusCodeMiddleware(),
    StatusCodeRedirectorMiddleware('views.login')
)

GLOBAL_MIDDLEWARES = (
    ControllerResponseFormatterMiddleware(get_flask_response_by_controller_response),
    CustomHandlerErrorMiddleware((
        DocumentaryErrorJSONResponseFormatter(),
        CustomJSONResponseErrorFormatter(
            (Exception, ),
            get_status_code_from_error,
            is_format_type=False
        )
    )),
    SQLAlchemySessionFinisherMiddleware(db),
    AccessTokenRequiredMiddleware(
        DEFAULT_JWT_SERIALIZATOR_FACTORY(),
        FlaskAccessTokenGetter('access-token')
    )
)

MIDDLEWARE_ENVIRONMENTS = {
    'api': {'USE_FOR_BLUEPRINT': True}
}
