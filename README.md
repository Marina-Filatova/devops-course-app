# Currency REST API + Ansible Kubernetes Installation

Минимальное REST API для получения курсов валют ЦБ РФ и Ansible-коллекция для установки компонентов Kubernetes.

## Содержание

- [Currency REST API](#currency-rest-api)
- [Ansible: Установка Kubernetes](#ansible-установка-kubernetes)
- [Создание кластера](#этапы-создания-кластера)
- [Развёртывание приложения в Kubernetes](#развертывание-приложения)

---

# [Currency REST API](#currency-rest-api)

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

## [Ansible: Установка Kubernetes](#ansible-установка-kubernetes)
Ansible-коллекция yadro.k8s для установки CRI-O, kubeadm и kubelet на Ubuntu 24.04.

## Структура проекта

```
text
.
├── inventory/
│   └── hosts.ini                 # Инвентори виртуальных машин
├── playbooks/
│   ├── cluster-init.yml          # Плейбук развертывания кластера k8s
│   └── bootstrap.yml             # Плейбук установки пакетов k8s
├── group_vars/
│   └── all/
|       ├── main.yml              # Общие переменные (IP зеркала)
│       └── vault.yml             # Зашифрованные секреты (sudo пароль)
├── host_vars/                    # Переменные отдельных хостов
│   ├── master-node/                     
│   |   └── main.yml              # Ansible_ssh_private_key_file
|    ...
├── molecule/                     # Тесты Molecule
│   ├── full-cluster-k8s/..       # Сценарий тестирования взаимодействия ролей
│   └── full/...                  # Полный сценарий тестирования установки пакетов
├── m.filatova_ansible/           # Ansible коллекция
│   ├── galaxy.yml
│   ├── roles/
│   │   ├── k8s_master            # Роль инициализации кластера
│   │   ├── k8s_worker            # Роль подключения нод
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
[master]
master-node ansible_host=10.184.0.50 ansible_user=master

[workers]
worker-node-1 ansible_host=10.184.0.49 ansible_user=worker
worker-node-2 ansible_host=10.184.0.51 ansible_user=worker

[k8s_team:children]
master
workers
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

### Роли коллекции

| Роль | Описание | README |
|------|----------|-------|
| `crio` | Установка и настройка CRI-O container runtime, включая необходимых capabilities для ping | [README](/m.filatova_ansible/roles/crio/README.md) |
| `kubeadm` | Добавление зеркала репозитория, установка kubeadm и kubectl | [README](/m.filatova_ansible/roles/kubeadm/README.md)|
| `kubelet` | Подготовка системы (sysctl, модули ядра, swap), установка и настройка kubelet | [README](/m.filatova_ansible/roles/kubelet/README.md)|
| `k8s_master` | Инициализация control plane, настройка kubeconfig, установка Calico CNI | [README](/m.filatova_ansible/roles/k8s_master/README.md)|
| `k8s_worker` | Присоединение worker-ноды к кластеру с использованием join-команды | [README](/m.filatova_ansible/roles/k8s_worker/README.md)|

### Переменные 
## Глобальные переменные плейбука

|Переменная | Тип |	По умолчанию | Описание |
------------|-----|--------------|-----------|
|`kubernetes_version`	| string |	"1.32" |	Версия Kubernetes для установки |
|`crio_version`	| string |	"1.32"	| Версия CRI-O для установки |

## Переменные ролей
#### k8s_master
| Переменная | Тип | По умолчанию | Описание |
|------------|-----|--------------|----------|
| `k8s_pod_network_cidr` | string | `192.168.0.0/16` | CIDR подовой сети (должен совпадать с Calico) |
| `calico_manifest_url` | string | `https://...calico.yaml` | URL манифеста Calico |

#### k8s_worker
| Переменная | Тип | По умолчанию | Описание |
|------------|-----|--------------|----------|
| `cri_socket` | string | `unix:///var/run/crio/crio.sock` | Путь к Unix-сокету CRI |

#### crio
| Переменная | Тип | По умолчанию | Описание |
|------------|-----|--------------|----------|
| `crio_conmon_cgroup` | string | `pod` | Cgroup для conmon |
| `crio_cgroup_driver` | string | `systemd` | Драйвер cgroup (systemd/cgroupfs) |

### Плейбуки

#### bootstrap.yml
Базовый плейбук установки компонентов на все ноды кластера:
- Удаление конфликтующих репозиториев
- Добавление локального зеркала пакетов
- Установка и настройка kubelet, CRI-O, kubeadm, kubectl

```bash
ansible-playbook -i inventory/hosts.ini playbooks/bootstrap.yml --vault-password-file .vault_pass
```

#### cluster-init.yml
Плейбук инициализации кластера:

- kubeadm init на master-ноде
- Установка Calico CNI
- Присоединение worker-нод через kubeadm join

```bash
ansible-playbook -i inventory/hosts.ini playbooks/cluster-init.yml --vault-password-file .vault_pass
```

## Тестирование
Тесты отдельных ролей *больше не работают*

Интеграционный тест всего плейбука
```bash
cd molecule/full

molecule test -s full
```
Тесты используют Docker-образ geerlingguy/docker-ubuntu2204-ansible и проверяют:

* Установку всех компонентов
* Идемпотентность ролей
* Загрузку модулей ядра

Тест с mock-скриптами (full-cluster-k8s)
```bash
cd molecule/full-cluster-k8s

molecule test -s full-cluster-k8s
```
Проверяют логику роли; проверки stat, создание файлов, факты.

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

# [Этапы создания кластера](#этапы-создания-кластера)
### 1. Подготовка инфраструктуры

Кластер разворачивался на трёх виртуальных машинах Ubuntu 24.04:

| Нода | IP | Роль |
|------|-----|------|
| master-node | 10.184.0.50 | Control plane |
| worker-node-1 | 10.184.0.49 | Worker |
| worker-node-2 | 10.184.0.51 | Worker |

Для подключеник к master-node для проверок используйте. Пароль не менялся
```Bash
ssh master@10.184.0.50 
```

### 2. Ручная установка

Перед написанием Ansible ролей кластер был развёрнут вручную для того чтобы понять все шаги и выявисть потенциальные проблемы

#### 2.1. Подготовка нод

Необходимые шаги при ручной установке следующие:
- Отключение swap (`swapoff -a`, удаление из `/etc/fstab`)
- Загрузка модулей ядра `overlay` и `br_netfilter`
- Настройка sysctl (`net.bridge.bridge-nf-call-iptables`, `net.ipv4.ip_forward`)
- Установка `kubelet`, `kubeadm`, `kubectl` версии 1.32.13
- Установка `cri-o` в качестве container runtime

В рамках домашнего задания №5 уже были установлены `kubelet`, `kubeadm`, `kubectl` и `cri-o`, эти шаги были сделаны с помощью Ansible playbook

#### 2.2. Проблема с доставкой пакетов
Пакеты Kubernetes и CRI-O были недоступны напрямую из официальных репозиториев в среде выполнения. Решение: на control node поднято локальное зеркало с помощью `dpkg-scanpackages` и `nginx`. Пакеты скачаны через `apt-get download` и закинуты в структуру, доступную по HTTP с control node. В Ansible плейбуке используется `deb822_repository` с параметром `trusted: true`.

#### 2.3. Инициализация control plane
```bash
sudo kubeadm init --pod-network-cidr=192.168.0.0/16
```
После инициализации скопирован kubeconfig:

```bash
mkdir -p $HOME/.kube
sudo cp /etc/kubernetes/admin.conf $HOME/.kube/config
sudo chown $(id -u):$(id -g) $HOME/.kube/config
```
#### 2.4. Проблема с установкой Calico через оператор
Попытка установки Calico через tigera-operator потерпела неудачу: `CRD installations.operator.tigera.io` не создалась из-за ошибки `metadata.annotations: Too long.` Поэтому использован классический манифест calico.yaml без оператора:

```bash
kubectl apply -f https://raw.githubusercontent.com/projectcalico/calico/v3.29.3/manifests/calico.yaml
```

#### 2.5. Присоединение worker-нод
Проблема 1: конфликт CRI — на worker-нодах обнаружены оба containerd и cri-o. kubeadm отказывался присоединяться. Пришлось явно указывать `--cri-socket unix:///var/run/crio/crio.sock.`

Проблема 2: обе worker-ноды имели одинаковый hostname `worker`, из-за чего вторая нода не могла зарегистрироваться. Одна нода переименована через `hostnamectl set-hostname worker-2`.

### 3. Проблема с ping из busybox (capabilities)

При запуске ping из пода с образом busybox возникала ошибка:

```Bash
ping: permission denied (are you root?)
```

ICMP-пакеты требуют capability NET_RAW. По умолчанию CRI-O не включает её в список default_capabilities. Проверка показала, что busybox запускается с CapEff: 00000000000005fb (без NET_RAW, который добавляет бит 0000000000002000).

В конфигурацию CRI-O добавлен файл /etc/crio/crio.conf.d/02-capabilities.conf:

```Bash
[crio.runtime]
default_capabilities = [
    "CHOWN",
    "DAC_OVERRIDE",
    "FSETID",
    "FOWNER",
    "SETGID",
    "SETUID",
    "SETPCAP",
    "NET_BIND_SERVICE",
    "NET_RAW",
    "KILL",
]
```

После рестарта CRI-O контейнеры запускаются с CapEff: 00000000000025fb (включая NET_RAW), и ping работает без дополнительных флагов.

### 4. Проблема с Docker Hub rate limit

В процессе тестирования поды стали создаваться с ошибкой:
```Bash
toomanyrequests: You have reached your unauthenticated pull rate limit
```

Возможно, все виртуаные машины курса используют общий NAT и суммарное количество запросов к Docker Hub превысило лимит в предверии дедлайна. 
Для решения нужно иИспользовать `imagePullPolicy: IfNotPresent`, чтобы CRI-O использовал закешированные образы вместо повторного скачивания:

```bash
kubectl run busybox --image=busybox:latest --restart=Never --image-pull-policy=IfNotPresent --rm -i -- ping -c 4 8.8.8.8
```

На всех виртуальных машинах есть закешированный образ busybox.

# [Развёртывание приложения в Kubernetes](#развертывание-приложения)
## Что сделано
 
Приложение `currency-rest-api` развёрнуто в кластере Kubernetes (1 мастер + 2 воркера)
с использованием CRI-O и CNI-плагина Calico. Доступ снаружи организован через
nginx Ingress Controller. Настроен HTTPS с self-signed сертификатом.
 
## Структура манифестов
 
```
k8s_manifests/
├── 00-ingress-controller.yml   # DaemonSet nginx ingress
├── 01-namespace.yml            # Namespace currency-api
├── 02-deployment.yml           # Deployment (2 реплики, RollingUpdate, anti-affinity)
├── 03-service.yml              # Service ClusterIP
└── 04-ingress.yml              # Ingress (HTTP + HTTPS)
```
 
Файлы пронумерованы чтобы `kubectl apply -f k8s_manifests/` применял их
в правильном порядке.
 
## Требования
 
- Kubernetes кластер >= 1.32
- kubectl настроенный на кластер (`~/.kube/config`)
- openssl (для генерации TLS-сертификата)
## Деплой
 
### 1. Настройка kubectl
 
```bash
mkdir -p ~/.kube
scp master@10.184.0.50:~/.kube/config ~/.kube/config
```
 
### 2. Генерация TLS-сертификата и создание Secret
 
```bash
openssl req -x509 -nodes -days 365 -newkey rsa:2048 -keyout tls.key -out tls.crt -subj "/CN=currency-api.local/O=currency-api"
 
kubectl create secret tls currency-api-tls --cert=tls.crt --key=tls.key -n currency-api
 
rm tls.crt tls.key
```
 
### 3. Применение манифестов
 
```bash
kubectl apply -f k8s_manifests/
```
 
### 4. Локальный DNS 
 
```bash
echo "10.184.0.49  currency-api.local" | sudo tee -a /etc/hosts
```
 
### 5. Проверка
 
```bash
curl http://currency-api.local/info
 
curl -k https://currency-api.local/info # -k для игнорирования предупреждения из-за Self-signed сертификата
```
 
Ожидаемый ответ:
```json
{"version": "1.0.0", "service": "currency", "author": "m.filatova"}
```
 
## Особенности реализации
 
### DaemonSet + HostPort для ingress-контроллера

Кластер без внешнего балансировщика, поэтому ingress поднят на каждой ноде: DaemonSet - по одному поду на ноду, HostPort 80/443 -  принимаем трафик напрямую.
 
### 2 реплики с podAntiAffinity
 
В кластере два воркера — запущено по одной реплике на каждом.
`podAntiAffinity` нужен чтобы обе реплики не лежали на одной ноде. Если воркер упадёт — вторая реплика на другой ноде
продолжит обрабатывать запросы.
 
### Self-signed сертификат
 
Кластер за VPN и без публичного домена, поэтому получается испльзовать только это. В продакш с публичным доменом будет правильно:
cert-manager + Let's Encrypt + автоматическое обновление сертификата каждые 90 дней.
 