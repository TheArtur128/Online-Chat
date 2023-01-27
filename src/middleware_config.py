from functools import partial

from flask import jsonify, abort, redirect
from flask_middlewares import DecoratorMiddleware
from flask_middlewares.tools import get_status_code_from, StatusCodeGroup
from pyhandling import *

from config import DEFAULT_JWT_SERIALIZATOR_FACTORY
from frameworks.flask import get_flask_response_by_controller_response, FlaskAccessTokenGetter
from infrastructure.errors import ResorceError, AccessTokenInvalidError
from infrastructure.middlewares import AccessTokenRequiredMiddleware
from orm import db
from services.tokens import TokenPromiser
from tools.errors import DocumentaryError
from tools.formatters import convert_documentary_error_to_dict
from tools.utils import get_status_code_from_error


IS_GLOBAL_MIDDLEWARES_HIGHER = False

GLOBAL_MIDDLEWARES = (
    DecoratorMiddleware(
        partial(
            ActionChain(get_flask_response_by_controller_response).clone_with,
            is_other_handlers_left=True
        )
    ),
    DecoratorMiddleware(
        close(rollbackable, closer=post_partial)(
            on_condition(
                post_partial(isinstance, AccessTokenInvalidError),
                mergely(
                    take(dict |then>> jsonify),
                    message=str,
                    status_code=get_status_code_from_error
                ),
                else_=raise_
            )
        )
    ),
    DecoratorMiddleware(
        mergely(
            take(rollbackable),
            db.session.commit >= eventually |then>> returnly |then>> next_action_decorator_of,
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
                mergely(
                    take(dict |then>> jsonify),
                    on_condition(
                        post_partial(isinstance, DocumentaryError),
                        partial(convert_documentary_error_to_dict, is_converting_error_type_name=False),
                        else_=mergely(take(dict), message=str)
                    ),
                    status_code=get_status_code_from_error
                )
                >= partial(on_condition, post_partial(isinstance, ResorceError), else_=raise_)
                |then>> close(rollbackable, closer=post_partial)
            ),
        )
    },
    'views': {
        'USE_FOR_BLUEPRINT': True,
        'IS_GLOBAL_MIDDLEWARES_HIGHER': False,
        'MIDDLEWARES': (
            DecoratorMiddleware(next_action_decorator_of(
                get_status_code_from
                |then>> on_condition(
                    post_partial(execute_operation, 'in', StatusCodeGroup.ERROR),
                    abort
                )
            )),
            DecoratorMiddleware(next_action_decorator_of(
                get_status_code_from
                |then>> on_condition(
                    post_partial(execute_operation, '==', 403),
                    "views.authorization" >= close(redirect) |then>> eventually
                )
            ))
        )
    }
}