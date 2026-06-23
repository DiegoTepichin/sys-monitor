import psutil
import logging

logger = logging.getLogger(__name__)

def get_top_processes(n: int = 5) -> list:
    """
    Retrieves the top N active processes sorted by CPU utilization percentage.
    
    Args:
        n (int): Number of top processes to retrieve (default is 5).
        
    Returns:
        list: A sorted list of dictionaries containing process PID, name,
              CPU usage, and Memory usage, or an empty list on error.
    """
    processes_list = []
    try:
        # Iterating over all running processes to capture basic details
        for proc in psutil.process_iter(['pid', 'name', 'cpu_percent', 'memory_percent']):
            try:
                # Fetching the process attributes dictionary
                info = proc.info
                # Ensure cpu_percent is not None before sorting
                if info['cpu_percent'] is not None:
                    processes_list.append(info)
            except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
                # Safely ignore transient or system-restricted processes
                continue
        
        # Sort list descending by CPU usage percentage
        processes_list.sort(key=lambda x: x['cpu_percent'], reverse=True)
        return processes_list[:n]
    except Exception as e:
        logger.error(f"Failed to fetch running processes list: {e}", exc_info=True)
        return []
