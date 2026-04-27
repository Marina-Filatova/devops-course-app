# k8s_worker

Подключает worker-ноду к существующему Kubernetes кластеру с помощью `kubeadm join` на Ubuntu 22.04.

## Требования

- Ubuntu >= 22.04
- Ansible >= 2.14
- Установлены `kubeadm`, `kubelet`, `crio` (роли `kubeadm`, `kubelet`, `crio`)
- Кластер уже инициализирован ролью `k8s_master`

## Зависимости

Используется только `ansible.builtin`.

## Переменные

| Variable | Type | Default | Description |
|----------|------|---------|-------------|
| `kubeadm_join_command` | `str` | — | Полная команда `kubeadm join`. Передаётся через `hostvars` с мастер-ноды (**обязательно**) |

## Идемпотентность

Роль проверяет наличие `/etc/kubernetes/kubelet.conf` перед запуском `kubeadm join`. Повторный запуск безопасен.

## Example Playbook

```yaml
- name: Join worker nodes
  hosts: workers
  become: true
  vars:
    kubeadm_join_command: "{{ hostvars[groups['master'][0]]['kubeadm_join_command'] }}"
  roles:
    - role: k8s_worker
```