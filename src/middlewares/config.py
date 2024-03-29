from flask_middlewares.tools import BinarySet
from pyhandling import operation_by

from middlewares import require_access_token, redirect_on_status_code_that


MIDDLEWARE_ENVIRONMENTS = {
    'api': {
        "USE_FOR_BLUEPRINT": True,
        "VIEW_NAMES": BinarySet(non_included="api.userresource"),
        "MIDDLEWARES": [require_access_token]
    },
    "redirecting": {
        "USE_FOR_BLUEPRINT": "views",
        "VIEW_NAMES": BinarySet(non_included=["views.authorization"]),
        "MIDDLEWARES": [
            redirect_on_status_code_that(
                operation_by('==', 403),
                "views.authorization"
            )
        ]
    }
}