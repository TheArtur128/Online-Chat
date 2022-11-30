from typing import Callable, Iterable


def format_dict(
        data: dict,
        *,
        line_between_elements: str = ', ',
        line_between_key_and_value: str = ': ',
        key_changer: Callable[[str], any] = lambda key: key,
        value_changer: Callable[[any], any] = lambda value: value,
    ) -> str:
    return line_between_elements.join(
        "{key_part}{line_between_key_and_value_part}{value_part}".format(
            key_part=str(key_changer(key)),
            value_part=str(value_changer(value)),
            line_between_key_and_value_part=line_between_key_and_value
        )
        for key, value in data.items()
    )


def wrap_in_brackets(data: any, bracket: str, times: int = 1) -> str:
    for _ in range(times):
        data = (
            (bracket[0] if len(bracket) > 1 else bracket)
            + str(data)
            + (bracket[1] if len(bracket) > 1 else bracket)
        )

    return data