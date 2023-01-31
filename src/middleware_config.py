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
    get_flask_response_by_controller_response >= next_action_decorator_of |then>> DecoratorMiddleware,
    close(rollbackable, closer=post_partial)(
        on_condition(
            isinstance |by| AccessTokenInvalidError,
            mergely(
                json_response_of,
                message=str,
                status_code=get_status_code_from_error
            ),
            else_=raise_
        )
    ),
    mergely(
        take(rollbackable),
        db.session.commit >= eventually |then>> returnly |then>> next_action_decorator_of,
        db.session.rollback >= eventually |then>> returnly |then>> take
    ),
    AccessTokenRequiredMiddleware(
        TokenPromiser(DEFAULT_JWT_SERIALIZATOR_FACTORY()),
        FlaskAccessTokenGetter('access-token')
    )
)

json_response_of = dict |then>> jsonify

MIDDLEWARE_ENVIRONMENTS = {
    'api': {
        'USE_FOR_BLUEPRINT': True,
        'IS_GLOBAL_MIDDLEWARES_HIGHER': False,
        'MIDDLEWARES': (
            (
                mergely(
                    take(json_response_of),
                    on_condition(
                        isinstance |by| DocumentaryError,
                        convert_documentary_error_to_dict,
                        else_=mergely(take(dict), message=str)
                    ),
                    status_code=get_status_code_from_error
                )
                >= partial(on_condition, isinstance |by| ResorceError, else_=raise_)
                |then>> close(rollbackable, closer=post_partial)
            ),
        )
    },
    'views': {
        'USE_FOR_BLUEPRINT': True,
        'IS_GLOBAL_MIDDLEWARES_HIGHER': False,
        'MIDDLEWARES': (
            next_action_decorator_of(returnly(
                get_status_code_from
                |then>> on_condition(
                    post_partial(execute_operation, 'in', StatusCodeGroup.ERROR),
                    abort
                )
            )),
            next_action_decorator_of(returnly(
                get_status_code_from
                |then>> on_condition(
                    operation_by('==', 403),
                    "views.authorization" >= close(redirect) |then>> eventually
                )
            ))
        )
    }
}