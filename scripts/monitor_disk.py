import logging
import time
from threading import Lock

import psutil

logger = logging.getLogger(__name__)

last_disk_io = None
last_disk_time = 0
_disk_lock = Lock()


def get_disk_usage(path: str = "/") -> dict:
    metrics = {
        "total": 0,
        "used": 0,
        "free": 0,
        "percent": 0.0,
        "read_speed_mb": 0.0,
        "write_speed_mb": 0.0,
        "error": None,
    }

    global last_disk_io, last_disk_time

    try:
        disk = psutil.disk_usage(path)
        metrics["total"] = disk.total
        metrics["used"] = disk.used
        metrics["free"] = disk.free
        metrics["percent"] = disk.percent

        try:
            current_disk_io = psutil.disk_io_counters()
            current_time = time.time()

            with _disk_lock:
                if last_disk_io is not None and last_disk_time > 0 and current_disk_io:
                    time_delta = current_time - last_disk_time
                    if 0 < time_delta < 15:
                        bytes_read = current_disk_io.read_bytes - last_disk_io.read_bytes
                        bytes_write = current_disk_io.write_bytes - last_disk_io.write_bytes
                        metrics["read_speed_mb"] = (bytes_read / time_delta) / (1024 * 1024)
                        metrics["write_speed_mb"] = (bytes_write / time_delta) / (1024 * 1024)

                if current_disk_io:
                    last_disk_io = current_disk_io
                    last_disk_time = current_time
        except Exception:
            pass
    except Exception as e:
        logger.error(f"Failed to fetch disk usage metrics for path '{path}': {e}", exc_info=True)
        metrics["error"] = str(e)

    return metrics
