# k8s_master

Инициализирует Kubernetes control-plane с помощью `kubeadm init` и устанавливает Calico CNI на Ubuntu 22.04.

## Требования

- Ubuntu >= 22.04
- Ansible >= 2.14
- Установлены `kubeadm`, `kubectl`, `crio` (роли `kubeadm`, `crio`)

## Зависимости

Используется только `ansible.builtin`.

## Переменные

| Variable | Type | Default | Description |
|----------|------|---------|-------------|
| `k8s_pod_network_cidr` | `str` | `"192.168.0.0/16"` | Pod network CIDR для `kubeadm init`. Должен совпадать с настройками CNI |
| `calico_manifest_url` | `str` | `"https://raw.githubusercontent.com/projectcalico/calico/v3.29.3/manifests/calico.yaml"` | URL манифеста Calico |

## Выходные факты

| Fact | Description |
|------|-------------|
| `kubeadm_join_command` | Полная команда `kubeadm join` для подключения воркеров |

## Example Playbook

```yaml
- name: Initialize master node
  hosts: master
  become: true
  roles:
    - role: k8s_master

- name: Join workers
  hosts: workers
  become: true
  vars:
    kubeadm_join_command: "{{ hostvars[groups['master'][0]]['kubeadm_join_command'] }}"
  roles:
    - role: k8s_worker
```