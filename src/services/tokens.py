from typing import Optional
from enum import Enum, auto

from services.errors import AccessTokenError


class TokenDecoderResult(Enum):
    INCORRECT = auto()


token_coder = Callable[[dict], str]
token_decoder = Callable[[str], dict | TokenDecoderResult]


def validate_access_token(token: Optional[str], token_decoder: token_decoder) -> None:
    if not token:
        raise AccessTokenError("Access token is missing")

    if token_decoder(token) is TokenDecoderResult.INCORRECT:
        raise AccessTokenError("Access token is invalid")