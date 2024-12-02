import subprocess

import pytest


@pytest.fixture(scope="session", autouse=True)
def install_charmed_openstack_exporter_snap():
    """Install the snap and enable openstack-exporter service for testing."""
    snap_build_name = "charmed-openstack-exporter_*.snap"
    config_dir_path = "/etc/openstack"
    config_file_path = f"{config_dir_path}/clouds.yaml"
    config_test_file_path = f"{config_dir_path}/test.yaml"

    subprocess.check_call(
        f"sudo snap install --dangerous {snap_build_name}",
        shell=True,
    )

    # Create the directory if it doesn't exist and create the file
    subprocess.check_call(["sudo", "mkdir", "-p", config_dir_path])
    subprocess.check_call(["sudo", "touch", config_file_path])
    subprocess.check_call(["sudo", "touch", config_test_file_path])

    # To allow the snap to read from the /etc/openstack/, manually add the connection:
    subprocess.check_call(["sudo", "snap", "connect", "charmed-openstack-exporter:etc-openstack"])
    subprocess.check_call(
        [
            "sudo",
            "snap",
            "set",
            "charmed-openstack-exporter",
            f"os-client-config={config_file_path}",
            "cloud=cloud",
        ]
    )
    subprocess.check_call(["sudo", "snap", "start", "charmed-openstack-exporter"])

    yield

    subprocess.check_call(["sudo", "snap", "remove", "--purge", "charmed-openstack-exporter"])
    subprocess.check_call(["sudo", "rm", config_file_path])
    subprocess.check_call(["sudo", "rm", config_test_file_path])
    subprocess.check_call(["sudo", "rmdir", config_dir_path])
