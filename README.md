# Currency REST API + Ansible Kubernetes Installation

Минимальное REST API для получения курсов валют ЦБ РФ и Ansible-коллекция для установки компонентов Kubernetes.

## Содержание

- [Currency REST API](#currency-rest-api)
- [Ansible: Установка Kubernetes](#ansible-установка-kubernetes)

---

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

## Ansible: Установка Kubernetes
Ansible-коллекция yadro.k8s для установки CRI-O, kubeadm и kubelet на Ubuntu 24.04.

## Структура проекта

```
text
.
├── inventory/
│   └── hosts.ini                 # Инвентори виртуальных машин
├── playbooks/
│   └── bootstrap.yml             # Основной плейбук установки
├── group_vars/
│   └── all/
│       └── vault.yml             # Зашифрованные секреты (sudo пароль)
├── host_vars/                    # Переменные отдельных хостов
│   ├── master-node/                     
│   |   └── main.yml              # Username и ansible_ssh_private_key_file
|    ...
├── molecule/                     # Интеграционные тесты Molecule
│   └── full/...                  # Полный сценарий тестирования
├── m.filatova_ansible/           # Ansible коллекция
│   ├── galaxy.yml
│   ├── roles/
│   │   ├── crio/                 # Роль установки CRI-O
│   │   ├── kubeadm/              # Роль установки kubeadm + kubectl
│   │   └── kubelet/              # Роль подготовки системы + kubelet
│   └── extensions/
│       └── molecule/             # Тесты отдельных ролей
├── requirements.yml              # Зависимости коллекций
├── ansible.cfg                   # Конфигурация Ansible
└── .vault_pass                   # Пароль для Vault (в .gitignore)
```

## Требования
Установленные коллекции:

* community.general
* ansible.posix

Установка зависимостей:

```bash
ansible-galaxy collection install -r requirements.yml
```
## Быстрый старт
Настройка инвентори — отредактируйте inventory/hosts.ini:

```ini
[k8s_team]
master-node ansible_host=10.184.0.50
worker-node-1 ansible_host=10.184.0.49
worker-node-2 ansible_host=10.184.0.51
```
Настройка Vault (опционально):

```bash
# Создайте файл с паролем Vault
echo -n "your_vault_password" > .vault_pass

# Создайте зашифрованный файл с sudo-паролями
ansible-vault create --vault-password-file .vault_pass group_vars/all/vault.yml
```
Содержимое group_vars/all/vault.yml:

```yaml
---
ansible_become_password: your_sudo_password
```
## Запуск плейбука:

```bash
ansible-playbook -i inventory/hosts.ini playbooks/bootstrap.yml --vault-password-file .vault_pass
```
## Переменные
### Глобальные переменные плейбука

|Переменная | Тип |	По умолчанию | Описание |
------------|-----|--------------|-----------|
|`kubernetes_version`	| string |	"1.32" |	Версия Kubernetes для установки |
|`crio_version`	| string |	"1.32"	| Версия CRI-O для установки |

### Переменные ролей
Подробное описание переменных каждой роли находится в соответствующих README:

* Роль CRI-O
* Роль Kubeadm
* Роль Kubelet

## Тестирование
Тесты отдельных ролей
```bash
cd m.filatova_ansible

molecule test -s crio
molecule test -s kubeadm
molecule test -s kubelet
```
Интеграционный тест всего плейбука
```bash
cd molecule/full

molecule test -s full
```
Тесты используют Docker-образ geerlingguy/docker-ubuntu2204-ansible и проверяют:

* Установку всех компонентов
* Идемпотентность ролей
* Загрузку модулей ядра

## Безопасность (Ansible Vault)
Для безопасного хранения sudo-паролей используется Ansible Vault:

* `group_vars/all/vault.yml` — зашифрованный файл с ansible_become_password
* `.vault_pass` — пароль для расшифровки (добавлен в .gitignore)

При запуске плейбука необходимо указывать `--vault-password-file .vault_pass`.

## Роли

|Роль |	Описание	|README|
|-----|------------|-------|
|crio |	Установка CRI-O container runtime (>= 1.32)	|[README](/m.filatova_ansible/roles/crio/README.md)|
|kubeadm|	Добавление репозитория Kubernetes, установка kubeadm и kubectl|	[README](/m.filatova_ansible/roles/kubeadm/README.md)|
|kubelet|	Подготовка системы, установка и настройка kubelet|	[README](/m.filatova_ansible/roles/kubelet/README.md)|

# ⚠️ Важное примечание по установке в production-окружении

**Тесты Molecule проходят успешно**, как для отдельных ролей, так и глобальные, если использовать `VPN`, но при попытке использовать плейбук для наших ВМ возникает проблема на шаге `TASK [kubeadm : Install kubeadm and kubectl]`. Пакеты не скачиваются и task уходит в timeout