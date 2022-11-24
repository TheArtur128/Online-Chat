from unittest import main
from json import dumps

from tests import AppTest


class ApiTest(AppTest):
	_default_headers: dict = {'Content-Type': 'application/json'}

	_user_endpoint: str = 'api/users'

	def test_user_endpoint(self) -> None:
		self.assertEqual(
			self._test_client.get(
				self._user_endpoint,
				data=dumps([{'user_url_token': 'oleg123'}]),
				headers=self._default_headers
			).json,
			[{
				'user_url_token': 'oleg123',
				'public_username': 'Oleg',
				'description': "I am Oleg",
				'avatar_path': None
			}]
		)

if __name__ == '__main__':
	main()