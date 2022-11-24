from unittest import TestCase

from flask import Flask

from app import app


class AppTest(TestCase):
	_app_for_test: Flask = app

	def setUp(self) -> None:
		self._test_client = self._app_for_test.test_client()