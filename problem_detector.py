import psutil
import time
import threading
from enum import Enum, auto
from typing import Callable

class ProblemType(Enum):
    NETWORK = auto()
    POWER = auto()
    CPU = auto()
    MEMORY = auto()
    STORAGE = auto()
    SOFTWARE = auto()

class ProblemDetector:
    def __init__(self, callback: Callable[[str, int], None], check_interval: int = 10):
        """
        Initialize the problem detector.
        
        Args:
            callback: Function to call when a problem is detected
            check_interval: How often to check for problems (in seconds)
        """
        self.callback = callback
        self.check_interval = check_interval
        self._running = False
        self._thread = None
        
        # Thresholds for problem detection
        self.thresholds = {
            ProblemType.CPU: 90,        # CPU usage %
            ProblemType.MEMORY: 90,     # Memory usage %
            ProblemType.STORAGE: 90,    # Disk usage %
            ProblemType.NETWORK: {
                'min_upload': 10,       # KB/s
                'min_download': 10      # KB/s
            }
        }
        
    def start(self):
        """Start the problem detection thread"""
        if not self._running:
            self._running = True
            self._thread = threading.Thread(target=self._monitor, daemon=True)
            self._thread.start()
    
    def stop(self):
        """Stop the problem detection thread"""
        self._running = False
        if self._thread and self._thread.is_alive():
            self._thread.join()
    
    def _monitor(self):
        """Main monitoring loop"""
        while self._running:
            self._check_cpu()
            self._check_memory()
            self._check_storage()
            self._check_network()
            self._check_power()
            
            time.sleep(self.check_interval)
    
    def _check_cpu(self):
        """Check for high CPU usage"""
        cpu_percent = psutil.cpu_percent(interval=1)
        if cpu_percent > self.thresholds[ProblemType.CPU]:
            self.callback(f"High CPU usage: {cpu_percent}%", 103)
    
    def _check_memory(self):
        """Check for high memory usage"""
        mem = psutil.virtual_memory()
        if mem.percent > self.thresholds[ProblemType.MEMORY]:
            self.callback(f"High memory usage: {mem.percent}%", 104)
    
    def _check_storage(self):
        """Check for low disk space"""
        for part in psutil.disk_partitions():
            try:
                usage = psutil.disk_usage(part.mountpoint)
                if usage.percent > self.thresholds[ProblemType.STORAGE]:
                    self.callback(f"Low disk space on {part.mountpoint}: {usage.percent}%", 105)
            except:
                continue
    
    def _check_network(self):
        """Check for network connectivity issues"""
        net1 = psutil.net_io_counters()
        time.sleep(1)
        net2 = psutil.net_io_counters()
        
        upload = (net2.bytes_sent - net1.bytes_sent) / 1024
        download = (net2.bytes_recv - net1.bytes_recv) / 1024
        
        if upload < self.thresholds[ProblemType.NETWORK]['min_upload'] and \
           download < self.thresholds[ProblemType.NETWORK]['min_download']:
            self.callback("Network connection unstable", 101)
    
    def _check_power(self):
        """Check for power-related issues"""
        if hasattr(psutil, "sensors_battery"):
            battery = psutil.sensors_battery()
            if battery and battery.percent < 20 and not battery.power_plugged:
                self.callback(f"Low battery: {battery.percent}% remaining", 102)