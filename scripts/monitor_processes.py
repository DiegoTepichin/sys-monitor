import logging

import psutil

logger = logging.getLogger(__name__)


def get_top_processes(n: int = 5) -> list:
    processes_list = []
    try:
        for proc in psutil.process_iter(["pid", "name", "cpu_percent", "memory_percent"]):
            try:
                info = proc.info
                if info["cpu_percent"] is not None:
                    processes_list.append(info)
            except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
                continue

        processes_list.sort(key=lambda x: x["cpu_percent"], reverse=True)
        return processes_list[:n]

    except Exception as e:
        logger.error(f"Failed to fetch running processes list: {e}", exc_info=True)
        return []
