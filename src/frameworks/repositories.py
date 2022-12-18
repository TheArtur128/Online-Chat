from abc import ABC
from typing import Optional, Iterable, Callable

from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm.attributes import InstrumentedAttribute
from sqlalchemy.sql.expression import BinaryExpression, and_, or_, not_

from services.repositories import Repository, SearchAnnotation, GroupingAnnotation, Equal, Greater, Lesser, And, Or, Not
from orm import db
from orm.models import User


class SQLAlchemyRepository(Repository, ABC):
    _sqlalchemy_model: db.Model

    def __init__(self, session: SQLAlchemy):
        self.session = session

    def all(self) -> Iterable[db.Model]:
        return self._sqlalchemy_model.query.all()

    @property
    def supported_storage_types(self) -> tuple[db.Model]:
        return (self._sqlalchemy_model, )

    def add(self, instance: db.Model) -> None:
        self._sqlalchemy_model.add(instance)

    def remove(self, instance: db.Model) -> None:
        self._sqlalchemy_model.delete(instance)

    def _get_by_conditions(
        self,
        conditions: dict[str, Iterable[SearchAnnotation | object]],
        is_many: bool
    ) -> Optional[db.Model] | Iterable[db.Model]:
        sqlalchemy_conditions = list()

        for attribute_name, condition in conditions.items():
            sqlalchemy_conditions.extend(self.__get_sqlalchemy_conditions_by(
                condition, attribute_name
            ))

        objects = self._sqlalchemy_model.query.filter(*sqlalchemy_conditions)

        return objects.all() if is_many else objects.first()

    __sqlalchemy_grouper_by_annotation_type: dict[SearchAnnotation, Callable] = {
        And: and_, Or: or_, Not: not_
    }

    def __get_sqlalchemy_conditions_by(
        self,
        conditions: Iterable[SearchAnnotation | object],
        attribute_name: str
    ) -> Iterable[BinaryExpression]:
        model_attribute = getattr(self._sqlalchemy_model, attribute_name)
        sqlalchemy_conditions = list()

        for condition in conditions:
            if isinstance(condition, Greater):
                sqlalchemy_conditions.append(model_attribute > condition.value)
            elif isinstance(condition, Lesser):
                sqlalchemy_conditions.append(model_attribute < condition.value)
            elif isinstance(condition, GroupingAnnotation) or isinstance(condition, Not):
                sqlalchemy_conditions.append(
                    self.__sqlalchemy_grouper_by_annotation_type[type(condition)](
                        *self.__get_sqlalchemy_conditions_by(
                            (
                                condition.annotations
                                if isinstance(condition, GroupingAnnotation)
                                else (condition.value, )
                            ),
                            attribute_name
                        )
                    )
                )
            elif isinstance(condition, Equal) or not isinstance(condition, SearchAnnotation):
                sqlalchemy_conditions.append(model_attribute == (
                    condition.value
                    if isinstance(condition, Equal)
                    else condition
                ))

        return sqlalchemy_conditions


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