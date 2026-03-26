from dataclasses import dataclass
from datetime import date
from typing import Optional

from entities import AppInfo, CurrencyRates
from ports import ConfigProvider, RatesRepository


@dataclass(frozen=True)
class CurrencyQuery:
    on_date: date
    currency: Optional[str]


class AppInfoService:
    def __init__(self, config: ConfigProvider):
        self._config = config

    def get_info(self, service: str) -> AppInfo:
        return AppInfo(
            version=self._config.get_version(),
            service=service,
            author=self._config.get_author(),
        )


class CurrencyRatesService:
    def __init__(self, repository: RatesRepository):
        self._repository = repository

    def get_rates(self, query: CurrencyQuery) -> CurrencyRates:
        rates = self._repository.get_rates(query.on_date)
        return CurrencyRates(rates=rates)
