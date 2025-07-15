class TestNftablesInstallation:
    """Test suite for nftables package installation"""

    def test_nftables_package_installed(self, host):
        """Test that nftables package is installed."""
        nftables = host.package("nftables")
        assert nftables.is_installed, "nftables package is not installed"

    def test_nftables_command_available(self, host):
        """Test that nft command is available."""
        cmd = host.run("which nft")
        assert cmd.rc == 0, "nft command not found"


class TestNftablesService:
    """Test suite for nftables service management"""

    def test_nftables_service_enabled(self, host, ansible_vars):
        """Test that nftables service is enabled when configured."""
        if ansible_vars['nftables_enabled']:
            service = host.service("nftables")
            assert service.is_enabled, "nftables service is not enabled"

    def test_nftables_service_running(self, host, ansible_vars):
        """Test that nftables service is running when configured."""
        if ansible_vars['nftables_enabled'] and ansible_vars['nftables_state'] == "started":
            service = host.service("nftables")
            assert service.is_running, "nftables service is not running"


class TestNftablesConfiguration:
    """Test suite for nftables configuration file"""

    def test_nftables_config_file_exists(self, host):
        """Test that nftables configuration file exists."""
        config_file = host.file("/etc/nftables.conf")
        assert config_file.exists, "nftables configuration file does not exist"
        assert config_file.is_file, "nftables config path is not a file"
        assert config_file.user == "root", f"Config file owner is {config_file.user}, expected root"
        assert config_file.group == "root", f"Config file group is {config_file.group}, expected root"
        assert config_file.mode == 0o644, f"Config file permissions are {oct(config_file.mode)}, expected 0o644"

    def test_nftables_config_contains_flush_ruleset(self, host):
        """Test that configuration starts with flush ruleset."""
        config_file = host.file("/etc/nftables.conf")
        content = config_file.content_string
        assert "flush ruleset" in content, "Configuration does not contain 'flush ruleset'"

    def test_nftables_config_contains_tables(self, host):
        """Test that configuration contains required tables."""
        config_file = host.file("/etc/nftables.conf")
        content = config_file.content_string
        assert "table ip filter" in content, "IPv4 filter table not found"
        assert "table ip6 filter" in content, "IPv6 filter table not found"


class TestNftablesRules:
    """Test suite for nftables rules and policies"""

    def test_nftables_ruleset_loaded(self, host):
        """Test that nftables rules are loaded."""
        cmd = host.run("nft list ruleset")
        assert cmd.rc == 0, f"Failed to list nftables ruleset: {cmd.stderr}"

    def test_ipv4_chains_exist(self, host):
        """Test that IPv4 filter chains exist."""
        cmd = host.run("nft list table ip filter")
        assert cmd.rc == 0, "IPv4 filter table does not exist"

        output = cmd.stdout
        assert "chain input" in output, "IPv4 input chain not found"
        assert "chain output" in output, "IPv4 output chain not found"
        assert "chain forward" in output, "IPv4 forward chain not found"

    def test_ipv6_chains_exist(self, host):
        """Test that IPv6 filter chains exist."""
        cmd = host.run("nft list table ip6 filter")
        assert cmd.rc == 0, "IPv6 filter table does not exist"

        output = cmd.stdout
        assert "chain input" in output, "IPv6 input chain not found"
        assert "chain output" in output, "IPv6 output chain not found"
        assert "chain forward" in output, "IPv6 forward chain not found"

    def test_ipv4_chain_policies(self, host, ansible_vars):
        """Test that IPv4 chain policies are correctly set."""
        cmd = host.run("nft list table ip filter")
        output = cmd.stdout

        input_policy = ansible_vars['nftables_ipv4_policy_input']
        output_policy = ansible_vars['nftables_ipv4_policy_output']
        forward_policy = ansible_vars['nftables_ipv4_policy_forward']

        assert f"policy {input_policy}" in output, f"IPv4 input policy {input_policy} not found"
        assert f"policy {output_policy}" in output, f"IPv4 output policy {output_policy} not found"
        assert f"policy {forward_policy}" in output, f"IPv4 forward policy {forward_policy} not found"

    def test_ipv6_chain_policies(self, host, ansible_vars):
        """Test that IPv6 chain policies are correctly set."""
        cmd = host.run("nft list table ip6 filter")
        output = cmd.stdout

        input_policy = ansible_vars['nftables_ipv6_policy_input']
        output_policy = ansible_vars['nftables_ipv6_policy_output']
        forward_policy = ansible_vars['nftables_ipv6_policy_forward']

        assert f"policy {input_policy}" in output, f"IPv6 input policy {input_policy} not found"
        assert f"policy {output_policy}" in output, f"IPv6 output policy {output_policy} not found"
        assert f"policy {forward_policy}" in output, f"IPv6 forward policy {forward_policy} not found"

    def test_ipv4_input_rules_applied(self, host, ansible_vars):
        """Test that IPv4 input rules are applied."""
        if not ansible_vars['nftables_ipv4_input_rules']:
            return

        cmd = host.run("nft list chain ip filter input")
        output = cmd.stdout

        for rule in ansible_vars['nftables_ipv4_input_rules']:
            # Extract the rule part (remove comments for matching)
            rule_part = rule.split(' comment ')[0].strip()
            # Handle potential syntax differences in nft output
            # nft may format braces differently, so we need flexible matching
            assert rule_part in output, f"IPv4 input rule '{rule_part}' not found in active ruleset"

    def test_ipv6_input_rules_applied(self, host, ansible_vars):
        """Test that IPv6 input rules are applied."""
        if not ansible_vars['nftables_ipv6_input_rules']:
            return

        cmd = host.run("nft list chain ip6 filter input")
        output = cmd.stdout

        for rule in ansible_vars['nftables_ipv6_input_rules']:
            # Extract the rule part (remove comments for matching)
            rule_part = rule.split(' comment ')[0].strip()
            # Handle potential syntax differences in nft output
            # nft may format braces differently, so we need flexible matching
            assert rule_part in output, f"IPv6 input rule '{rule_part}' not found in active ruleset"


class TestNftablesConnectivity:
    """Test suite for basic connectivity through nftables"""

    def test_loopback_interface_works(self, host):
        """Test that loopback interface is accessible."""
        cmd = host.run("ping -c 1 127.0.0.1")
        assert cmd.rc == 0, "Loopback connectivity failed"
