from marshmallow import Schema, fields, post_load, ValidationError, EXCLUDE

from models import User
from services.utils import create_length_validator_by_model_column, ASCIIRange
from services.validators import CharactersValidator


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

    password = fields.String(
        required=True,
        validate=[create_length_validator_by_model_column(User, 'password_hash')],
        error_messages={'required': "Password is required."}
    )


class FullUserSchema(BaseUserSchema):
    public_username = fields.String(validate=[create_length_validator_by_model_column(User, 'public_username')])
    avatar_path = fields.String(validate=[create_length_validator_by_model_column(User, 'avatar_path')])
    description = fields.String(validate=[create_length_validator_by_model_column(User, 'description')])
