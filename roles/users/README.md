# Ansible Role: users

This role is part of the `eliminyro.system` collection and automates comprehensive user management on Linux systems. It handles user creation, deletion, group management, SSH key configuration, and home directory setup with flexible permission settings.

## Requirements

- Ansible 2.15+ and Python 3.x on the control node.
- Target system with systemd support.
- Root/sudo privileges on target hosts.

## Overview

The role performs the following user management operations:

1. **Create users** – Creates system users with configurable properties
2. **Configure SSH keys** – Sets up SSH public key authentication
3. **Manage groups** – Assigns users to primary and supplementary groups
4. **Set permissions** – Configures home directory and SSH file permissions
5. **Delete users** – Removes specified users and their home directories

## Role Variables

### User Creation Variables

| Variable       | Default | Description                                |
| -------------- | ------- | ------------------------------------------ |
| `users_create` | `[]`    | List of users to create with their config |

Each user in `users_create` supports the following parameters:

| Parameter | Default    | Description                              |
| --------- | ---------- | ---------------------------------------- |
| `name`    | _required_ | Username                                 |
| `uid`     | _optional_ | User ID number                           |
| `groups`  | _optional_ | Primary/supplementary groups (string or list) |
| `shell`   | _optional_ | User's login shell                       |
| `pub_key` | _optional_ | SSH public key for authorized_keys       |

### User Deletion Variables

| Variable      | Default | Description                   |
| ------------- | ------- | ----------------------------- |
| `users_delete` | `[]`   | List of users to delete       |

Each user in `users_delete` supports:

| Parameter | Default    | Description |
| --------- | ---------- | ----------- |
| `name`    | _required_ | Username    |

## Dependencies

None.

## Example Playbook

### Basic User Creation

```yaml
---
- hosts: servers
  become: true
  vars:
    users_create:
      - name: "developer"
        uid: 1001
        groups: "sudo"
        shell: "/bin/bash"
        pub_key: "ssh-ed25519 AAAAC3NzaC1lZDI1NTE5AAAAIExample... dev@example.com"
      
      - name: "service"
        uid: 1002
        groups: "users"
        shell: "/bin/sh"
      
      - name: "admin"
        uid: 1003
        groups: ["sudo", "docker"]
        shell: "/bin/bash"
        pub_key: "ssh-rsa AAAAB3NzaC1yc2EAAAADAQABAAABgQC... admin@example.com"

  roles:
    - eliminyro.system.users
```

### User Management with Deletion

```yaml
---
- hosts: servers
  become: true
  vars:
    users_create:
      - name: "newuser"
        uid: 1001
        groups: "users"
        shell: "/bin/bash"
        pub_key: "{{ vault_newuser_ssh_key }}"
    
    users_delete:
      - name: "olduser"
      - name: "tempuser"

  roles:
    - eliminyro.system.users
```

### Advanced Configuration

```yaml
---
- hosts: all
  become: true
  vars:
    users_create:
      # System administrator
      - name: "sysadmin"
        uid: 1000
        groups: ["sudo", "adm", "systemd-journal"]
        shell: "/bin/bash"
        pub_key: "{{ vault_sysadmin_ssh_key }}"
      
      # Application service user
      - name: "appuser"
        uid: 2000
        groups: "users"
        shell: "/bin/sh"
      
      # Developer with multiple groups
      - name: "developer"
        uid: 1001
        groups: ["sudo", "docker", "users"]
        shell: "/bin/zsh"
        pub_key: "{{ vault_developer_ssh_key }}"
      
      # Read-only monitoring user
      - name: "monitor"
        uid: 3000
        groups: "users"
        shell: "/bin/bash"
        pub_key: "{{ vault_monitor_ssh_key }}"

  roles:
    - eliminyro.system.users
```

## User Configuration Details

### SSH Key Management

When `pub_key` is specified:
- Creates `.ssh` directory in user's home with `0700` permissions
- Creates `authorized_keys` file with `0600` permissions
- Sets proper ownership for all SSH-related files
- Supports multiple key formats (RSA, Ed25519, ECDSA)

### Group Management

The `groups` parameter supports:
- **String format**: `groups: "sudo"` (single group)
- **List format**: `groups: ["sudo", "docker"]` (multiple groups)
- Groups must exist on the system before user creation
- Users are added to specified groups as supplementary groups

### Home Directory

- Created automatically with appropriate permissions
- Default location: `/home/username`
- Owner and group set to the user
- Permissions set to `0755` (readable by others, writable by owner)

## Security Considerations

- **SSH Security**: SSH keys are properly secured with restrictive permissions
- **File Permissions**: Home directories and SSH files use secure permissions
- **User Isolation**: Each user gets their own home directory and proper ownership
- **Group Management**: Users are assigned to appropriate groups for access control
- **Shell Security**: Login shells are validated against system configuration

## Integration with Other Roles

This role works well with other system management roles:

```yaml
- hosts: servers
  become: true
  tasks:
    # Install packages first
    - include_role:
        name: eliminyro.system.packages
      vars:
        packages: ["sudo", "openssh-server"]
    
    # Create users
    - include_role:
        name: eliminyro.system.users
      vars:
        users_create:
          - name: "admin"
            groups: "sudo"
            pub_key: "{{ vault_admin_ssh_key }}"
    
    # Configure firewall
    - include_role:
        name: eliminyro.system.nftables
      vars:
        nftables_ipv4_input_rules:
          - "tcp dport 22 accept comment \"allow SSH\""
```

## Testing

This role includes comprehensive molecule testing that verifies:
- User creation with all specified properties
- SSH key configuration and permissions
- Group membership assignment
- Home directory creation and permissions
- User deletion functionality
- Shell validation

Run tests with:
```bash
molecule test -s users
```