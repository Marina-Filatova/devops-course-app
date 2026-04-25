# kubeadm

Устанавливает `kubeadm` и `kubectl` из официального Kubernetes-репозитория версии `>= 1.32` на Ubuntu 22.04.

## Требования

- Ubuntu >= 22.04
- Ansible >= 2.14

## Зависимости

Роль использует только модули `ansible.builtin`.

## Переменные

| Variable | Type | Default | Description |
|----------|------|---------|-------------|
| `kubernetes_version` | `str` | `"1.32"` | Ветка официального Kubernetes-репозитория |

## Example Playbook

```yaml
- name: Install kubeadm and kubectl
  hosts: all
  become: true
  roles:
    - role: yadro.k8s.kubeadm
```
