from typing import Callable

from pyhandling import close, by, then
from sculpting import Sculpture

from orm.models import User, UserSession
from rules.authorization import Profile, Session, Account


profile_sculture_from: Callable[[User], Profile] = close(Sculpture)(
    token="url_token"
)


session_sculture_from: Callable[[UserSession], Session] = close(Sculpture)(
    cancellation_time="cancellation_time"
)


account_sculture_from: Callable[[User], Account] = close(Sculpture)(
    profile=profile_sculture_from,
    session=(getattr |by| "session") |then>> session_sculture_from
)