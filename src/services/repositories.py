from abc import ABC, abstractmethod
from typing import Iterable

from flask_sqlalchemy import SQLAlchemy

from orm import db
from orm.models import User


class IRepository(ABC):
    @abstractmethod
    def __contains__(self, instance: object) -> bool:
        pass

    @abstractmethod
    def add(self, instance: object) -> None:
        pass

    @abstractmethod
    def get_by(self, *, is_many: bool = False, **conditions) -> object | Iterable | None:
        pass

    @abstractmethod
    def delete(self, instance: object) -> None:
        pass


class SQLAlchemyRepository(IRepository, ABC):
    _sqlalchemy_model: db.Model

    def __init__(self, session: SQLAlchemy):
        self.session = session

    def add(self, instance: db.Model) -> None:
        self._sqlalchemy_model.add(instance)

    def get_by(self, *, is_many: bool = False, **conditions) -> db.Model | Iterable[db.Model] | None:
        objects = self._sqlalchemy_model.query.filter_by(**conditions)

        return objects.all() if is_many else objects.one()

    def delete(self, instance: db.Model) -> None:
        self._sqlalchemy_model.delete(instance)


class CustomSQLAlchemyRepository(SQLAlchemyRepository):
    def __init__(self, session: SQLAlchemy, sqlalchemy_model: db.Model):
        super().__init__(session)
        self.sqlalchemy_model = sqlalchemy_model

    @property
    def sqlalchemy_model(self) -> db.Model:
        return self._sqlalchemy_model

    @sqlalchemy_model.setter
    def sqlalchemy_model(self, sqlalchemy_model: db.Model) -> None:
        self._sqlalchemy_model = sqlalchemy_model


class UserRepository(SQLAlchemyRepository):
    _sqlalchemy_model = User