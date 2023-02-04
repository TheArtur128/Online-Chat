from dataclasses import dataclass
from typing import Final, Tuple, Iterable, Optional, Any, Callable, TypeVar

from pyannotating import AnnotationTemplate, input_annotation
from pyhandling import returnly, by, return_, then, mergely, take, close, post_partial, event_as, raise_, on_condition
from pyhandling.annotations import dirty, reformer_of, handler, handler_of


attribute_getter_of = handler_of
attribute_setter_of = AnnotationTemplate(Callable, [[input_annotation, Any], Any])

attribute_getter = attribute_getter_of[object]
attribute_setter = attribute_setter_of[object]


_MAGIC_METHODS_NAMES: Final[Tuple[str]] = (
    "__pos__", "__neg__", "__abs__", "__invert__", "__round__", "__floor__",
    "__ceil__", "__iadd__", "__isub__", "__imul__", "__ifloordiv__", "__idiv__",
    "__itruediv__", "__imod__", "__ipow__", "__ilshift__", "__irshift__",
    "__iand__", "__ior__", "__ixor__", "__int__", "__float__", "__complex__",
    "__oct__", "__hex__", "__index__", "__trunc__", "__str__", "__repr__",
    "__unicode__", "__format__", "__hash__", "__nonzero__", "__add__", "__sub__",
    "__mul__", "__floordiv__", "__truediv__", "__mod__", "__pow__", "__lt__",
    "__le__", "__eq__", "__ne__", "__ge__"
)


def method_proxies_to_attribute(attribute_name: str, method_names: Iterable[str]) -> dirty[reformer_of[type]]:
    @returnly
    def decorator(type_: type, attribute_name: str) -> type:
        if attribute_name[:2] == '__':
            attribute_name = f"_{type_.__name__}{attribute_name}"

        for methods_name in method_names:
            _proxy_method_to_attribute(attribute_name, methods_name, type_)

    return decorator |by| attribute_name


def _proxy_method_to_attribute(attribute_name: str, method_name: str, type_: type) -> None:
    def method_wrapper(instance: object, *args, **kwargs):
        return getattr(getattr(instance, attribute_name), method_name)(*args, **kwargs)

    setattr(
        type_,
        method_name,
        method_wrapper
    )


def setting_of(attribute_name: str) -> attribute_setter:
    def wrapper(object_: object, value: Any) -> Any:
        return setattr(object_, attribute_name, value)

    return wrapper


attribute_owner = TypeVar("attribute_owner")


@dataclass(frozen=True)
class AttributeMap(Generic[attribute_owner]):
    getter: attribute_getter_of[attribute_owner]
    setter: attribute_setter_of[attribute_owner]


attribute_map_for: Callable[[str], AttributeMap] = mergely(
    take(AttributeMap),
    close(getattr, closer=post_partial),
    setting_of
)
