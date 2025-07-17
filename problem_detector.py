import psutil
import time
import threading
import logging
from enum import Enum, auto
from typing import Callable, Dict, Any, Optional
from dataclasses import dataclass
from collections import deque
import statistics

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ProblemType(Enum):
    NETWORK = auto()
    POWER = auto()
    CPU = auto()
    MEMORY = auto()
    STORAGE = auto()
    SOFTWARE = auto()

@dataclass
class ProblemAlert:
    """Data class for problem alerts"""
    message: str
    code: int
    problem_type: ProblemType
    timestamp: float
    severity: str = "WARNING"  # WARNING, CRITICAL, INFO

class ProblemDetector:
    def __init__(self, callback: Callable[[ProblemAlert], None], check_interval: int = 10):
        """
        Initialize the problem detector.
        
        Args:
            callback: Function to call when a problem is detected
            check_interval: How often to check for problems (in seconds)
        """
        self.callback = callback
        self.check_interval = max(5, check_interval)  # Minimum 5 seconds
        self._running = False
        self._thread = None
        
        # Thresholds for problem detection
        self.thresholds = {
            ProblemType.CPU: {
                'warning': 80,
                'critical': 95,
                'sustained_duration': 30  # seconds
            },
            ProblemType.MEMORY: {
                'warning': 85,
                'critical': 95
            },
            ProblemType.STORAGE: {
                'warning': 85,
                'critical': 95
            },
            ProblemType.NETWORK: {
                'min_speed_kb': 1,  # KB/s minimum for activity detection
                'check_duration': 5  # seconds to check for activity
            },
            ProblemType.POWER: {
                'low_battery': 20,
                'critical_battery': 10
            }
        }
        
        # Historical data for trend analysis
        self._cpu_history = deque(maxlen=6)  # Last 6 measurements
        self._memory_history = deque(maxlen=3)  # Last 3 measurements
        self._network_baseline = None
        self._last_alerts = {}  # Prevent spam alerts
        self._alert_cooldown = 300  # 5 minutes cooldown between same alerts
        
    def start(self):
        """Start the problem detection thread"""
        if not self._running:
            self._running = True
            self._thread = threading.Thread(target=self._monitor, daemon=True)
            self._thread.start()
            logger.info("Problem detector started")
    
    def stop(self):
        """Stop the problem detection thread"""
        self._running = False
        if self._thread and self._thread.is_alive():
            self._thread.join(timeout=5)
        logger.info("Problem detector stopped")
    
    def update_thresholds(self, problem_type: ProblemType, **kwargs):
        """Update thresholds for a specific problem type"""
        if problem_type in self.thresholds:
            self.thresholds[problem_type].update(kwargs)
    
    def _should_alert(self, problem_type: ProblemType, code: int) -> bool:
        """Check if enough time has passed since last alert of same type"""
        key = f"{problem_type.name}_{code}"
        current_time = time.time()
        
        if key in self._last_alerts:
            if current_time - self._last_alerts[key] < self._alert_cooldown:
                return False
        
        self._last_alerts[key] = current_time
        return True
    
    def _send_alert(self, message: str, code: int, problem_type: ProblemType, severity: str = "WARNING"):
        """Send alert if cooldown period has passed"""
        if self._should_alert(problem_type, code):
            alert = ProblemAlert(
                message=message,
                code=code,
                problem_type=problem_type,
                timestamp=time.time(),
                severity=severity
            )
            try:
                self.callback(alert)
                logger.info(f"Alert sent: {message} (Code: {code})")
            except Exception as e:
                logger.error(f"Error sending alert: {e}")
    
    def _monitor(self):
        """Main monitoring loop"""
        logger.info("Starting system monitoring")
        
        while self._running:
            try:
                self._check_cpu()
                self._check_memory()
                self._check_storage()
                self._check_network()
                self._check_power()
                self._check_system_health()
                
            except Exception as e:
                logger.error(f"Error in monitoring loop: {e}")
            
            time.sleep(self.check_interval)
    
    def _check_cpu(self):
        """Check for high CPU usage with trend analysis"""
        try:
            # Get CPU usage over a short interval
            cpu_percent = psutil.cpu_percent(interval=1)
            self._cpu_history.append(cpu_percent)
            
            # Check current usage
            if cpu_percent > self.thresholds[ProblemType.CPU]['critical']:
                self._send_alert(
                    f"Critical CPU usage: {cpu_percent:.1f}%",
                    103,
                    ProblemType.CPU,
                    "CRITICAL"
                )
            elif cpu_percent > self.thresholds[ProblemType.CPU]['warning']:
                # Check if it's sustained high usage
                if len(self._cpu_history) >= 3:
                    avg_cpu = statistics.mean(list(self._cpu_history)[-3:])
                    if avg_cpu > self.thresholds[ProblemType.CPU]['warning']:
                        self._send_alert(
                            f"Sustained high CPU usage: {avg_cpu:.1f}% (current: {cpu_percent:.1f}%)",
                            103,
                            ProblemType.CPU
                        )
            
        except Exception as e:
            logger.error(f"Error checking CPU: {e}")
    
    def _check_memory(self):
        """Check for high memory usage"""
        try:
            mem = psutil.virtual_memory()
            self._memory_history.append(mem.percent)
            
            if mem.percent > self.thresholds[ProblemType.MEMORY]['critical']:
                self._send_alert(
                    f"Critical memory usage: {mem.percent:.1f}% ({mem.used // (1024**3):.1f}GB used)",
                    104,
                    ProblemType.MEMORY,
                    "CRITICAL"
                )
            elif mem.percent > self.thresholds[ProblemType.MEMORY]['warning']:
                self._send_alert(
                    f"High memory usage: {mem.percent:.1f}% ({mem.used // (1024**3):.1f}GB used)",
                    104,
                    ProblemType.MEMORY
                )
            
        except Exception as e:
            logger.error(f"Error checking memory: {e}")
    
    def _check_storage(self):
        """Check for low disk space on all mounted drives"""
        try:
            critical_drives = []
            warning_drives = []
            
            for partition in psutil.disk_partitions():
                try:
                    usage = psutil.disk_usage(partition.mountpoint)
                    
                    if usage.percent > self.thresholds[ProblemType.STORAGE]['critical']:
                        critical_drives.append({
                            'mountpoint': partition.mountpoint,
                            'percent': usage.percent,
                            'free_gb': usage.free / (1024**3)
                        })
                    elif usage.percent > self.thresholds[ProblemType.STORAGE]['warning']:
                        warning_drives.append({
                            'mountpoint': partition.mountpoint,
                            'percent': usage.percent,
                            'free_gb': usage.free / (1024**3)
                        })
                        
                except (PermissionError, OSError):
                    continue
            
            # Send alerts for critical drives
            for drive in critical_drives:
                self._send_alert(
                    f"Critical disk space on {drive['mountpoint']}: {drive['percent']:.1f}% used "
                    f"({drive['free_gb']:.1f}GB free)",
                    105,
                    ProblemType.STORAGE,
                    "CRITICAL"
                )
            
            # Send alerts for warning drives
            for drive in warning_drives:
                self._send_alert(
                    f"Low disk space on {drive['mountpoint']}: {drive['percent']:.1f}% used "
                    f"({drive['free_gb']:.1f}GB free)",
                    105,
                    ProblemType.STORAGE
                )
                
        except Exception as e:
            logger.error(f"Error checking storage: {e}")
    
    def _check_network(self):
        """Check for network connectivity and performance issues"""
        try:
            net_io = psutil.net_io_counters()
            current_time = time.time()
            
            if self._network_baseline is None:
                self._network_baseline = {
                    'bytes_sent': net_io.bytes_sent,
                    'bytes_recv': net_io.bytes_recv,
                    'timestamp': current_time
                }
                return
            
            # Calculate network activity over time
            time_diff = current_time - self._network_baseline['timestamp']
            if time_diff >= self.thresholds[ProblemType.NETWORK]['check_duration']:
                bytes_sent_diff = net_io.bytes_sent - self._network_baseline['bytes_sent']
                bytes_recv_diff = net_io.bytes_recv - self._network_baseline['bytes_recv']
                
                upload_rate = (bytes_sent_diff / time_diff) / 1024  # KB/s
                download_rate = (bytes_recv_diff / time_diff) / 1024  # KB/s
                
                # Check for network inactivity (potential connection issues)
                min_activity = self.thresholds[ProblemType.NETWORK]['min_speed_kb']
                if upload_rate < min_activity and download_rate < min_activity:
                    # Additional check: try to get network interfaces
                    interfaces = psutil.net_if_stats()
                    active_interfaces = sum(1 for interface, stats in interfaces.items() 
                                          if stats.isup and not interface.startswith(('lo', 'docker', 'veth')))
                    
                    if active_interfaces == 0:
                        self._send_alert(
                            "No active network interfaces detected",
                            101,
                            ProblemType.NETWORK,
                            "CRITICAL"
                        )
                    else:
                        self._send_alert(
                            f"Low network activity: {upload_rate:.1f}KB/s up, {download_rate:.1f}KB/s down",
                            101,
                            ProblemType.NETWORK
                        )
                
                # Update baseline
                self._network_baseline = {
                    'bytes_sent': net_io.bytes_sent,
                    'bytes_recv': net_io.bytes_recv,
                    'timestamp': current_time
                }
            
        except Exception as e:
            logger.error(f"Error checking network: {e}")
    
    def _check_power(self):
        """Check for power-related issues"""
        try:
            if not hasattr(psutil, "sensors_battery"):
                return
                
            battery = psutil.sensors_battery()
            if battery is None:
                return
                
            if battery.percent <= self.thresholds[ProblemType.POWER]['critical_battery']:
                if not battery.power_plugged:
                    self._send_alert(
                        f"Critical battery level: {battery.percent}% - System may shutdown soon",
                        102,
                        ProblemType.POWER,
                        "CRITICAL"
                    )
            elif battery.percent <= self.thresholds[ProblemType.POWER]['low_battery']:
                if not battery.power_plugged:
                    time_remaining = "Unknown"
                    if battery.secsleft != psutil.POWER_TIME_UNKNOWN:
                        hours = battery.secsleft // 3600
                        minutes = (battery.secsleft % 3600) // 60
                        time_remaining = f"{hours}h {minutes}m"
                    
                    self._send_alert(
                        f"Low battery: {battery.percent}% remaining ({time_remaining})",
                        102,
                        ProblemType.POWER
                    )
                    
        except Exception as e:
            logger.error(f"Error checking power: {e}")
    
    def _check_system_health(self):
        """Check overall system health indicators"""
        try:
            # Check system uptime
            uptime = time.time() - psutil.boot_time()
            if uptime > 30 * 24 * 3600:  # 30 days
                self._send_alert(
                    f"System uptime is {uptime / (24 * 3600):.1f} days - consider restarting",
                    106,
                    ProblemType.SOFTWARE
                )
            
            # Check for zombie processes
            zombie_count = len([p for p in psutil.process_iter(['status']) 
                              if p.info['status'] == psutil.STATUS_ZOMBIE])
            if zombie_count > 10:
                self._send_alert(
                    f"High number of zombie processes: {zombie_count}",
                    107,
                    ProblemType.SOFTWARE
                )
                
        except Exception as e:
            logger.error(f"Error checking system health: {e}")
    
    def get_system_summary(self) -> Dict[str, Any]:
        """Get current system status summary"""
        try:
            cpu_percent = psutil.cpu_percent(interval=1)
            mem = psutil.virtual_memory()
            
            # Get disk usage for root partition
            disk_usage = psutil.disk_usage('/')
            
            # Get network stats
            net_io = psutil.net_io_counters()
            
            # Get battery info if available
            battery_info = None
            if hasattr(psutil, "sensors_battery"):
                battery = psutil.sensors_battery()
                if battery:
                    battery_info = {
                        'percent': battery.percent,
                        'plugged': battery.power_plugged,
                        'time_left': battery.secsleft if battery.secsleft != psutil.POWER_TIME_UNKNOWN else None
                    }
            
            return {
                'cpu_percent': cpu_percent,
                'memory_percent': mem.percent,
                'memory_used_gb': mem.used / (1024**3),
                'memory_total_gb': mem.total / (1024**3),
                'disk_percent': disk_usage.percent,
                'disk_free_gb': disk_usage.free / (1024**3),
                'network_bytes_sent': net_io.bytes_sent,
                'network_bytes_recv': net_io.bytes_recv,
                'battery': battery_info,
                'uptime_hours': (time.time() - psutil.boot_time()) / 3600
            }
            
        except Exception as e:
            logger.error(f"Error getting system summary: {e}")
            return {}


# Example usage
if __name__ == "__main__":
    def alert_handler(alert: ProblemAlert):
        print(f"[{alert.severity}] {alert.message} (Code: {alert.code}) - {alert.problem_type.name}")
    
    detector = ProblemDetector(alert_handler, check_interval=15)
    
    try:
        detector.start()
        print("System monitoring started. Press Ctrl+C to stop...")
        
        while True:
            time.sleep(30)  # Print summary every 30 seconds
            summary = detector.get_system_summary()
            print(f"\n--- System Summary ---")
            print(f"CPU: {summary.get('cpu_percent', 0):.1f}%")
            print(f"Memory: {summary.get('memory_percent', 0):.1f}% ({summary.get('memory_used_gb', 0):.1f}GB used)")
            print(f"Disk: {summary.get('disk_percent', 0):.1f}% ({summary.get('disk_free_gb', 0):.1f}GB free)")
            if summary.get('battery'):
                battery = summary['battery']
                print(f"Battery: {battery['percent']}% ({'Plugged' if battery['plugged'] else 'Unplugged'})")
            print(f"Uptime: {summary.get('uptime_hours', 0):.1f} hours")
            
    except KeyboardInterrupt:
        detector.stop()
        print("\nMonitoring stopped.")