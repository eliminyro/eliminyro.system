import pytest
from testinfra.utils.ansible_runner import AnsibleRunner
from testinfra import get_host
import os


testinfra_hosts = AnsibleRunner(
    os.environ['MOLECULE_INVENTORY_FILE']
).get_hosts('all')


@pytest.fixture
def host():
    """Fixture providing host object with sudo privileges"""
    host_name = testinfra_hosts[0]
    return get_host(f'ansible://{host_name}', sudo=True)


@pytest.fixture
def ansible_vars():
    """Fixture providing access to Ansible variables from the playbook"""
    host_name = testinfra_hosts[0]
    host = get_host(f'ansible://{host_name}')

    # Use debug module to get all host variables
    result = host.ansible('debug', 'var=hostvars[inventory_hostname]')
    return result['hostvars[inventory_hostname]']
