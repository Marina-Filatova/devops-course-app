# yadro.k8s

Ansible collection для домашнего задания по установке Kubernetes-компонентов на Ubuntu 22.04.

## Included Roles

- `yadro.k8s.kubeadm` - установка `kubeadm` и `kubectl`
- `yadro.k8s.kubelet` - подготовка узла и установка `kubelet`
- `yadro.k8s.crio` - установка и настройка CRI-O

## External Dependencies

- `community.general`
- `ansible.posix`

## Usage

```yaml
- name: Bootstrap Kubernetes nodes
  hosts: k8s_team
  become: true
  roles:
    - role: yadro.k8s.kubeadm
    - role: yadro.k8s.crio
    - role: yadro.k8s.kubelet
```

## Testing

Для ролей и полного сценария используются Molecule-сценарии.

- `extensions/molecule/kubeadm`
- `extensions/molecule/kubelet`
- `extensions/molecule/crio`
- `../molecule/full`
