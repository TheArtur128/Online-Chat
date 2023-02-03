from typing import Protocol, runtime_checkable

from services.errors import AccountAlreadyExistsError
from services.repositories import IRepository
from services.tokens import token_coder
from tools.utils import get_time_after


@runtime_checkable
class Account(Protocol):
    url_token: str


def register_account(account: Account, repository: IRepository[Account]) -> None:
    if repository.get_by(url_token=account.url_token) is not None:
        raise AccountAlreadyExistsError(
            f"Account with \"{account.url_token}\" url token already exists"
        )

    repository.add(account)



class AccountTokenFactory:
    def __init__(self, token_coder: ITokenCoder, life_minutes: int | float):
        self.token_coder = token_coder
        self.life_minutes = life_minutes

    def __call__(self, account: Account) -> str:
        return self.token_coder.encode({
            'url_token': account.url_token,
            'exp': get_time_after(self.life_minutes, is_time_raw=True)
        })