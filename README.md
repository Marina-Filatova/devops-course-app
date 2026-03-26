# Currency REST API

Минимальное REST API для получения курсов валют ЦБ РФ.

## Возможности API

- `GET /info` - информация о сервисе
- `GET /info/currency?currency=USD` - курс конкретной валюты
- `GET /info/currency?date=2026-03-20` - курсы на указанную дату
- `GET /info/currency?date=2026-03-20&currency=USD` - курсы на указанную дату и валюту

## Запуск локально

```bash
python3 main.py
```

По умолчанию приложение запускается на `http://localhost:8000`.

## Запуск в Docker

```bash
docker compose up --build
```

Приложение будет доступно на `http://localhost:8000`.

## Дополнение

В репозитории лежит выполненное дополнительное домашее задание:

- `trivy-report.json` - отчёт сканирования
- `sbom.json` - SBOM файл образа
- `docker-compose.hardened.yml` - docker-compose с параметрами безопасности
- `FINDINGS.md` - описание исправленных уязвимостей
