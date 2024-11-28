import subprocess

import pytest


@pytest.fixture(scope="session", autouse=True)
def install_dcgm_snap():
    """Install the snap and enable openstack-exporter service for testing."""
    snap_build_name = "charmed-openstack-exporter_*.snap"

    subprocess.check_call(
        f"sudo snap install --dangerous {snap_build_name}",
        shell=True,
    )

    # To allow the snap to read from the /etc/openstack/, manually add the connection:
    subprocess.check_call("sudo snap connect charmed-openstack-exporter:etc-openstack".split())

    subprocess.check_call("sudo snap start charmed-openstack-exporter".split())

    yield

    subprocess.check_call("sudo snap remove --purge charmed-openstack-exporter".split())
