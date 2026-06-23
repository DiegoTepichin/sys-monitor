# pyrefly: ignore [missing-import]
import pytest
from unittest.mock import patch, MagicMock

# Import the monitor modules to test
from scripts.monitor_cpu import get_cpu_usage
from scripts.monitor_memory import get_memory_usage
from scripts.monitor_disk import get_disk_usage

def test_get_cpu_usage_success():
    """Test get_cpu_usage returns expected structure under normal conditions."""
    with patch('psutil.cpu_count') as mock_cpu_count, \
         patch('psutil.cpu_percent') as mock_cpu_percent, \
         patch('psutil.sensors_temperatures', create=True) as mock_temps:
         
        mock_cpu_count.return_value = 8
        mock_cpu_percent.return_value = 15.5
        
        # Mock temperature reading
        mock_entry = MagicMock()
        mock_entry.current = 45.0
        mock_temps.return_value = {'cpu_thermal': [mock_entry]}

        result = get_cpu_usage()
        
        assert result['percent'] == 15.5
        assert result['cores'] == 8
        assert result['temperature'] == 45.0
        assert result['error'] is None

def test_get_cpu_usage_failure():
    """Test get_cpu_usage handles exceptions gracefully and registers errors."""
    with patch('psutil.cpu_percent', side_effect=Exception("Hardware failure")):
        result = get_cpu_usage()
        
        assert result['percent'] == 0.0
        assert result['error'] == "Hardware failure"

def test_get_memory_usage_success():
    """Test get_memory_usage extracts stats from virtual memory correctly."""
    with patch('psutil.virtual_memory') as mock_vm:
        mock_mem = MagicMock()
        mock_mem.total = 16000000000
        mock_mem.used = 8000000000
        mock_mem.free = 8000000000
        mock_mem.percent = 50.0
        mock_vm.return_value = mock_mem

        result = get_memory_usage()
        
        assert result['total'] == 16000000000
        assert result['used'] == 8000000000
        assert result['free'] == 8000000000
        assert result['percent'] == 50.0
        assert result['error'] is None

def test_get_memory_usage_failure():
    """Test get_memory_usage gracefully returns error upon exception."""
    with patch('psutil.virtual_memory', side_effect=RuntimeError("Kernel error")):
        result = get_memory_usage()
        
        assert result['percent'] == 0.0
        assert result['error'] == "Kernel error"

def test_get_disk_usage_success():
    """Test get_disk_usage reads disk metrics properly."""
    with patch('psutil.disk_usage') as mock_disk_usage:
        mock_disk = MagicMock()
        mock_disk.total = 500000000000
        mock_disk.used = 200000000000
        mock_disk.free = 300000000000
        mock_disk.percent = 40.0
        mock_disk_usage.return_value = mock_disk

        result = get_disk_usage("/")
        
        assert result['total'] == 500000000000
        assert result['used'] == 200000000000
        assert result['free'] == 300000000000
        assert result['percent'] == 40.0
        assert result['error'] is None

def test_get_disk_usage_failure():
    """Test get_disk_usage returns clean error state if inspect partition fails."""
    with patch('psutil.disk_usage', side_effect=FileNotFoundError("Partition missing")):
        result = get_disk_usage("/invalid/path")
        
        assert result['percent'] == 0.0
        assert result['error'] == "Partition missing"
