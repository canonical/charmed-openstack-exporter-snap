import subprocess
import urllib.request
from contextlib import contextmanager

import pytest
from tenacity import Retrying, retry, stop_after_delay, wait_fixed

ENDPOINT = "http://localhost:9180"
SYSTEMD_SERVICE = "snap.charmed-openstack-exporter.service.service"
SNAP_NAME = "charmed-openstack-exporter"


@retry(wait=wait_fixed(2), stop=stop_after_delay(10))
def _assert_service_failed() -> None:
    """Assert the systemd service is in a failed state."""
    assert 0 == subprocess.call(
        ["sudo", "systemctl", "is-failed", "--quiet", SYSTEMD_SERVICE]
    ), f"{SYSTEMD_SERVICE} is running"


@retry(wait=wait_fixed(2), stop=stop_after_delay(10))
def _assert_service_active() -> None:
    """Assert the systemd service is in a active state."""
    assert 0 == subprocess.call(
        ["sudo", "systemctl", "is-active", "--quiet", SYSTEMD_SERVICE]
    ), f"{SYSTEMD_SERVICE} is not running"


@retry(wait=wait_fixed(5), stop=stop_after_delay(30))
def _assert_endpoint_reachable(endpoint: str) -> None:
    """Assert the endpoint is reachable."""
    response = urllib.request.urlopen(endpoint)  # will raise if not reachable
    status_code = response.getcode()
    assert status_code == 200, f"Endpoint {endpoint} returned status code {status_code}"


@retry(wait=wait_fixed(2), stop=stop_after_delay(10))
def _assert_service_listening(bind: str, service: str) -> None:
    """Assert service is listening on a specific bind."""
    pid = subprocess.check_output(["sudo", "lsof", "-t", "-i", bind], text=True).strip()
    assert service in subprocess.check_output(
        ["cat", f"/proc/{pid}/cmdline"], text=True
    ), f"{service} is not listening on {bind}"


@retry(wait=wait_fixed(2), stop=stop_after_delay(10))
def _set_snap_config(config: str, value: str) -> None:
    """Set a configuration value for a snap service."""
    assert 0 == subprocess.call(
        ["sudo", "snap", "set", SNAP_NAME, f"{config}={value}"]
    ), f"Failed to set {config} to {value}"


@retry(wait=wait_fixed(2), stop=stop_after_delay(10))
def _unset_snap_config(config: str) -> None:
    """Unset a configuration value for a snap service."""
    assert 0 == subprocess.call(
        ["sudo", "snap", "unset", SNAP_NAME, config]
    ), f"Failed to unset {config}"


@retry(wait=wait_fixed(2), stop=stop_after_delay(10))
def _restart_snap_service() -> None:
    """Restart the snap services."""
    assert 0 == subprocess.call(
        ["sudo", "snap", "restart", f"{SNAP_NAME}.service"]
    ), "Failed to restart snap"


def _get_start_cmd(process: str) -> str:
    """Get the command used to start a process."""
    return subprocess.check_output(["ps", "-C", process, "-o", "cmd", "-ww"], text=True)


def _assert_config_exists(config: str):
    """Check if a configuration exists in the snap configuration."""
    assert 0 == subprocess.call(
        ["sudo", "snap", "get", SNAP_NAME, config]
    ), "Snap configuration does not exist"


@contextmanager
def _snap_config_ctx(config, new_value):
    """Set up a context manager to test snap configuration."""
    try:
        _assert_config_exists(config)
        _set_snap_config(config, new_value)
        _restart_snap_service()
        yield
    finally:
        # Revert back
        _unset_snap_config(config)
        _restart_snap_service()
        _assert_service_active()


# Snap tests


def test_openstack_exporter_binary() -> None:
    """Test the charmed_openstack_exporter binary."""
    assert 0 == subprocess.call(
        [f"{SNAP_NAME}.openstack-exporter", "--help"]
    ), "openstack-exporter binary not found"


def test_charmed_openstack_exporter_service() -> None:
    """Test of the charmed_openstack_exporter service and its endpoint."""
    _assert_service_active()
    # We don't test for the /metrics endpoint as there is no cloud
    _assert_endpoint_reachable(ENDPOINT)


def test_valid_bind_config() -> None:
    """Test valid snap bind configuration."""
    new_bind = ":9770"
    with _snap_config_ctx("web.listen-address", new_bind):
        _assert_service_listening(new_bind, SNAP_NAME)


def test_invalid_bind_config() -> None:
    """Test invalid snap bind configuration."""
    with _snap_config_ctx("web.listen-address", "test"):
        _assert_service_failed()


def test_cloud_config_arg() -> None:
    """Test cloud configuration argument."""
    with _snap_config_ctx("cloud", "test-cloud"):
        _assert_service_active()
        for attempt in Retrying(wait=wait_fixed(2), stop=stop_after_delay(10)):
            with attempt:
                assert "test-cloud" in _get_start_cmd("openstack-exporter"), "cloud is not set"


