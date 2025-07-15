# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to
[Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added

- **Molecule testing infrastructure** - Complete molecule scenarios for all
  roles

  - Created molecule directory structure with individual scenarios for each role
  - Added centralized group_vars configuration for test variables
  - Implemented testinfra verification suites for comprehensive testing

- **Users role molecule scenario**

  - Full test coverage for user creation, group assignment, SSH keys, and shell
    validation
  - User deletion testing with proper cleanup verification
  - Prepare stage ensuring required groups exist before user creation
  - Cleanup stage for proper test environment teardown
  - Dynamic testing using Ansible variables instead of hardcoded values

- **Nftables role molecule scenario**

  - Complete firewall configuration testing including service management
  - IPv4 and IPv6 rule validation with policy enforcement testing
  - Configuration file validation and active ruleset verification
  - Basic connectivity testing to ensure firewall functionality
  - Cleanup stage for complete nftables removal and environment reset
  - Host fixture with sudo privileges for privileged operations

- **Packages role molecule scenario**
  - Multi-platform testing support (Ubuntu, Debian, ArchLinux)
  - Dynamic package installation verification across different distributions

### Enhanced

- **Test organization** - Structured tests using class-based organization
  following collection best practices
- **Cross-platform compatibility** - Tests handle distribution differences
  (group variations, package managers)
- **Error handling** - Comprehensive error messages and graceful handling of
  optional configuration fields
- **Documentation** - Inline documentation and clear test descriptions for
  maintainability

### Technical Improvements

- **Ansible variable integration** - All tests dynamically use Ansible variables
  from group_vars
- **Testinfra fixtures** - Proper conftest.py setup with ansible_vars and host
  fixtures
- **Molecule configuration** - Optimized molecule.yml configurations for
  efficient testing
- **Prepare/cleanup stages** - Proper test environment setup and teardown
  procedures

## [0.1.0] - Initial Release

### Added

- **Users role** - Complete user management functionality

  - User creation with configurable UID, shell, and group assignments
  - User deletion capabilities for cleanup operations
  - SSH public key management with authorized_keys configuration
  - Home directory creation with proper permissions
  - Support for both individual users and batch operations
  - Group membership management (primary and supplementary groups)

- **Nftables role** - Comprehensive firewall management

  - IPv4 and IPv6 firewall table configuration
  - Configurable chain policies (input, output, forward)
  - Custom rule sets for input, output, and forward chains
  - Service management (enable/disable, start/stop)
  - Template-based configuration file generation
  - Support for connection tracking and stateful filtering
  - Default secure configuration with drop policies

- **Packages role** - Multi-distribution package management
  - Distribution-specific package lists (Debian, ArchLinux)
  - Automatic distribution detection and package mapping
  - Batch package installation using native package managers
  - Support for common development and system packages
  - Extensible package definition system

### Features

- **Cross-platform support** - Roles work across Debian-based and Arch-based
  systems
- **Idempotent operations** - All roles support repeated execution without side
  effects
- **Configurable defaults** - Sensible defaults with full customization
  capabilities
- **Template system** - Dynamic configuration file generation using Jinja2
  templates
- **Service integration** - Proper systemd service management where applicable

### Initial Configuration

- **Galaxy metadata** - Proper collection structure with galaxy.yml
- **Role documentation** - Basic README files for each role
- **Default variables** - Comprehensive default configurations in
  roles/\*/defaults/main.yml
- **Task organization** - Well-structured task files with clear naming
  conventions
