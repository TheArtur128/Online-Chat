from typing import Callable

from marshmallow import Schema, fields, post_load, ValidationError, EXCLUDE, pre_dump
from werkzeug.security import check_password_hash

from models import User
from services.utils import create_length_validator_by_model_column, ASCIIRange
from services.validators import CharactersValidator
from services.formatters import format_dict, wrap_in_brackets
from services.errors import UserNotFoundError, AuthenticationError


class BaseUserSchema(Schema):
    class Meta:
        unknown = EXCLUDE

    user_url_token = fields.String(
        required=True,
        validate=[
            create_length_validator_by_model_column(User, 'user_url_token'),
            CharactersValidator(
                line_name='User url name',
                allowable_characters=(
                    *ASCIIRange(48, 58),
                    *ASCIIRange(65, 91),
                    *ASCIIRange(97, 123),
                    '-',
                    '_'
                )
            )
        ],
        error_messages={'required': "User url name is required."}
    )

    password_hash = fields.String(
        validate=[create_length_validator_by_model_column(User, 'password_hash')]
    )

    password = fields.String(dump_only=True)

    @post_load
    def load_user(self, data: dict, **kwargs) -> User:
        if not 'user_url_token' in self.fields.keys():
            raise ValidationError("User url name is required.")

        criteria = data | dict.fromkeys(('password', ))
        del criteria['password']

        user = User.query.filter_by(**criteria).first()

        if (
            'password' in self.fields.keys()
            and 'password' in data.keys()
            and not check_password_hash(user.password_hash, data['password'])
        ):
            raise AuthenticationError("Password is incorrect.")

        return user


class FullUserSchema(BaseUserSchema):
    public_username = fields.String(
        allow_none=True,
        dump_default=None,
        validate=[create_length_validator_by_model_column(User, 'public_username')]
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
