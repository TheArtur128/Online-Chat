from typing import Optional, Iterable
from json import dumps

from flask import Response, request

from infrastructure.controllers import AdditionalDataProxyController, ControllerResponse


class FlaskJSONRequestAdditionalProxyController(AdditionalDataProxyController):
    @property
    def additional_data(self) -> Iterable | dict:
        return request.json


class FlaskAccessTokenGetter:
    def __init__(self, token_key_name: str):
        self.token_key_name = token_key_name

    def __call__(self) -> Optional[str]:
        return request.cookies.get(self.token_key_name) or request.headers.get(self.token_key_name)


def get_json_data_from_request() -> dict | Iterable:
    return request.json


def get_flask_response_by_controller_response(controller_response: ControllerResponse) -> Response:
    headers = dict(controller_response.metadata)

    is_payload_json_like = (
        isinstance(controller_response.payload, Iterable)
        and any(not isinstance(item, str) for item in controller_response.payload)
    )

    if is_payload_json_like:
        headers['Content-Type'] = 'application/json'

    return Response(
        response=(
            dumps(controller_response.payload)
            if is_payload_json_like
            else controller_response.payload
        ),
        status=controller_response.status_code,
        headers=headers
    )