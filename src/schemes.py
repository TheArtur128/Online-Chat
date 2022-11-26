from typing import Callable

from marshmallow import Schema, fields, post_load, ValidationError, EXCLUDE, pre_dump
from werkzeug.security import check_password_hash

from models import User
from services.utils import create_length_validator_by_model_column, ASCIIRange
from services.validators import CharactersValidator
from services.formatters import format_dict, wrap_in_brackets
from services.errors import UserNotFoundError, AuthenticationError, UserDoesntExistError


class BaseUserSchema(Schema):
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

    password_hash = fields.String(
        validate=[create_length_validator_by_model_column(User, 'password_hash')]
    )

    password = fields.String(dump_only=True)

    @post_load
    def load_user(self, data: dict, **kwargs) -> User:
        if not 'url_token' in self.fields.keys():
            raise ValidationError("Url token is required.")

        criteria = data | dict.fromkeys(('password', ))
        del criteria['password']

        user = User.query.filter_by(**criteria).first()
        
        if not user:
            raise UserDoesntExistError(
                "User with data ({user_data}) does not exist".format(
                    user_data=format_dict(
                        data,
                        line_between_key_and_value='=',
                        value_changer=lambda value: f'"{value}"'
                    )
                )
            )

        if (
            'password' in self.fields.keys()
            and 'password' in data.keys()
            and not check_password_hash(user.password_hash, data['password'])
        ):
            raise AuthenticationError("Password is incorrect.")

        return user


class FullUserSchema(BaseUserSchema):
    name = fields.String(
        validate=[create_length_validator_by_model_column(User, 'name')]
    )
    avatar_path = fields.String(
        allow_none=True,
        dump_default=None,
        validate=[create_length_validator_by_model_column(User, 'avatar_path')],
    )
    description = fields.String(
        allow_none=True,
        dump_default=None,
        validate=[create_length_validator_by_model_column(User, 'description')]
    )
