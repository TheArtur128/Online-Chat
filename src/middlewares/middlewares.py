from flask import redirect, request
from pyhandling import *
from pyhandling.annotations import checker_of, decorator

from adapters.tokens import JWTSerializator
from config import SECRET_KEY
from services.tokens import validate_access_token
from tools.utils import status_code_parsing_with_default, merge_events


def redirect_on_status_code_that(status_code_checker: checker_of[int], url_to_redirect: str) -> decorator:
    return (returnly |then>> next_action_decorator_of)(
        status_code_parsing_with_default(500)
        |then>> on_condition(
            status_code_checker,
            url_to_redirect >= close(redirect) |then>> eventually
        )
    )


require_access_token: decorator = merge_events |by| (
    event_as(getattr, request, "headers")
    |then>> (callmethod |by| 'get')
    |then>> (validate_access_token |by| JWTSerializator(SECRET_KEY))
)