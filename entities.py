from dataclasses import dataclass
from typing import Optional


@dataclass(frozen=True)
class AppInfo:
    version: str
    service: str
    author: str


@dataclass(frozen=True)
class CurrencyRates:
    rates: dict

    def filtered(self, currency: Optional[str]) -> dict:
        if currency is None:
            return dict(self.rates)
        return {currency: self.rates[currency]}
