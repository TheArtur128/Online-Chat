from typing import Final, Tuple, Iterable, Optional, Any, Callable
from pyannotating import AnnotationTemplate, input_annotation
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
