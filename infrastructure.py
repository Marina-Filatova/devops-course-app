import os
from datetime import date
from urllib.request import Request, urlopen
import xml.etree.ElementTree as ET

from ports import ConfigProvider, RatesRepository


class EnvConfigProvider(ConfigProvider):
    def get_version(self) -> str:
        return os.environ.get("VERSION") or "1.0.0"

    def get_author(self) -> str:
        return os.environ.get("AUTHOR") or "m.filatova"

    def get_port(self) -> int:
        raw = os.environ.get("PORT") or "8000"
        try:
            return int(raw)
        except ValueError:
            return 8000


class CbrRatesRepository(RatesRepository):
    
    def _fetch_cbr_xml(self, on_date: date) -> bytes:
        date_param = on_date.strftime("%d/%m/%Y")
        url = f"https://www.cbr.ru/scripts/XML_daily.asp?date_req={date_param}"
        req = Request(url, headers={"User-Agent": "CurrencyAPI/1.0"})
        with urlopen(req, timeout=10) as resp:
            return resp.read()

    def _parse_rates(self, xml_bytes: bytes):
        root = ET.fromstring(xml_bytes)
        rates = {}
        for valute in root.findall("Valute"):
            char_code = valute.findtext("CharCode")
            value_text = valute.findtext("Value")
            if not char_code or not value_text:
                continue
            try:
                def _to_float(s):
                    return float(s.replace("\u00a0", "").replace(" ", "").replace(",", "."))

                value = _to_float(value_text)
            except ValueError:
                continue
            rates[char_code] = value
        return rates
    
    def get_rates(self, on_date: date):
        xml_data = self._fetch_cbr_xml(on_date)
        return self._parse_rates(xml_data)
