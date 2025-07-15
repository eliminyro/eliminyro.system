class TestUsersCreation:
    """Test suite for user creation and configuration"""

    def test_users_exist(self, host, ansible_vars):
        """Test that all users from users_create variable exist."""
        for user_config in ansible_vars['users_create']:
            user = host.user(user_config["name"])
            assert user.exists, f"User {user_config['name']} does not exist"

            if 'uid' in user_config:
                assert user.uid == user_config[
                    "uid"], f"User {user_config['name']} has UID {user.uid}, expected {user_config['uid']}"

            if 'shell' in user_config:
                assert user.shell == user_config[
                    "shell"], f"User {user_config['name']} has shell {user.shell}, expected {user_config['shell']}"

    def test_user_groups(self, host, ansible_vars):
        """Test that users are assigned to correct groups."""
        for user_config in ansible_vars['users_create']:
            if 'groups' not in user_config:
                continue

            username = user_config['name']
            expected_groups = user_config['groups']
            user = host.user(username)

            # Handle both string and list formats for groups
            if isinstance(expected_groups, str):
                expected_groups = [expected_groups]

            for group_name in expected_groups:
                # Check if user is in the group (either primary or supplementary)
                group = host.group(group_name)
                assert group.exists, f"Group {group_name} does not exist"
                assert (user.gid == group.gid or group_name in user.groups), \
                    f"User {username} is not in group {group_name}"

    def test_user_home_directories(self, host, ansible_vars):
        """Test that user home directories exist and have correct permissions."""
        for user_config in ansible_vars['users_create']:
            username = user_config['name']
            home_dir = host.file(f"/home/{username}")

            assert home_dir.exists, f"Home directory for user {username} does not exist"
            assert home_dir.is_directory, f"Home path for user {username} is not a directory"
            assert home_dir.user == username, f"Home directory for user {username} has wrong owner"
            # Home directory should be readable/writable by owner
            assert home_dir.mode & 0o700 == 0o700, f"Home directory for user {username} has incorrect permissions"

    def test_user_ssh_keys(self, host, ansible_vars):
        """Test that SSH public keys are properly configured for users."""
        for user_config in ansible_vars['users_create']:
            if 'pub_key' not in user_config:
                continue

            username = user_config['name']
            pub_key = user_config['pub_key']
            authorized_keys_file = host.file(
                f"/home/{username}/.ssh/authorized_keys")

            assert authorized_keys_file.exists, f"authorized_keys file does not exist for user {username}"
            assert authorized_keys_file.is_file, f"authorized_keys path is not a file for user {username}"
            assert authorized_keys_file.user == username, f"authorized_keys file has wrong owner for user {username}"
            assert authorized_keys_file.mode == 0o600, f"authorized_keys file has incorrect permissions for user {username}"

            # Check that the public key is in the authorized_keys file
            authorized_keys_content = authorized_keys_file.content_string
            assert pub_key in authorized_keys_content, f"Public key not found in authorized_keys for user {username}"

    def test_user_can_login(self, host, ansible_vars):
        """Test that users can potentially login (have valid shell)."""
        for user_config in ansible_vars['users_create']:
            if 'shell' not in user_config:
                continue

            username = user_config['name']
            expected_shell = user_config['shell']
            user = host.user(username)

            # Shell should be a valid shell (exists in /etc/shells or is executable)
            if host.file("/etc/shells").exists:
                shells_content = host.file("/etc/shells").content_string
                assert expected_shell in shells_content, f"Shell {expected_shell} for user {username} not found in /etc/shells"
            else:
                # Fallback check - shell should at least exist and be executable
                shell_file = host.file(expected_shell)
                assert shell_file.exists, f"Shell {expected_shell} for user {username} does not exist"


class TestUsersDeletion:
    """Test suite for verifying user deletion functionality"""

    def test_deleted_users_do_not_exist(self, host, ansible_vars):
        """Test that users from users_delete variable do not exist after role execution."""
        if 'users_delete' not in ansible_vars:
            return

        for usertodelete in ansible_vars['users_delete']:
            user = host.user(usertodelete['name'])
            assert not user.exists, f"User {usertodelete['name']} still exists but should have been deleted"

    def test_deleted_users_home_directories_removed(self, host, ansible_vars):
        """Test that home directories are removed for deleted users."""
        if 'users_delete' not in ansible_vars:
            return

        for usertodelete in ansible_vars['users_delete']:
            home_dir = host.file(f"/home/{usertodelete['name']}")
            assert not home_dir.exists, f"Home directory /home/{usertodelete['name']} still exists for deleted user"
