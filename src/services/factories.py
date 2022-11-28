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


class CustomArgumentFactory(ArgumentFactory):
    def __init__(self, original_factory: Callable, *args, is_input_arguments_first: bool = True, **kwargs):
        self._original_factory = original_factory
        self.args = args
        self.kwargs = kwargs
        self._is_input_arguments_first = is_input_arguments_first

    @property
    def args(self) -> tuple:
        return self._args

    @args.setter
    def args(self, args: Iterable) -> None:
        self._args = tuple(args)

    @property
    def kwargs(self) -> dict:
        return self._kwargs

    @kwargs.setter
    def kwargs(self, kwargs: dict) -> None:
        self._kwargs = dict(kwargs)

    @property
    def is_input_arguments_first(self) -> bool:
        return self._is_input_arguments_first

    @is_input_arguments_first.setter
    def is_input_arguments_first(self, is_input_arguments_first: bool) -> None:
        self._is_input_arguments_first = is_input_arguments_first


class TokenFactory(ABC):
    _original_token_factory: Callable[[str, datetime], Token] = Token

    def __call__(self) -> Token:
        return self._original_token_factory(
            body=self._create_token_body(),
            cancellation_time=self._get_token_cancellation_time()
        )

    @abstractmethod
    def _create_token_body(self) -> str:
        pass

    @abstractmethod
    def _get_token_cancellation_time(self) -> datetime:
        pass

