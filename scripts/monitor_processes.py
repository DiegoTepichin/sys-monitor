import psutil
import logging

logger = logging.getLogger(__name__)

def get_top_processes(n: int = 5) -> list:
    """Get the top N active processes sorted by CPU utilization.

    Filters out early system daemons and kernel processes (PIDs < 10) to only
    show user-space processes.

    Args:
        n (int): Max number of processes to return (defaults to 5).

    Returns:
        list: A list of dicts. Each dict contains:
            - 'pid' (int): Process ID.
            - 'name' (str): Executable name.
            - 'cpu_percent' (float): CPU usage percent.
            - 'memory_percent' (float): RAM usage percent.
            - If it fails, returns an empty list.
    """
    processes_list = []
    try:
        # Fetch CPU utilization for all processes
        for proc in psutil.process_iter(['pid', 'name', 'cpu_percent', 'memory_percent']):
            try:
                info = proc.info
                # Filter out system-level processes (PID < 10)
                if info['pid'] is not None and info['pid'] < 10:
                    continue
                
                # Check for active processes
                if info['cpu_percent'] is not None:
                    processes_list.append(info)
            except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
                continue
                
        # Sort list descending by CPU usage
        processes_list.sort(key=lambda x: x['cpu_percent'], reverse=True)
        return processes_list[:n]
        
    except Exception as e:
        logger.error(f"Failed to fetch running processes list: {e}", exc_info=True)
        return []
