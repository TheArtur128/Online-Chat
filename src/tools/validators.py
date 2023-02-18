from typing import Iterable

from marshmallow import ValidationError
from pyhandling import DelegatingProperty


class CharacterAttribute:
    characters = DelegatingProperty("__characters", settable=True, setting_converter=frozenset)

    def __init__(self, characters: Iterable[str]):
        self.characters = characters

    def __get__(self, instance: any, owner: any) -> any:
        return self.characters

    def __set__(self, instance: any, characters: Iterable[str]) -> None:
        self.characters = characters


class CharactersValidator:
    def __init__(self, extra_characters: Iterable[str] = tuple(), allowable_characters: Iterable[str] = tuple(), line_name='The line'):
        self.extra_characters = CharacterAttribute(extra_characters)
        self.allowable_characters = CharacterAttribute(allowable_characters)
        self.line_name = line_name

    def __call__(self, line: str) -> None:
        line_characters = frozenset(line)
        extra_characters = (
            (line_characters - self.allowable_characters.characters)
            if self.allowable_characters.characters else frozenset()
            | self.extra_characters.characters & line_characters
        )

        if extra_characters:
            raise ValidationError(
                "{line_name} has extra characters: {extra_characters}".format(
                    line_name=self.line_name,
                    extra_characters=', '.join(extra_characters)
                ).capitalize()
            )
