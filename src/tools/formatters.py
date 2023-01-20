from typing import Callable, Iterable

from tools.errors import DocumentaryError


def convert_documentary_error_to_dict(
    error: DocumentaryError,
    *,
    is_convert_error_type_name: bool = True,
    is_convert_error_message: bool = True,
    is_convert_error_detail: bool = True
) -> dict:
    result_dict = (
        {'error-type': type(error).__name__}
        if is_convert_error_type_name
        else dict()
    )

    if error.message and is_convert_error_message:
        result_dict['message'] = error.message

    if error.document and is_convert_error_detail:
        result_dict['detail'] = error.document

    return result_dict


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