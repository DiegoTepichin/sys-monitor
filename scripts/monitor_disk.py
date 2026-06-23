import psutil
import logging

logger = logging.getLogger(__name__)

def get_disk_usage(path: str = "/") -> dict:
    """Get system disk usage statistics for the specified partition.

    Args:
        path (str): The directory or mount point path to inspect (defaults to "/").

    Returns:
        dict: A dictionary containing:
            - 'total' (int): Total space in bytes.
            - 'used' (int): Used space in bytes.
            - 'free' (int): Free space in bytes.
            - 'percent' (float): Disk usage percentage.
            - 'error' (str or None): Error message if an exception was raised, else None.
    """
    metrics = {
        "total": 0,
        "used": 0,
        "free": 0,
        "percent": 0.0,
        "error": None
    }
    try:
        disk = psutil.disk_usage(path)
        metrics["total"] = disk.total
        metrics["used"] = disk.used
        metrics["free"] = disk.free
        metrics["percent"] = disk.percent
    except Exception as e:
        logger.error(f"Failed to fetch disk usage metrics for path '{path}': {e}", exc_info=True)
        metrics["error"] = str(e)
        
    return metrics
