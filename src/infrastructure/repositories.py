from models import db, User


class IRepository(ABC):
    def add(self, instance: object) -> None:
        pass

    def get(self, id: int) -> object:
        pass

    def filter_by(self, **conditions) -> object:
        pass

    def get_all(self) -> Iterable:
        pass


class SQLAlchemyRepository(IRepository, ABC):
    _sqlalchemy_model: db.Model

    def __init__(self, session: SQLAlchemy):
        self.session = session

    def add(self, instance: db.Model) -> None:
        self._sqlalchemy_model.add(instance)

    def get_by(self, *, is_many: bool = False, **conditions) -> object:
        objects = self._sqlalchemy_model.query.filter_by(**conditions)

        return objects.all() if is_many else objects.one()

    def delete(self, instance: db.Model) -> None:
        self._sqlalchemy_model.delete(instance)


class UserRepository(SQLAlchemyRepository):
    _sqlalchemy_model = User