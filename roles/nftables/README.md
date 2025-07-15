# Ansible Role: nftables

This role is part of the `eliminyro.system` collection and automates comprehensive firewall management using nftables. It handles package installation, service management, rule configuration, and provides secure default policies for both IPv4 and IPv6 traffic.

## Requirements

- Ansible 2.15+ and Python 3.x on the control node.
- Target system with systemd support.
- Root/sudo privileges on target hosts.
- nftables support in the kernel (most modern Linux distributions).

## Overview

The role performs the following firewall management operations:

1. **Install nftables** – Installs nftables package and dependencies
2. **Configure service** – Manages nftables systemd service
3. **Generate rules** – Creates nftables configuration from templates
4. **Apply policies** – Sets up chain policies for input, output, and forward
5. **Load rules** – Applies custom rules for IPv4 and IPv6 traffic

## Role Variables

### Service Management

| Variable          | Default     | Description                              |
| ----------------- | ----------- | ---------------------------------------- |
| `nftables_enabled` | `true`     | Enable nftables service                  |
| `nftables_state`   | `"started"` | Service state (`started` or `stopped`)  |

### IPv4 Chain Policies

| Variable                      | Default   | Description                    |
| ----------------------------- | --------- | ------------------------------ |
| `nftables_ipv4_policy_input`  | `"drop"`  | Input chain default policy     |
| `nftables_ipv4_policy_output` | `"accept"` | Output chain default policy   |
| `nftables_ipv4_policy_forward` | `"accept"` | Forward chain default policy |

### IPv6 Chain Policies  

| Variable                      | Default   | Description                    |
| ----------------------------- | --------- | ------------------------------ |
| `nftables_ipv6_policy_input`  | `"drop"`  | Input chain default policy     |
| `nftables_ipv6_policy_output` | `"accept"` | Output chain default policy   |
| `nftables_ipv6_policy_forward` | `"accept"` | Forward chain default policy |

### IPv4 Rules

| Variable                     | Default | Description                     |
| ---------------------------- | ------- | ------------------------------- |
| `nftables_ipv4_input_rules`  | `[]`    | List of input chain rules       |
| `nftables_ipv4_output_rules` | `[]`    | List of output chain rules      |
| `nftables_ipv4_forward_rules` | `[]`   | List of forward chain rules     |

### IPv6 Rules

| Variable                     | Default | Description                     |
| ---------------------------- | ------- | ------------------------------- |
| `nftables_ipv6_input_rules`  | `[]`    | List of input chain rules       |
| `nftables_ipv6_output_rules` | `[]`    | List of output chain rules      |
| `nftables_ipv6_forward_rules` | `[]`   | List of forward chain rules     |

## Dependencies

None.

## Example Playbook

### Basic Firewall Setup

```yaml
---
- hosts: servers
  become: true
  vars:
    nftables_enabled: true
    nftables_state: "started"
    
    nftables_ipv4_policy_input: "drop"
    nftables_ipv4_input_rules:
      - "ct state invalid drop comment \"early drop of invalid connections\""
      - "ct state established,related accept comment \"allow tracked connections\""
      - "iif \"lo\" accept comment \"allow loopback\""
      - "tcp dport 22 accept comment \"allow SSH\""

  roles:
    - eliminyro.system.nftables
```

### Web Server Configuration

```yaml
---
- hosts: webservers
  become: true
  vars:
    nftables_enabled: true
    nftables_state: "started"
    
    nftables_ipv4_policy_input: "drop"
    nftables_ipv4_input_rules:
      - "ct state invalid drop comment \"early drop of invalid connections\""
      - "ct state established,related accept comment \"allow tracked connections\""
      - "iif \"lo\" accept comment \"allow loopback\""
      - "tcp dport 22 accept comment \"allow SSH\""
      - "tcp dport 80 accept comment \"allow HTTP\""
      - "tcp dport 443 accept comment \"allow HTTPS\""
    
    nftables_ipv6_input_rules:
      - "ct state invalid drop comment \"early drop of invalid connections\""
      - "ct state established,related accept comment \"allow tracked connections\""
      - "iif \"lo\" accept comment \"allow loopback\""
      - "tcp dport 22 accept comment \"allow SSH\""
      - "tcp dport 80 accept comment \"allow HTTP\""
      - "tcp dport 443 accept comment \"allow HTTPS\""

  roles:
    - eliminyro.system.nftables
```

### Advanced Configuration with Custom Rules

