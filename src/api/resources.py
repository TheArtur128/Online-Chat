from typing import Optional, Callable

from flask_restful import Resource
from flask import request, Response
from marshmallow import Schema

from schemes import BaseUserSchema, FullUserSchema


class UserResource(Resource):
	_user_serialization_schema: Schema = BaseUserSchema(only=('user_url_token', ))
	_user_deserialization_schema: Schema = FullUserSchema(exclude=('password', ))

	def get(self):
		try: 
			return self._user_schema.dump(
				user.__dict__ for user in self._user_schema.load(request.json)
			)
		except StatusCodeError as error:
			return (
				(error.messages if isinstance(error, ValidationError) else dict()),
				error.status_code
			)
		except ValidationError as error:
			return error.messages, 400