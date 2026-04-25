# Домашнее задание №4: Advanced CI/CD (Jenkins) Отчет

**Выполнила:** Филатова Марина (m.filatova)  
**Дата:** 11.04.2026

---

## 1. Инфраструктура

| Компонент | IP | Роль | Лейбл |
|-----------|-----|------|-------|
| Jenkins Master | 10.184.0.50 | CI Server | built-in |
| Worker-1 | 10.184.0.49 | Staging Agent | staging |
| Worker-2 | 10.184.0.51 | Production Agent | production |

Агенты подключены через SSH. На каждом воркере установлен Docker, пользователь `worker` добавлен в группу `docker` для работы без `sudo`.

---

## 2. Jenkins Jobs

- Multibranch Pipeline: `app-main-ci`

- Параметризованный Pipeline: `app-main-deploy`
    - **Параметры:**
    - `IMAGE_TAG` (String) — тег Docker образа, по умолчанию `latest`
    - `ENVIRONMENT` (Choice) — `staging` или `production`
    - **Script Path:** `Jenkinsfile_deploy`

---

## 3. Shared Library

**Репозиторий:** `https://education-git.yadro.com/education/devops/2026/m.filatova/m_filatova_jenkins_shared_library`

**Структура:**
```
vars/
└── runSmokeTest.groovy       # smoke-тестирование эндпоинтов
```
---

## 4. Основной пайплайн (Jenkinsfile)

### 4.1 Определение типа триггера

```groovy
def isMR()    { return env.CHANGE_ID != null }
def isMain()  { return env.BRANCH_NAME == 'main' || env.BRANCH_NAME == 'master' }
def isTag()   { return env.TAG_NAME != null }
```

### 4.2 Стадии пайплайна

| Стадия | Условие выполнения | 
|--------|-------------------|
| **Checkout** | Всегда | 
| **Lint & SAST** | Всегда | 
| **Build** | MR \|\| main \|\| tag |
| **Deploy to Staging** | main, вызов `app-main-deploy` с `ENVIRONMENT=staging` |
| **Deploy to Production** | tag, вызов `app-main-deploy` с `ENVIRONMENT=production` |

---

## 5. Результаты тестирования

### 5.1 Feature-ветка
При пуше в feature-ветку выполняются стадии Checkout и Lint & SAST. Артефакты с отчётами сохраняются. Стадии Build и Deploy пропускаются.

### 5.2 Merge Request
При создании MR добавляется стадия Build (сборка образа без пуша в Docker Hub). Deploy стадии пропускаются.

### 5.3 Main → Staging
После мержа в main выполняется полный цикл: сборка, пуш в Docker Hub, деплой на staging-окружение (worker-1) и smoke-тесты. Приложение успешно разворачивается и отвечает на запросы.

### 5.4 Tag → Production
При создании тега формата `v*` выполняется сборка, пуш в Docker Hub с тегом из Git, деплой на production-окружение (worker-2) и smoke-тесты. Стадия staging деплоя пропускается.

### 5.5 Ручной деплой
Job `app-main-deploy` можно запустить вручную через **Build with Parameters**, указав `IMAGE_TAG` и `ENVIRONMENT`.

---

## 6. Артефакты

После каждого билда сохраняются:
- `lint_report.txt` — результат проверки Dockerfile утилитой Hadolint
- `sast_report.txt` — результат статического анализа кода утилитой Bandit

---

## 7. Docker Hub

Собранные образы публикуются в Docker Hub:
- **Репозиторий:** `https://hub.docker.com/r/mfilatova/currency-rest-api`

---

## 8. Выводы

- Настроены два отдельных агента для staging и production окружений
- Реализован Multibranch Pipeline с различным поведением в зависимости от триггера
- Настроен параметризованный деплой с возможностью ручного запуска
- Часть логики вынесена в Shared Library
- Настроены автоматические триггеры
- Отчёты Lint и SAST сохраняются как артефакты
