from typing import Optional
from enum import Enum, auto

from services.errors import AccessTokenError


class TokenDecoderResult(Enum):
    INCORRECT = auto()


class ITokenPromiser(ABC):
    @abstractmethod
    def __call__(self, token: Optional[str]) -> None:
        pass
token_coder = Callable[[dict], str]
token_decoder = Callable[[str], dict | TokenDecoderResult]


class TokenPromiser(ITokenPromiser):
    def __init__(self, token_decoder: ITokenDecoder):
        self.token_decoder = token_decoder

    def __call__(self, token: Optional[str]) -> None:
        if not token:
            raise MissingTokenError("Token is missing")
        
        if self.token_decoder.decode(token) is TokenDecoderResult.INCORRECT:
            raise InvalidTokenError("Token is invalid")