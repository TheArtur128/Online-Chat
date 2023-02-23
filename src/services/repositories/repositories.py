from abc import ABC, abstractmethod
from typing import Optional, Iterable, Union, Callable, Generic, Iterator, TypeVar

from pyannotating import Special, many_or_one

from services.repositories.search_annotations import *


StoredT = TypeVar("StoredT")


class IRepository(Generic[StoredT], ABC):
    @abstractmethod
    def __iter__(self) -> Iterator[StoredT]:
        pass

    @abstractmethod
    def all(self) -> Iterable[StoredT]:
        pass

    @abstractmethod
    def add(self, instance: StoredT) -> None:
        pass

    @abstractmethod
    def get_by(
        self,
        conditions: dict[str, Special[SearchAnnotation]] = dict(),
        *,
        is_many: bool = False,
        **keyword_conditions: Special[SearchAnnotation]
    ) -> Optional[many_or_one[StoredT]]:
        pass

    @abstractmethod
    def remove(self, instance: StoredT) -> None:
        pass


class MonolithicRepository(IRepository, ABC):
    def __iter__(self) -> Iterator[StoredT]:
        return iter(self.all())

    def get_by(
        self,
        conditions: dict[str, Special[SearchAnnotation]] = dict(),
        *,
        is_many: bool = False,
        **keyword_conditions: Special[SearchAnnotation]
    ) -> Optional[many_or_one[StoredT]]:
        return self._get_by_conditions(
            dict_value_map(as_collection, conditions | keyword_conditions),
            is_many
        )

    @abstractmethod
    def _get_by_conditions(
        self,
        conditions: dict[str, many_or_one[Special[SearchAnnotation]]],
        is_many: bool
    ) -> Optional[many_or_one[StoredT]]:
        pass