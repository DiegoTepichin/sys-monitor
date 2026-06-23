# pyrefly: ignore [missing-import]
import time
import requests
import logging
from datetime import datetime

# Import configs and system monitor scripts
from config import POLL_INTERVAL, API_KEY, PORT, HOST
from scripts.monitor_cpu import get_cpu_usage
from scripts.monitor_memory import get_memory_usage
from scripts.monitor_disk import get_disk_usage
from scripts.monitor_processes import get_top_processes

# Setup standalone logging configuration
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("sys-monitor-agent")

# Server endpoint where metrics will be posted
API_URL = f"http://{HOST if HOST != '0.0.0.0' else '127.0.0.1'}:{PORT}/api/metrics"

def run_agent():
    """Starts the monitoring daemon loop.

    Gathers metrics locally from psutil scripts and pushes them to the Flask server
    every POLL_INTERVAL seconds. Handles exceptions internally to ensure the daemon
    remains operational even if the API server goes down.
    """
    logger.info(f"Starting Sys-Monitor Agent daemon. Target API: {API_URL} (Interval: {POLL_INTERVAL}s)")
    
    headers = {
        "X-API-Key": API_KEY,
        "Content-Type": "application/json"
    }

    while True:
        try:
            # Query local hardware metrics
            cpu = get_cpu_usage()
            memory = get_memory_usage()
            disk = get_disk_usage()
            processes = get_top_processes(5)

            # Assemble payload
            payload = {
                "timestamp": datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%SZ'),
                "cpu": cpu,
                "memory": memory,
                "disk": disk,
                "processes": processes
            }

            # Send metrics to Flask server
            logger.info("Collecting hardware snapshots...")
            response = requests.post(API_URL, json=payload, headers=headers, timeout=5)
            
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
            # Catching generic errors so the background thread process is crash-proof
            logger.error(f"Unexpected error in metrics reporting loop: {err}", exc_info=True)

        time.sleep(POLL_INTERVAL)

if __name__ == "__main__":
    run_agent()
