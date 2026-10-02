# pyrefly: ignore [missing-import]
from types import SimpleNamespace
from unittest.mock import MagicMock, patch

import psutil

from scripts import monitor_network
from scripts.monitor_processes import get_top_processes


def test_network_usage_computes_rate_from_counter_delta():
    first = SimpleNamespace(bytes_recv=0, bytes_sent=0)
    second = SimpleNamespace(bytes_recv=4 * 1024 * 1024, bytes_sent=2 * 1024 * 1024)
    monitor_network.last_net_io = None
    monitor_network.last_net_time = 0

    with (
        patch("psutil.net_io_counters", side_effect=[first, second]),
        patch("time.time", side_effect=[100.0, 102.0]),
    ):
        baseline = monitor_network.get_network_usage()
        result = monitor_network.get_network_usage()

    assert baseline["download_mb"] == 0.0
    assert result["download_mb"] == 2.0
    assert result["upload_mb"] == 1.0
    assert result["error"] is None


def test_network_usage_reports_errors():
    with patch("psutil.net_io_counters", side_effect=RuntimeError("no nic")):
        result = monitor_network.get_network_usage()

    assert result["error"] == "no nic"


def _proc(pid, name, cpu):
    proc = MagicMock()
    proc.info = {"pid": pid, "name": name, "cpu_percent": cpu, "memory_percent": 1.0}
    return proc


def test_top_processes_sorted_by_cpu_and_skips_vanished():
    vanished = MagicMock()
    type(vanished).info = property(lambda _: (_ for _ in ()).throw(psutil.NoSuchProcess(9)))
    procs = [_proc(1, "a", 5.0), vanished, _proc(2, "b", 50.0), _proc(3, "c", 20.0)]

    with patch("psutil.process_iter", return_value=procs):
        result = get_top_processes(2)

    assert [p["name"] for p in result] == ["b", "c"]
