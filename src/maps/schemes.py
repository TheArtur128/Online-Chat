from marshmallow import Schema, fields, EXCLUDE, post_dump

from orm.models import User
from tools.utils import length_validator_by_column, ascii_range_as
from tools.validators import CharactersValidator


class UserSchema(Schema):
    class Meta:
        unknown = EXCLUDE

    url_token = fields.String(
        required=True,
        validate=[
            length_validator_by_column("url_token", User),
            CharactersValidator(
                line_name="Url token",
                allowable_characters=(
                    *ascii_range_as(range(48, 58)),
                    *ascii_range_as(range(65, 91)),
                    *ascii_range_as(range(97, 123)),
                    '-',
                    '_'
                )
            )
        ],
        error_messages={"required": "Url token is required."}
    )

    password_hash = fields.String(
        required=True,
        validate=[length_validator_by_column("password_hash", User)],
        error_messages={"required": "Password hash is required."}
    )

    password = fields.String(
        required=True,
        dump_only=True,
        error_messages={"required": "Password is required."}
    )