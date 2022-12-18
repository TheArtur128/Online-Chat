from abc import ABC

from services.errors import AccountAlreadyExistsError
from services.repositories import Repository


class Account(ABC):
    url_token: str


class AccountRegistrar:
    def __init__(self, account_repository: Repository[Account]):
        self.account_repository = account_repository

    def __call__(self, account: Account) -> None:
        if self.account_repository.get_by(url_token=account.url_token) is not None:
            raise AccountAlreadyExistsError(
                f"Account with \"{account.url_token}\" url token already exists"
            )

        self.account_repository.add(account)