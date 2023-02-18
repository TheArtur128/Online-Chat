from datetime import datetime
from typing import Protocol, runtime_checkable

from services.errors import RegistrationError
from services.repositories import IRepository
from services.tokens import token_coder
from tools.utils import get_time_after


@runtime_checkable
class Session(Protocol):
    cancellation_time: datetime


def is_session_timed_out(session: Session) -> bool:
    return datetime.now() < session.cancellation_time


@runtime_checkable
class Profile(Protocol):
    token: str


@runtime_checkable
class Account(Protocol):
    profile: Profile
    session: Session


def register_account(
    account: Account,
    account_repository: IRepository[Account],
    profile_repository: IRepository[Profile],
    session_validator: checker_of[Session]
) -> None:
    if profile_repository.get_by(token=account.profile.token) is not None:
        raise RegistrationError(
            f"{account.profile.name}'s profile already exists"
        )

    if not session_validator(account.session):
        raise RegistrationError(f"Session for {account.profile.name}'s account is invalid")

    account_repository.add(account)


def create_token_for(account: Account, coder: token_coder, life_minutes: int | float) -> str:
    return coder(
        dict(
            token=account.token,
            exp=get_time_after(life_minutes, is_time_raw=True)
        )
    )


