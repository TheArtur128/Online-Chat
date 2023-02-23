from datetime import datetime
from typing import Protocol

from pyhandling.annotations import checker_of

from services.errors import RegistrationError
from services.repositories import IRepository
from services.tokens import token_coder
from tools.utils import get_time_after


class Session(Protocol):
    cancellation_time: datetime


def is_session_timed_out(session: Session) -> bool:
    return datetime.now() < session.cancellation_time


class Profile(Protocol):
    full_name: str
    short_name: str


def token_for(profile: Profile, coder: token_coder, life_minutes: int | float) -> str:
    return coder(
        dict(
            token=profile.full_name,
            exp=get_time_after(life_minutes, is_time_raw=True)
        )
    )


class Account(Protocol):
    profile: Profile
    session: Session


def register_account(
    account: Account,
    account_repository: IRepository[Account],
    profile_repository: IRepository[Profile],
    session_validator: checker_of[Session]
) -> None:
    if profile_repository.get_by(full_name=account.profile.full_name) is not None:
        raise RegistrationError(
            f"{account.profile.full_name}'s profile already exists"
        )

    if not session_validator(account.session):
        raise RegistrationError(f"Session for {account.profile.name}'s account is invalid")

    account_repository.add(account)