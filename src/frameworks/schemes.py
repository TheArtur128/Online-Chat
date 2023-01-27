from marshmallow import Schema, fields, EXCLUDE, post_dump

from orm.models import User
from tools.utils import create_length_validator_by_model_column, ASCIIRange
from tools.validators import CharactersValidator


class UserSchema(Schema):
    class Meta:
        unknown = EXCLUDE

    url_token = fields.String(
        required=True,
        validate=[
            create_length_validator_by_model_column(User, 'url_token'),
            CharactersValidator(
                line_name='Url token',
                allowable_characters=(
                    *ASCIIRange(48, 58),
                    *ASCIIRange(65, 91),
                    *ASCIIRange(97, 123),
                    '-',
                    '_'
                )
            )
        ],
        error_messages={'required': "Url token is required."}
    )

    name = fields.String(validate=[create_length_validator_by_model_column(User, 'name')])

    password_hash = fields.String(
        required=True,
        validate=[create_length_validator_by_model_column(User, 'password_hash')],
        error_messages={'required': "Password hash is required."}
    )

    password = fields.String(
        required=True,
        dump_only=True,
        error_messages={'required': "Password is required."}
    )

    avatar_path = fields.String(
        allow_none=True,
        validate=[create_length_validator_by_model_column(User, 'avatar_path')],
    )
    
    description = fields.String(
        allow_none=True,
        validate=[create_length_validator_by_model_column(User, 'description')]
    )

    @post_dump
    def previous_dump(self, data: object, **kwargs):
        if 'name' not in data.keys() and 'url_token' in data.keys():
            data['name'] = data['url_token']

        return data


user_schema_without_password = partial(UserSchema, exclude=('password', 'password_hash'))
