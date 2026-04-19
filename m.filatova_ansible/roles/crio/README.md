# crio

Устанавливает и настраивает CRI-O версии `>= 1.32` на Ubuntu 22.04 для Kubernetes-узлов.

## Требования

- Ubuntu >= 22.04
- Ansible >= 2.14

## Зависимости

Роль использует только модули `ansible.builtin`.

## Переменные

| Variable | Type | Default | Description |
|----------|------|---------|-------------|
| `crio_version` | `str` | `"1.32"` | Ветка репозитория CRI-O |
| `crio_cgroup_driver` | `str` | `"systemd"` | Cgroup driver для CRI-O |
| `crio_conmon_cgroup` | `str` | `"pod"` | Значение `conmon_cgroup` в конфигурации CRI-O |

## Example Playbook

```yaml
- name: Install CRI-O
  hosts: all
  become: true
  roles:
    - role: yadro.k8s.crio
```
