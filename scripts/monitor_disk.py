import psutil
import logging

logger = logging.getLogger(__name__)

def get_disk_usage(path: str = "/") -> dict:
    """
    Retrieves system disk usage statistics for the specified partition.
    
    Args:
        path (str): The directory/mount point to inspect (default is root directory "/").
        
    Returns:
        dict: Detailed disk metrics containing total, used, free (in bytes),
              and usage percentage, or empty dict on error.
    """
    try:
        disk = psutil.disk_usage(path)
        return {
            "total": disk.total,
            "used": disk.used,
            "free": disk.free,
            "percent": disk.percent
        }
    except Exception as e:
        logger.error(f"Failed to fetch disk usage metrics for path '{path}': {e}", exc_info=True)
        return {}
