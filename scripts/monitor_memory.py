import psutil
import logging

logger = logging.getLogger(__name__)

def get_memory_usage() -> dict:
    """
    Retrieves system virtual memory details.
    
    Returns:
        dict: Detailed memory metrics containing total, available, 
              used, free, and usage percentage, or empty dict on error.
    """
    try:
        mem = psutil.virtual_memory()
        return {
            "total": mem.total,
            "available": mem.available,
            "percent": mem.percent,
            "used": mem.used,
            "free": mem.free
        }
    except Exception as e:
        logger.error(f"Failed to fetch memory metrics: {e}", exc_info=True)
        return {}
