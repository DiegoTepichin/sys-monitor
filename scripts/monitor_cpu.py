import psutil
import logging

# Configure logger for this module
logger = logging.getLogger(__name__)

def get_cpu_usage() -> float:
    """
    Retrieves the current overall CPU usage percentage.
    Uses a non-blocking check interval to prevent blocking the web server thread.
    
    Returns:
        float: CPU usage percentage (0.0 to 100.0), or 0.0 on failure.
    """
    try:
        # Utilizing interval=0.1 to sample CPU usage quickly without blocking Flask
        return psutil.cpu_percent(interval=0.1)
    except Exception as e:
        logger.error(f"Failed to fetch CPU usage: {e}", exc_info=True)
        return 0.0