@pytest.mark.parametrize(
    "config",
    [
        "collect-metric-time",
        "disable-cinder-agent-uuid",
        "disable-deprecated-metrics",
        "disable-service.baremetal",
        "disable-service.compute",
        "disable-service.container-infra",
        "disable-service.database",
        "disable-service.dns",
        "disable-service.gnocchi",
        "disable-service.identity",
        "disable-service.image",
        "disable-service.load-balancer",
        "disable-service.network",
        "disable-service.object-store",
        "disable-service.orchestration",
        "disable-service.placement",
        "disable-service.volume",
        "disable-slow-metrics",
        "multi-cloud",
        "cache",
    ],
)
def test_enable_config_flag(config: str) -> None:
    """Test enable snap flag configuration."""
    with _snap_config_ctx(config, "true"):
        _assert_service_active()
        for attempt in Retrying(wait=wait_fixed(2), stop=stop_after_delay(10)):
            with attempt:
                assert f"--{config}" in _get_start_cmd(
                    "openstack-exporter"
                ), f"{config} is not enabled"


@pytest.mark.parametrize(
    "config",
    [
        "collect-metric-time",
        "disable-cinder-agent-uuid",
        "disable-deprecated-metrics",
        "disable-service.baremetal",
        "disable-service.compute",
        "disable-service.container-infra",
        "disable-service.database",
        "disable-service.dns",
        "disable-service.gnocchi",
        "disable-service.identity",
        "disable-service.image",
        "disable-service.load-balancer",
        "disable-service.network",
        "disable-service.object-store",
        "disable-service.orchestration",
        "disable-service.placement",
        "disable-service.volume",
        "disable-slow-metrics",
        "multi-cloud",
        "cache",
    ],
)
def test_disable_config_flag(config) -> None:
    """Test disable snap flag configuration."""
    with _snap_config_ctx(config, "false"):
        _assert_service_active()
        for attempt in Retrying(wait=wait_fixed(2), stop=stop_after_delay(10)):
            with attempt:
                assert f"--{config}" not in _get_start_cmd(
                    "openstack-exporter"
                ), f"{config} is not disabled"


@pytest.mark.parametrize(
    "config",
    [
        "collect-metric-time",
        "disable-cinder-agent-uuid",
        "disable-deprecated-metrics",
        "disable-service.baremetal",
        "disable-service.compute",
        "disable-service.container-infra",
        "disable-service.database",
        "disable-service.dns",
        "disable-service.gnocchi",
        "disable-service.identity",
        "disable-service.image",
        "disable-service.load-balancer",
        "disable-service.network",
        "disable-service.object-store",
        "disable-service.orchestration",
        "disable-service.placement",
        "disable-service.volume",
        "disable-slow-metrics",
        "multi-cloud",
        "cache",
    ],
)
def test_invalid_config_flag(config) -> None:
    """Test invalid snap flag configuration."""
    assert 0 != subprocess.call(
        ["sudo", "snap", "set", SNAP_NAME, f"{config}=test"]
    ), "Invalid configuration flag was set"


@pytest.mark.parametrize(
    "config, new_value",
    [
        ("endpoint-type", "public"),
        ("log.format", "json"),
        ("log.level", "info"),
        ("os-client-config", "/etc/openstack/test.yaml"),
        ("prefix", "test"),
        ("cache-ttl", "10s"),
        ("web.telemetry-path", "/test-metrics"),
        ("domain-id", "0"),
    ],
)
def test_valid_value_config(config: str, new_value: str) -> None:
    with _snap_config_ctx(config, new_value):
        _assert_service_active()
        for attempt in Retrying(wait=wait_fixed(2), stop=stop_after_delay(10)):
            with attempt:
                assert f"--{config}={new_value}" in _get_start_cmd(
                    "openstack-exporter"
                ), f"{config} is not set"


@pytest.mark.parametrize(
    "config, new_value",
    [
        ("log.format", "test"),
        ("log.level", "test"),
        ("os-client-config", "test"),
        ("cache-ttl", "test"),
        ("web.telemetry-path", "test"),
    ],
)
def test_invalid_value_config(config: str, new_value: str) -> None:
    with _snap_config_ctx(config, new_value):
        _assert_service_failed()


def test_disable_metrics_config() -> None:
    """Test disable metrics configuration."""
    new_value = "test-metrics1 test-metrics2 test-metrics3"
    with _snap_config_ctx("disable-metrics", f"{new_value}"):
        _assert_service_active()
        for metric in new_value.split():
            for attempt in Retrying(wait=wait_fixed(2), stop=stop_after_delay(10)):
                with attempt:
                    assert f"--disable-metric={metric}" in _get_start_cmd(
                        "openstack-exporter"
                    ), f"{metric} is not disabled"
