from typing import Callable

from pyhandling import close, by, then

from orm.models import User, UserSession
from services.authorization import Profile, Session, Account
from tools.mapping import AttributeMapper


profile_mapper_for: Callable[[User], Profile] = close(AttributeMapper)(
    token="url_token"
)


session_mapper_for: Callable[[UserSession], Session] = close(AttributeMapper)(
    cancellation_time="cancellation_time"
)


account_mapper_for: Callable[[User], Account] = close(AttributeMapper)(
    profile=profile_mapping_for,
    session=(getattr |by| "session") |then>> session_mapper_for 
)