```yaml
---
- hosts: all
  become: true
  vars:
    nftables_enabled: true
    nftables_state: "started"
    
    # Restrictive input policy
    nftables_ipv4_policy_input: "drop"
    nftables_ipv4_policy_output: "accept"
    nftables_ipv4_policy_forward: "drop"
    
    nftables_ipv4_input_rules:
      # Connection tracking
      - "ct state invalid drop comment \"drop invalid connections\""
      - "ct state established,related accept comment \"allow established connections\""
      
      # Loopback
      - "iif \"lo\" accept comment \"allow loopback\""
      
      # SSH with rate limiting
      - "tcp dport 22 ct state new limit rate 5/minute accept comment \"SSH with rate limit\""
      
      # Web services
      - "tcp dport { 80, 443 } accept comment \"allow HTTP/HTTPS\""
      
      # DNS
      - "udp dport 53 accept comment \"allow DNS queries\""
      
      # NTP
      - "udp dport 123 accept comment \"allow NTP\""
      
      # ICMP
      - "icmp type { echo-request, destination-unreachable, time-exceeded } accept comment \"allow ICMP\""
    
    nftables_ipv4_output_rules:
      # Log dropped outbound traffic
      - "log prefix \"nftables-output-drop: \" drop"
    
    # IPv6 configuration
    nftables_ipv6_policy_input: "drop"
    nftables_ipv6_input_rules:
      - "ct state invalid drop comment \"drop invalid connections\""
      - "ct state established,related accept comment \"allow established connections\""
      - "iif \"lo\" accept comment \"allow loopback\""
      - "tcp dport 22 accept comment \"allow SSH\""
      - "icmpv6 type { echo-request, destination-unreachable, time-exceeded, nd-neighbor-solicit, nd-neighbor-advert } accept comment \"allow ICMPv6\""

  roles:
    - eliminyro.system.nftables
```

## Rule Syntax

Rules use standard nftables syntax. Common patterns include:

### Connection Tracking
```yaml
- "ct state established,related accept"
- "ct state invalid drop"
- "ct state new limit rate 10/minute accept"
```

### Port-based Rules
```yaml
- "tcp dport 80 accept"
- "tcp dport { 80, 443 } accept"
- "udp dport 53 accept"
```

### Interface-based Rules
```yaml
- "iif \"lo\" accept"
- "iif \"eth0\" tcp dport 22 accept"
```

### IP-based Rules
```yaml
- "ip saddr 192.168.1.0/24 accept"
- "ip daddr 10.0.0.1 accept"
```

### Logging
```yaml
- "log prefix \"firewall-drop: \" drop"
- "log level warn prefix \"suspicious: \" drop"
```

## Default Configuration

The role provides secure defaults:

- **Input Policy**: `drop` (deny by default)
- **Output Policy**: `accept` (allow outbound traffic)
- **Forward Policy**: `accept` (allow routing if needed)

Essential rules should be added to prevent lockout:
```yaml
nftables_ipv4_input_rules:
  - "ct state established,related accept"
  - "iif \"lo\" accept"
  - "tcp dport 22 accept"  # SSH access
```

## Security Considerations

- **Default Deny**: Uses drop policies for maximum security
- **Connection Tracking**: Implements stateful filtering for established connections
- **Loopback Protection**: Always allows loopback interface traffic
- **SSH Access**: Ensure SSH rules are included to prevent lockout
- **Rule Order**: Rules are processed in order, place more specific rules first
- **Rate Limiting**: Consider rate limiting for services like SSH

## Integration with Other Roles

This role works well with other system management roles:

```yaml
- hosts: servers
  become: true
  tasks:
    # Create users first
    - include_role:
        name: eliminyro.system.users
      vars:
        users_create:
          - name: "admin"
            groups: "sudo"
    
    # Install packages
    - include_role:
        name: eliminyro.system.packages
      vars:
        packages: ["openssh-server", "nginx"]
    
    # Configure firewall last
    - include_role:
        name: eliminyro.system.nftables
      vars:
        nftables_ipv4_input_rules:
          - "ct state established,related accept"
          - "iif \"lo\" accept"
          - "tcp dport 22 accept comment \"SSH\""
          - "tcp dport { 80, 443 } accept comment \"Web\""
```

## Testing

This role includes comprehensive molecule testing that verifies:
- Package installation and service management
- Configuration file generation and syntax
- Rule application and policy enforcement
- IPv4 and IPv6 functionality
- Basic connectivity through firewall rules

Run tests with:
```bash
molecule test -s nftables
```

## Troubleshooting

### Common Issues

1. **Locked out via SSH**: Ensure SSH rules are included before applying restrictive policies
2. **Service won't start**: Check rule syntax with `nft -f /etc/nftables.conf`
3. **Rules not applying**: Verify nftables service is enabled and started
4. **IPv6 issues**: Ensure kernel supports IPv6 and nftables IPv6 features

### Debugging Commands

```bash
# Check current ruleset
nft list ruleset

# Test configuration syntax
nft -f /etc/nftables.conf

# Check service status
systemctl status nftables

# View service logs
journalctl -u nftables
```