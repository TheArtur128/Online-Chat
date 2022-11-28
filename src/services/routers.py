from abc import ABC, abstractmethod


from services.middlewares import MiddlewareKeeper, DBSessionFinisherMiddleware


class IRouter(ABC):
    @abstractmethod
    def __call__(self, data: dict) -> any:
        pass


class Router(IRouter, ABC):
    def __call__(self, data: dict) -> any:
        return self._handle_cleaned_data(self._get_cleaned_data_from(data))

    @abstractmethod
    def _get_cleaned_data_from(self, data: dict) -> dict:
        pass

    @abstractmethod
    def _handle_cleaned_data(self, data: dict) -> any:
        pass


class MiddlewareRouter(Router, MiddlewareKeeper, ABC):
    def __call__(self, data: dict) -> any:
        self._proxy_middleware.call_route(super().__call__, data)
