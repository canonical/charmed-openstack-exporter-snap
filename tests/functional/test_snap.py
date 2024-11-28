import subprocess


def test_snap_installed():
    subprocess.check_call(["snap", "list", "charmed-openstack-exporter"])
