# Testing

This collection uses [Molecule](https://molecule.readthedocs.io/) with
[Testinfra](https://testinfra.readthedocs.io/) for comprehensive testing of both
roles.

## Prerequisites

```bash
pip install molecule[default] molecule-plugins testinfra pytest
pip install ansible-core>=2.15
```

## Test Scenarios

### Users Role Testing

Tests user management, SSH key configuration, and group assignment:

```bash
molecule test -s users
```

**Test Coverage:**

- User creation with configurable properties (UID, shell, groups)
- SSH public key deployment and authorized_keys configuration
- Home directory creation with proper permissions
- Group membership assignment and validation
- User deletion functionality
- Shell validation and security checks

### Nftables Role Testing

Tests firewall configuration, rule application, and service management:

```bash
molecule test -s nftables
```

**Test Coverage:**

- Nftables package installation and service management
- Configuration file generation and syntax validation
- IPv4 and IPv6 rule application and policy enforcement
- Active ruleset verification and rule matching
- Service state management (enable/disable, start/stop)
- Basic connectivity testing through firewall rules

## Running Individual Test Phases

```bash
# Create test environment
molecule create -s <scenario>

# Run converge (apply the role)
molecule converge -s <scenario>

# Run tests only
molecule verify -s <scenario>

# Clean up
molecule destroy -s <scenario>
```

## Test Structure

```
molecule/
├── users/
│   ├── molecule.yml          # Molecule configuration
│   ├── converge.yml          # Apply users role
│   ├── prepare.yml           # Pre-test setup (create groups, test users)
│   ├── cleanup.yml           # Test cleanup (remove created users)
│   ├── group_vars/           # Test variables
│   │   └── all/main.yml
│   └── tests/                # Testinfra test files
│       ├── conftest.py       # Test fixtures
│       └── test_users.py     # Users role tests
└── nftables/
    ├── molecule.yml          # Molecule configuration
    ├── converge.yml          # Apply nftables role
    ├── cleanup.yml           # Test cleanup (remove firewall config)
    ├── group_vars/           # Test variables
    │   └── all/main.yml
    └── tests/                # Testinfra test files
        ├── conftest.py       # Test fixtures
        └── test_nftables.py  # Nftables role tests
```

## Test Configuration

### Users Scenario

- **Driver**: Default (local execution)
- **Provisioner**: Ansible
- **Verifier**: Testinfra
- **Test Environment**: Local system with user management testing
- **Prepare Stage**: Creates required groups and test users for deletion testing
- **Cleanup Stage**: Removes all created users and home directories

### Nftables Scenario

- **Driver**: Default (local execution)
- **Provisioner**: Ansible
- **Verifier**: Testinfra
- **Test Environment**: Local system with privileged access for firewall testing
- **Cleanup Stage**: Flushes rules, stops service, removes config and package

## Test Organization

Tests are organized using class-based structure for better organization:

### Users Role Test Classes

- **TestUsersCreation**: User creation, properties, and configuration testing
- **TestUsersDeletion**: User deletion and cleanup verification

### Nftables Role Test Classes

- **TestNftablesInstallation**: Package installation verification
- **TestNftablesService**: Service management and state testing
- **TestNftablesConfiguration**: Configuration file generation and validation
- **TestNftablesRules**: Rule application and policy enforcement testing
- **TestNftablesConnectivity**: Basic connectivity and firewall functionality

## Continuous Integration

Tests run automatically on:

- Pull requests
- Pushes to master branch
- Manual workflow dispatch

The CI pipeline runs scenarios based on detected changes and includes:

- Ansible lint validation
- YAML lint validation
- Ansible sanity tests
- Conditional molecule testing (only runs tests for changed roles)

## Writing Tests

Tests are written using [Testinfra](https://testinfra.readthedocs.io/) with
pytest fixtures and dynamic Ansible variable access. Example:

```python
class TestUsersCreation:
    """Test suite for user creation and configuration"""

    def test_users_exist(self, host, ansible_vars):
        """Test that all users from users_create variable exist."""
        for user_config in ansible_vars['users_create']:
            user = host.user(user_config["name"])
            assert user.exists, f"User {user_config['name']} does not exist"

            if 'uid' in user_config:
                assert user.uid == user_config["uid"]

    def test_user_ssh_keys(self, host, ansible_vars):
        """Test that SSH public keys are properly configured."""
        for user_config in ansible_vars['users_create']:
            if 'pub_key' not in user_config:
                continue

            username = user_config['name']
            authorized_keys_file = host.file(f"/home/{username}/.ssh/authorized_keys")
            assert authorized_keys_file.exists
            assert authorized_keys_file.mode == 0o600
```

## Debugging Failed Tests

```bash
# Keep environment after failure for debugging
molecule test --destroy=never -s <scenario>

# Connect to test environment for manual inspection
sudo -i

# View test logs with verbose output
molecule test -s <scenario> -- -v

# Run specific test classes
molecule verify -s <scenario> -- tests/test_users.py::TestUsersCreation
```

## Local Development

For faster development iterations:

```bash
# Create environment once
molecule create -s <scenario>

# Iteratively test changes
molecule converge -s <scenario>
molecule verify -s <scenario>

# Cleanup when done
molecule destroy -s <scenario>
```

## Test Variables

Test scenarios use specific variables defined in `group_vars/all/main.yml`:

### Users Scenario Variables

```yaml
users_create:
  - name: "testuser1"
    groups: "sudo"
    uid: 100500
    shell: "/bin/bash"
    pub_key: "ssh-ed25519 AAAAC3NzaC1lZDI1NTE5AAAAIExample... molecule-test"
  - name: "testuser2"
    groups: "users"
    uid: 100501
    shell: "/bin/sh"

users_delete:
  - name: "usertodelete1"
  - name: "usertodelete2"
```

### Nftables Scenario Variables

```yaml
nftables_enabled: true
nftables_state: "started"

nftables_ipv4_policy_input: "drop"
nftables_ipv4_input_rules:
  - 'ct state invalid drop comment "early drop of invalid connections"'
  - 'ct state established,related accept comment "allow tracked connections"'
  - 'iif "lo" accept comment "allow loopback"'
  - 'tcp dport 22 accept comment "allow SSH"'
  - 'tcp dport 80 accept comment "allow HTTP"'
  - 'tcp dport 443 accept comment "allow HTTPS"'

nftables_ipv6_input_rules:
  - 'ct state invalid drop comment "early drop of invalid connections"'
  - 'ct state established,related accept comment "allow tracked connections"'
  - 'iif "lo" accept comment "allow loopback"'
  - 'tcp dport 22 accept comment "allow SSH"'
```

## Security Testing

Tests include security validation:

- **User Security**: UID assignments, group memberships, shell validation
- **SSH Security**: Key file permissions (0600), authorized_keys configuration
- **Home Directory Security**: Proper ownership and permissions (0755)
- **Firewall Security**: Rule application, policy enforcement, connectivity
  testing
- **File Permissions**: Configuration files with appropriate restrictive
  permissions
- **Service Security**: Proper systemd service integration and state management

## Advanced Testing Features

### Dynamic Variable Testing

Tests dynamically read Ansible variables using the `ansible_vars` fixture,
ensuring:

- No hardcoded values in tests
- Automatic adaptation to configuration changes
- Comprehensive validation of all configured items

### Privileged Operations

Nftables tests run with sudo privileges to:

- Install/remove packages
- Manage systemd services
- Configure firewall rules
- Test network connectivity

### Test Lifecycle Management

- **Prepare Stage**: Sets up prerequisites (groups, test users for deletion)
- **Converge Stage**: Applies the role configuration
- **Verify Stage**: Validates role functionality
- **Cleanup Stage**: Removes all test artifacts and configurations

## Integration Testing

While each role is tested independently, the collection supports integration
testing:

```yaml
- hosts: all
  become: true
  tasks:
    # Test complete system setup workflow
    - include_role: name: eliminyro.system.users
    - include_role: name: eliminyro.system.nftables
```

This approach ensures both individual role functionality and cross-role
compatibility.
