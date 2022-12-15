from infrastructure.services.repositories import IRepository
from infrastructure.errors import UserAlreadyExistsError
from orm.models import User


class UserRegistrar:
    def __init__(self, user_repository: IRepository):
        self.user_repository = user_repository

    def __call__(self, user: User) -> None:
        if self.user_repository.get_by(url_token=user.url_token) is not None:
            raise UserAlreadyExistsError(
                f"User with \"{user.url_token}\" url token already exists"
            )

        self.user_repository.add(user)