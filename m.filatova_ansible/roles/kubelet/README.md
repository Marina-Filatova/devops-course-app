# kubelet

Подготавливает узел для Kubernetes и устанавливает `kubelet` на Ubuntu 22.04.

## Требования

- Ubuntu 22.04
- Ansible >= 2.14
- Kubernetes-репозиторий уже добавлен на хост

## Зависимости

- `community.general`
- `ansible.posix`

Зависимости для сторонних модулей описаны в [requirements.yml](requirements.yml).

## Переменные

| Variable | Type | Default | Description |
|----------|------|---------|-------------|
| `kubernetes_version` | `str` | `"1.32"` | Ожидаемая ветка Kubernetes-репозитория |
| `kubelet_cgroup_driver` | `str` | `"systemd"` | Cgroup driver для kubelet |

## Example Playbook

```yaml
- name: Install kubelet
  hosts: all
  become: true
  roles:
    - role: yadro.k8s.kubeadm
    - role: yadro.k8s.kubelet
```
