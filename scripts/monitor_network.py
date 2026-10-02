import logging
import time
from threading import Lock

import psutil

logger = logging.getLogger(__name__)

last_net_io = None
last_net_time = 0
_net_lock = Lock()


def get_network_usage() -> dict:
    global last_net_io, last_net_time

    metrics = {"download_mb": 0.0, "upload_mb": 0.0, "error": None}

    try:
        current_net_io = psutil.net_io_counters()
        current_time = time.time()

        with _net_lock:
            if last_net_io is not None and last_net_time > 0:
                time_delta = current_time - last_net_time
                if time_delta > 0:
                    bytes_recv = current_net_io.bytes_recv - last_net_io.bytes_recv
                    bytes_sent = current_net_io.bytes_sent - last_net_io.bytes_sent
                    metrics["download_mb"] = (bytes_recv / time_delta) / (1024 * 1024)
                    metrics["upload_mb"] = (bytes_sent / time_delta) / (1024 * 1024)

            last_net_io = current_net_io
            last_net_time = current_time

    except Exception as e:
        logger.error(f"Failed to fetch network metrics: {e}", exc_info=True)
        metrics["error"] = str(e)

    return metrics
