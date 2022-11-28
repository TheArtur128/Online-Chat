from abc import ABC, abstractmethod
from typing import Callable, Iterable


class ArgumentFactory(ABC):
    _original_factory: Callable
    _args: tuple
    _kwargs: dict

    _is_input_arguments_first: bool = False

    def __call__(self, *args, **kwargs) -> any:
        args = [args, self._args]

        if self._is_input_arguments_first:
            args.reverse()

        return self._original_factory(
            *(args[0] + args[1]),
            **self._kwargs,
            **kwargs
        )
