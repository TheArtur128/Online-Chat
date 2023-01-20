from flask import jsonify, abort
from flask_middlewares import DecoratorMiddleware
from flask_middlewares.standard.status_code import StatusCodeRedirectorMiddleware
from flask_middlewares.tools import ExceptionDictTemplater, get_status_code_from, StatusCodeGroup

from config import DEFAULT_JWT_SERIALIZATOR_FACTORY
from frameworks.flask import get_flask_response_by_controller_response, FlaskAccessTokenGetter
from infrastructure.errors import ResorceError, AccessTokenInvalidError
from infrastructure.middlewares import AccessTokenRequiredMiddleware
from orm import db
from pyhandling import *
from services.tokens import TokenPromiser
from tools.errors import DocumentaryError
from tools.formatters import convert_documentary_error_to_dict
from tools.utils import get_status_code_from_error


IS_GLOBAL_MIDDLEWARES_HIGHER = False

GLOBAL_MIDDLEWARES = (
    DecoratorMiddleware(
        partial(
            ActionChain(get_flask_response_by_controller_response).clone_with,
            is_other_handlers_on_the_left=True
        )
    ),
    DecoratorMiddleware(
        post_partial(
            rollbackable,
            on_condition(
                post_partial(isinstance, AccessTokenInvalidError),
                mergely(
                    take(dict),
                    ExceptionDictTemplater(is_format_type=False),
                    status_code=get_status_code_from_error
                ) |then>> jsonify,
                else_=raise_
            )
        )
    ),
    DecoratorMiddleware(
        mergely(
            take(rollbackable),
            close(call |then>> returnly(eventually(db.session.commit))),
            db.session.rollback >= eventually |then>> returnly |then>> take
        )
    ),
    AccessTokenRequiredMiddleware(
        TokenPromiser(DEFAULT_JWT_SERIALIZATOR_FACTORY()),
        FlaskAccessTokenGetter('access-token')
    )
)

MIDDLEWARE_ENVIRONMENTS = {
    'api': {
        'USE_FOR_BLUEPRINT': True,
        'IS_GLOBAL_MIDDLEWARES_HIGHER': False,
        'MIDDLEWARES': (
            DecoratorMiddleware(
                post_partial(
                    rollbackable,
                    CustomJSONResponseErrorFormatter(
                        (ResorceError, ),
                        get_status_code_from_error,
                        is_format_type=False
                    ) |then>> DocumentaryErrorJSONResponseFormatter()
                )
            )
        )
    },
    'views': {
        'USE_FOR_BLUEPRINT': True,
        'IS_GLOBAL_MIDDLEWARES_HIGHER': False,
        'MIDDLEWARES': (
            AbortBadStatusCodeMiddleware(),
            StatusCodeRedirectorMiddleware('views.authorization', 403)
        ),
    }
}