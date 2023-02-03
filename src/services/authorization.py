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


def create_token_for(account: Account, coder: token_coder, life_minutes: int | float) -> str:
    return coder(
        dict(
            url_token=account.url_token,
            exp=get_time_after(life_minutes, is_time_raw=True)
        )
    )