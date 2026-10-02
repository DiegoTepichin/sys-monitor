# pyrefly: ignore [missing-import]
import logging
import time
from datetime import UTC, datetime

import requests

# Import configs and system monitor scripts
from config import API_KEY, HOST, POLL_INTERVAL, PORT
from scripts.monitor_cpu import get_cpu_usage
from scripts.monitor_disk import get_disk_usage
from scripts.monitor_memory import get_memory_usage
from scripts.monitor_network import get_network_usage
from scripts.monitor_processes import get_top_processes

# Setup standalone logging configuration
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger("sys-monitor-agent")


def get_api_url():
    resolved_host = "127.0.0.1" if HOST == "0.0.0.0" else HOST
    return f"http://{resolved_host}:{PORT}/api/metrics"


def run_agent():
    api_url = get_api_url()
    logger.info(
        f"Starting Sys-Monitor Agent daemon. Target API: {api_url} (Interval: {POLL_INTERVAL}s)"
    )

    headers = {"Content-Type": "application/json", "X-API-Key": API_KEY}

    while True:
        try:
            cpu = get_cpu_usage()
            memory = get_memory_usage()
            disk = get_disk_usage()
            processes = get_top_processes(5)
            network = get_network_usage()

            payload = {
                "timestamp": datetime.now(UTC).strftime("%Y-%m-%dT%H:%M:%SZ"),
                "cpu": cpu,
                "memory": memory,
                "disk": disk,
                "network": network,
                "processes": processes,
            }

            logger.info("Collecting hardware snapshots...")
            response = requests.post(api_url, json=payload, headers=headers, timeout=5)

            if response.status_code == 201:
                logger.info("Hardware performance metrics successfully pushed to Flask server.")
            else:
                logger.warning(
                    f"Metrics rejected by server (Status Code: {response.status_code}). Response: {response.text}"
                )

        except requests.exceptions.ConnectionError:
            logger.warning("Connection failed. Flask server is unreachable. Retrying next cycle.")
        except requests.exceptions.RequestException as req_err:
            logger.error(f"Network error trying to connect to API server: {req_err}")
        except Exception as err:
            logger.error(f"Unexpected error in metrics reporting loop: {err}", exc_info=True)

        time.sleep(POLL_INTERVAL)


if __name__ == "__main__":
    run_agent()
