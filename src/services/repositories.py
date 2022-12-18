from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Optional, Iterable, Union, Callable


class SearchAnnotation:
    pass


@dataclass(frozen=True)
class ValueAnnotation(SearchAnnotation):
    value: any


@dataclass(frozen=True)
class Greater(ValueAnnotation):
    pass


@dataclass(frozen=True)
class Lesser(ValueAnnotation):
    pass


@dataclass(frozen=True)
class Equal(ValueAnnotation):
    pass


@dataclass(frozen=True)
class Not(ValueAnnotation):
    pass


class GroupingAnnotation(SearchAnnotation):
    def __init__(self, *annotations: SearchAnnotation):
        self.annotations = annotations


class And(GroupingAnnotation):
    pass


class Or(GroupingAnnotation):
    pass


class IRepository(ABC):
    @abstractmethod
    def __iter__(self) -> iter:
        pass

    @abstractmethod
    def all(self) -> Iterable:
        pass

    @abstractmethod
    def add(self, instance: object) -> None:
        pass

    @abstractmethod
    def get_by(
        self,
        conditions: dict[str, SearchAnnotation | object] = dict(),
        *,
        is_many: bool = False,
        **additional_conditions: SearchAnnotation | object
    ) -> Optional[object | Iterable]:
        pass

    @abstractmethod
    def remove(self, instance: object) -> None:
        pass


class _RepositoryAnnotation:
    def __init__(self, repository_type: type, supported_types: Iterable[type]):
        self.repository_type = repository_type
        self.supported_types = supported_types

    @property
    def supported_types(self) -> tuple:
        return self._supported_types

    @supported_types.setter
    def supported_types(self, supported_types: Iterable) -> None:
        self._supported_types = tuple(supported_types)

        if not self._supported_types:
            raise AttributeError("The length of supported_types must be greater than zero")

    @property
    def centered_supported_types(self) -> Union:
        return Union[*self.supported_types]

    def __repr__(self) -> str:
        return "{repository_type_name}[{supported_type_part}]".format(
            repository_type_name=self.repository_type.__name__,
            supported_type_part=self.__get_formatted_supported_types()
        )

    def __instancecheck__(self, instance: object) -> bool:
        return (
            isinstance(instance, self.repository_type)
            and (
                not self.supported_types or any(
                    issubclass(instance_type, self.centered_supported_types)
                    for instance_type in instance.supported_storage_types
                )
            )
        )

    def __get_formatted_supported_types(self) -> str:
        supported_type_line = str(self.centered_supported_types)

        return (
            supported_type_line[supported_type_line.index('[') + 1:-1].replace(',', ' |')
            if (
                hasattr(self.centered_supported_types, '__origin__')
                and self.centered_supported_types.__origin__ is Union
            )
            else self.centered_supported_types.__name__
        )


class Repository(IRepository, ABC):
    _annotation_factory: Callable[[type, Iterable[type]], type] = _RepositoryAnnotation

    @property
    @abstractmethod
    def supported_storage_types(self) -> Iterable[type]:
        pass

    def __iter__(self) -> iter:
        return iter(self.all())

    def get_by(
        self,
        conditions: dict[str, SearchAnnotation | object | Iterable[SearchAnnotation]] = dict(),
        *,
        is_many: bool = False,
        **additional_conditions: SearchAnnotation | object | Iterable[SearchAnnotation]
    ) -> Optional[object | Iterable[object]]:
        return self._get_by_conditions(
            self._get_valid_conditions_by(conditions | additional_conditions),
            is_many
        )

    @classmethod
    def __class_getitem__(cls, supported_type_resource: type | Iterable[type]) -> type:
        return cls._annotation_factory(
            cls,
            (
                supported_type_resource
                if isinstance(supported_type_resource, Iterable)
                else (supported_type_resource, )
            )
        )

    @abstractmethod
    def _get_by_conditions(
        self,
        conditions: dict[str, Iterable[SearchAnnotation | object]],
        is_many: bool
    ) -> Optional[object] | Iterable[object]:
        pass

    def _get_valid_conditions_by(
        self,
        conditions: dict[str, SearchAnnotation | object | Iterable[SearchAnnotation]]
    ) -> dict[str, Iterable[SearchAnnotation | object]]:
        return {
            _: (condition, ) if not isinstance(condition, Iterable) else condition
            for _, condition in conditions.items()
        }
