import os

# Server Configuration
PORT = int(os.environ.get("PORT", 5000))
HOST = os.environ.get("HOST", "0.0.0.0")
DEBUG = os.environ.get("DEBUG", "True").lower() == "true"

# System Health Thresholds (Percentage)
CPU_THRESHOLD = int(os.environ.get("CPU_THRESHOLD", 80))      # Warning threshold for CPU
MEMORY_THRESHOLD = int(os.environ.get("MEMORY_THRESHOLD", 85))  # Warning threshold for RAM
DISK_THRESHOLD = int(os.environ.get("DISK_THRESHOLD", 90))      # Warning threshold for Disk
