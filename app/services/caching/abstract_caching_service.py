import abc
from typing import Any


class AbstractCachingService(abc.ABC):
    @abc.abstractmethod
    def get(self, *args, **kwargs) -> Any:
        raise NotImplementedError

    @abc.abstractmethod
    def set(self, *args, **kwargs) -> None:
        raise NotImplementedError

    @abc.abstractmethod
    def delete(self, *args, **kwargs) -> None:
        raise NotImplementedError
