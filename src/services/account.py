from abc import ABC

from services.errors import AccountAlreadyExistsError
from services.repositories import Repository
from services.serializers import ICoder
from tools.utils import get_time_after


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


class AccountAccessTokenFactory:
    def __init__(self, access_token_coder: ICoder, life_minutes: int | float):
        self.access_token_coder = access_token_coder
        self.life_minutes = life_minutes

    def __call__(self, account: Account) -> str:
        return self.access_token_coder.encode({
            'url_token': account.url_token,
            'exp': get_time_after(self.life_minutes, is_time_raw=True)
        })