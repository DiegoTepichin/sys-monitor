import psutil
import logging

logger = logging.getLogger(__name__)

def get_memory_usage() -> dict:
    """Get virtual memory usage details.

    Retrieves total, used, free and percentage utilization of RAM using psutil.
    Catches errors locally and reports them in the returned dictionary.

    Returns:
        dict: A dictionary containing:
            - 'total' (int): Total physical memory in bytes.
            - 'used' (int): Memory currently used by the system in bytes.
            - 'free' (int): Free physical memory in bytes.
            - 'percent' (float): Percentage of memory usage (0.0 to 100.0).
            - 'error' (str or None): Error message if fetching metrics failed, else None.
    """
    metrics = {
        "total": 0,
        "used": 0,
        "free": 0,
        "percent": 0.0,
        "error": None
    }
    try:
        mem = psutil.virtual_memory()
        metrics["total"] = mem.total
        metrics["used"] = mem.used
        metrics["free"] = mem.free
        metrics["percent"] = mem.percent
    except Exception as e:
        logger.error(f"Failed to fetch memory metrics: {e}", exc_info=True)
        metrics["error"] = str(e)
        
    return metrics
