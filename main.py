import json
from datetime import date, datetime
from http.server import BaseHTTPRequestHandler, HTTPServer
from urllib.parse import parse_qs, urlparse

from infrastructure import CbrRatesRepository, EnvConfigProvider
from services import AppInfoService, CurrencyQuery, CurrencyRatesService

# Парсим YYYY-MM-DD в date
def parse_date_param(value: str):
    try:
        return datetime.strptime(value, "%Y-%m-%d").date()
    except ValueError:
        return None

class Handler(BaseHTTPRequestHandler):
    server_version = "CurrencyAPI/1.0"

    def __init__(self, *args, **kwargs):
        # Зависимости обработчика
        self._config = EnvConfigProvider()
        self._rates_repo = CbrRatesRepository()
        self._info_uc = AppInfoService(self._config)
        self._rates_uc = CurrencyRatesService(self._rates_repo)
        super().__init__(*args, **kwargs)

    def _send_json(self, payload, status=200):
        body = json.dumps(payload, ensure_ascii=False).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def _send_error(self, message, status=400):
        self._send_json({"error": message}, status=status)

    def do_GET(self):
        parsed = urlparse(self.path)
        path = parsed.path.strip().rstrip("/")
        raw_query = parse_qs(parsed.query)
        query = {k.lower(): v for k, v in raw_query.items()}

        if path == "" or path == "/":
            self._send_error("Not found", status=404)
            return

        if path == "/info":
            info = self._info_uc.get_info(service="currency")
            payload = {
                "version": info.version,
                "service": info.service,
                "author": info.author,
                "status": "ok",
                "deploy": "argocd",
            }
            self._send_json(payload)
            return

        if path == "/info/currency":
            currency_list = query.get("currency")

            currency = (
                currency_list[0].strip().upper() if currency_list and currency_list[0] else None
            )

            # Парсим дату или берем сегодняшнюю
            date_list = query.get("date")
            if date_list:
                parsed_date = parse_date_param(date_list[0].strip())
                if parsed_date is None:
                    self._send_error("Invalid date format. Use YYYY-MM-DD.", status=400)
                    return
            else:
                parsed_date = date.today()

            # Запрашиваем курсы у ЦБ
            try:
                query_obj = CurrencyQuery(on_date=parsed_date, currency=currency)
                rates = self._rates_uc.get_rates(query_obj)
            except Exception as exc:
                print(f"Fetch error: {exc}")
                self._send_error("Failed to fetch currency data", status=502)
                return

            # Фильтруем по валюте, если задана
            if currency:
                if currency not in rates.rates:
                    self._send_error("Currency not found", status=404)
                    return
                data = rates.filtered(currency)
            else:
                data = rates.filtered(None)
            
            payload = {"service": "currency", "data": data}
            self._send_json(payload)
            return
        
        self._send_error("Not found", status=404)


def main():
    config = EnvConfigProvider()
    port = config.get_port()
    server = HTTPServer(("0.0.0.0", port), Handler)
    print(f"Listening on 0.0.0.0:{port}")
    server.serve_forever()


if __name__ == "__main__":
    main()
