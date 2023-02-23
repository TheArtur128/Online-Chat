from abc import ABC
from functools import partial

from flask import request
from flask_restful import Resource
from pyhandling import to, then, call, close, post_partial
from pyhandling.annotations import decorator
from sculpting import material_of

from api.schemes import UserSchema, user_schema_without_passwords
from adapters.repositories import ConvertingRepository, SQLAlchemyRepository
from adapters.sculptures import account_sculture_from, profile_sculture_from
from infrastructure.controllers import convert_by, search_in, call_service
from rules.authorization import register_account, is_session_timed_out
from orm import db
from orm.models import User
from tools.utils import data_additing_decorator_by, dict_value_map


class DecoratedResourceMixin(Resource, ABC):
    _decorator: decorator

    def __init__(self, *args, **kwargs):
        for method_name in self.methods:
            method_name = method_name.lower()

            setattr(
                self,
                method_name,
                self._decorator(getattr(self, method_name))
            )

        super().__init__()


class UserResource(DecoratedResourceMixin):
    _decorator = data_additing_decorator_by(
        (getattr |to* (request, 'json')) |then>> call
    )

    get = (
        (convert_by |to| user_schema_without_passwords(many=True))
        |then>> (search_in |to| SQLAlchemyRepository(db, User))
        |then>> (dict_value_map |to| user_schema_without_passwords().dump)
    )

    post = (
        (convert_by |to| UserSchema(exclude=["password"], many=False))
        |then>> (call_service |to| User)
        |then>> account_sculture_from
        |then>> close(register_account, closer=post_partial)(
            ConvertingRepository(SQLAlchemyRepository(db, User), account_sculture_from, material_of),
            ConvertingRepository(SQLAlchemyRepository(db, User), profile_sculture_from, material_of),
            is_session_timed_out
        )
    )