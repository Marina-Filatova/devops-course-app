from abc import ABC, abstractmethod
from datetime import date


class RatesRepository(ABC):
    @abstractmethod
    def get_rates(self, on_date: date):
        raise NotImplementedError


class ConfigProvider(ABC):
    @abstractmethod
    def get_version(self) -> str:
        raise NotImplementedError

    @abstractmethod
    def get_author(self) -> str:
        raise NotImplementedError

    @abstractmethod
    def get_port(self) -> int:
        raise NotImplementedError
