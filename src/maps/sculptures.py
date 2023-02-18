from typing import Callable

from pyhandling import close, by, then
from sculpting import Sculture

from orm.models import User, UserSession
from services.authorization import Profile, Session, Account
from tools.mapping import AttributeMapper


profile_sculture_from: Callable[[User], Profile] = close(Sculture)(
    token="url_token"
)


session_sculture_from: Callable[[UserSession], Session] = close(Sculture)(
    cancellation_time="cancellation_time"
)


account_sculture_from: Callable[[User], Account] = close(Sculture)(
    profile=profile_sculture_from_user,
    session=(getattr |by| "session") |then>> session_mapper_for 
)


OriginalT = TypeVar("OriginalT")

original_from: Callable[[Sculture[OriginalT]], OriginalT] = (
    getattr |by| "_Sculpture__original"
)