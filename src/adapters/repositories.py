from typing import Iterable, Optional, Callable

from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm.attributes import InstrumentedAttribute
from sqlalchemy.sql.expression import BinaryExpression, and_, or_, not_

from services.repositories import Repository
from services.repositories.search_annotations import *
from orm import db


class SQLAlchemyRepository(MonolithicRepository):
    def __init__(self, model: db.Model, session: SQLAlchemy):
        self._model = model
        self._session = session

    def all(self) -> Iterable[db.Model]:
        return self._model.query.all()

    def add(self, instance: db.Model) -> None:
        self._model.add(instance)

    def remove(self, instance: db.Model) -> None:
        self._model.delete(instance)

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

        objects = self._model.query.filter(*sqlalchemy_conditions)

        return objects.all() if is_many else objects.first()

    __sqlalchemy_grouper_by_annotation_type: dict[SearchAnnotation, Callable] = {
        And: and_, Or: or_, Not: not_
    }

    def __get_sqlalchemy_conditions_by(
        self,
        conditions: Iterable[SearchAnnotation | object],
        attribute_name: str
    ) -> Iterable[BinaryExpression]:
        model_attribute = getattr(self._model, attribute_name)
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



OriginalT = TypeVar("OriginalT")
ConvertedT = TypeVar("OriginalT")


class ConvertingRepository(IRepository, Generic[OriginalT, ConvertedT]):
    def __init__(
        self,
        repository: IRepository[OriginalT],
        converter: Callable[[OriginalT], ConvertedT],
        isoconverter: Callable[[ConvertedT], OriginalT]
    ):
        self._repository = repository

        self._converter = converter
        self._isoconverter = isoconverter

    def __iter__(self) -> Iterator[ConvertedT]:
        return iter(self.all())

    def all(self) -> Iterable[ConvertedT]:
        return tuple(map(self._converter, self._repository.all()))

    def add(self, instance: ConvertedT) -> None:
        self._repository.add(self._isoconverter(instance))

    def remove(self, instance: ConvertedT) -> None:
        self._repository.remove(self._isoconverter(instance))

    def get_by(
        self,
        conditions: dict[str, Special[SearchAnnotation]] = dict(),
        *,
        is_many: bool = False,
        **keyword_conditions: Special[SearchAnnotation]
    ) -> Optional[many_or_one[ConvertedT]]:
        found_object_resource = self._repository(conditions, is_many=is_many, **keyword_conditions)

        if found_object_resource is None:
            return None

        return tuple(map(self._converter, as_collection(found_object_resource)))