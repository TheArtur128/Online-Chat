from dataclasses import dataclass


class SearchAnnotation:
    pass


@dataclass(frozen=True)
class ValueAnnotation(SearchAnnotation):
    value: any


@dataclass(frozen=True)
class In(SearchAnnotation):
    pass


@dataclass(frozen=True)
class Equal(ValueAnnotation):
    pass


@dataclass(frozen=True)
class Greater(ValueAnnotation):
    pass


@dataclass(frozen=True)
class Lesser(ValueAnnotation):
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