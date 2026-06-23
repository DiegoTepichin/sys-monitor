import psutil
import logging

logger = logging.getLogger(__name__)

def get_cpu_usage() -> dict:
    """Get current CPU usage percentage, core count, and system temperature.

    Attempts to read overall CPU performance and temperature metrics using
    the psutil library. Handles exceptions gracefully to ensure the daemon remains stable.

    Returns:
        dict: A dictionary containing:
            - 'percent' (float): Total CPU utilization percentage.
            - 'cores' (int): Logical processor core count.
            - 'temperature' (float or None): System CPU temperature in Celsius if supported, else None.
            - 'error' (str or None): Error message if exception raised, else None.
    """
    metrics = {
        "percent": 0.0,
        "cores": 0,
        "temperature": None,
        "error": None
    }
    try:
        metrics["cores"] = psutil.cpu_count(logical=True) or 0
        metrics["percent"] = psutil.cpu_percent(interval=0.1)
        
        # Try to obtain system temperatures
        try:
            temps = psutil.sensors_temperatures()
            # Look for common labels for CPU sensors
            if temps:
                for name, entries in temps.items():
                    if 'cpu' in name.lower() or 'core' in name.lower() or 'temp' in name.lower():
                        if entries:
                            metrics["temperature"] = entries[0].current
                            break
        except Exception as temp_err:
            # System might not support temperature reading (e.g. macOS or virtualization environments)
            logger.debug(f"Temperature reading not supported: {temp_err}")
            
    except Exception as e:
        logger.error(f"Failed to fetch CPU metrics: {e}", exc_info=True)
        metrics["error"] = str(e)
        
    return metrics
