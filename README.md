# Ansible Collection - eliminyro.system

[![Molecule CI](https://github.com/eliminyro/eliminyro.system/actions/workflows/main.yml/badge.svg)](https://github.com/eliminyro/eliminyro.system/actions/workflows/main.yml)
[![Release](https://github.com/eliminyro/eliminyro.system/actions/workflows/release.yml/badge.svg)](https://github.com/eliminyro/eliminyro.system/actions/workflows/release.yml)
[![Ansible Galaxy](https://img.shields.io/badge/galaxy-eliminyro.system-blue.svg)](https://galaxy.ansible.com/eliminyro/system)

A comprehensive Ansible collection for system administration and security
management, providing automated user management and firewall configuration
across multiple Linux distributions.

## Overview

This collection includes two main roles:

- **`users`** - Complete user and group management with SSH key configuration
- **`nftables`** - Comprehensive firewall management with IPv4/IPv6 support

## Requirements

- Ansible 2.15.0 or higher
- Python 3.x on the control node
- Target systems with systemd support
- Root/sudo privileges on target hosts

## Installation

### From Ansible Galaxy

```bash
ansible-galaxy collection install eliminyro.system
```

### From Git Repository

```bash
ansible-galaxy collection install git+https://github.com/eliminyro/eliminyro.system.git
```

### From Local Source

```bash
git clone https://github.com/eliminyro/eliminyro.system.git
cd eliminyro.system
ansible-galaxy collection build
ansible-galaxy collection install eliminyro-system-*.tar.gz
```

## Roles

### users

Manages system users and groups with comprehensive configuration options
including SSH key management, shell assignment, and user deletion capabilities.

**Key Features:**

- User creation with configurable UID, shell, and group assignments
- SSH public key management with authorized_keys configuration
- User deletion capabilities for cleanup operations
- Home directory creation with proper permissions
- Group membership management (primary and supplementary groups)
- Support for both individual users and batch operations

**Example:**

```yaml
- hosts: servers
  become: true
  roles:
    - role: eliminyro.system.users
      vars:
        users_create:
          - name: "developer"
            uid: 1001
            groups: "sudo"
            shell: "/bin/bash"
            pub_key: "ssh-ed25519 AAAAC3NzaC1lZDI1NTE5AAAAIExample..."
          - name: "service"
            uid: 1002
            groups: "users"
            shell: "/bin/sh"
        users_delete:
          - name: "olduser"
```

### nftables

Configures comprehensive firewall rules using nftables with support for both
IPv4 and IPv6, custom rule sets, and service management.

**Key Features:**

- IPv4 and IPv6 firewall table configuration
- Configurable chain policies (input, output, forward)
- Custom rule sets for input, output, and forward chains
- Service management (enable/disable, start/stop)
- Template-based configuration file generation
- Support for connection tracking and stateful filtering
- Default secure configuration with drop policies

**Example:**

```yaml
- hosts: servers
  become: true
  roles:
    - role: eliminyro.system.nftables
      vars:
        nftables_enabled: true
        nftables_state: "started"
        nftables_ipv4_policy_input: "drop"
        nftables_ipv4_input_rules:
          - 'ct state invalid drop comment "early drop of invalid connections"'
          - 'ct state established,related accept comment "allow tracked
            connections"'
          - 'iif "lo" accept comment "allow loopback"'
          - 'tcp dport 22 accept comment "allow SSH"'
          - 'tcp dport 80 accept comment "allow HTTP"'
          - 'tcp dport 443 accept comment "allow HTTPS"'
```

## Complete Workflow Example

```yaml
- name: Complete system setup
  hosts: all
  become: true
  tasks:
    # Configure firewall
    - name: Setup firewall
      include_role:
        name: eliminyro.system.nftables
      vars:
        nftables_enabled: true
        nftables_state: "started"
        nftables_ipv4_policy_input: "drop"
        nftables_ipv4_input_rules:
          - 'ct state invalid drop comment "early drop of invalid connections"'
          - 'ct state established,related accept comment "allow tracked
            connections"'
          - 'iif "lo" accept comment "allow loopback"'
          - 'tcp dport 22 accept comment "allow SSH"'
        nftables_ipv6_input_rules:
          - 'ct state invalid drop comment "early drop of invalid connections"'
          - 'ct state established,related accept comment "allow tracked
            connections"'
          - 'iif "lo" accept comment "allow loopback"'
          - 'tcp dport 22 accept comment "allow SSH"'

    # Create users
    - name: Setup users
      include_role:
        name: eliminyro.system.users
      vars:
        users_create:
          - name: "admin"
            uid: 1001
            groups: "sudo"
            shell: "/bin/bash"
            pub_key: "{{ vault_admin_ssh_key }}"
          - name: "deployer"
            uid: 1002
            groups: "users"
            shell: "/bin/bash"
            pub_key: "{{ vault_deployer_ssh_key }}"
```

## Security Considerations

This collection implements several security best practices:

- **Firewall Security**: Default deny policies with explicit allow rules
- **User Security**: Configurable UID assignments and group memberships
- **SSH Security**: Public key authentication support with proper file
  permissions
- **File Permissions**: All configuration files use appropriate restrictive
  permissions
- **Service Management**: Proper systemd service integration with security
  controls

## Testing

This collection includes comprehensive testing using Molecule with testinfra
verification:

```bash
# Test users role
molecule test -s users

# Test nftables role
molecule test -s nftables

```

The test suite includes:

- User creation and deletion verification
- SSH key configuration testing
- Firewall rule validation and connectivity testing
- Service management testing

## Documentation

Detailed documentation for each role is available in their respective README
files:

- [Users Role Documentation](roles/users/README.md)
- [Nftables Role Documentation](roles/nftables/README.md)

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests for new functionality
5. Run the test suite
6. Submit a pull request

## License

GPL-3.0-or-later

## Author

[Pavel Eliminyro](https://bc.eliminyro.me)

## Support

- **Issues**:
  [GitHub Issues](https://github.com/eliminyro/eliminyro.system/issues)
- **Repository**:
  [GitHub Repository](https://github.com/eliminyro/eliminyro.system)
