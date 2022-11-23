from typing import Optional, Callable

from flask_restful import Resource
from flask import request, Response
from marshmallow import Schema

from shemes import BaseUserSchema


class UserResource(Resource):
	_default_user_schema: Schema = BaseUserSchema(only=('user_url_token'))

	def __init__(self, user_schema: Optional[Schema] = None):
		self._user_schema = user_schema if user_schema else self._default_user_schema
		self._user_schema.many = True

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