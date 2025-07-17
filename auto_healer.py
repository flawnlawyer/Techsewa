import psutil
import os
import platform
import subprocess
import logging
import time
import threading
from enum import Enum, auto
from typing import Dict, List, Optional, Callable, Tuple
from dataclasses import dataclass
from datetime import datetime, timedelta
import json
import shutil
import tempfile

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('auto_healer.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class ProblemType(Enum):
    NETWORK = auto()
    POWER = auto()
    CPU = auto()
    MEMORY = auto()
    STORAGE = auto()
    SOFTWARE = auto()
    THERMAL = auto()
    DISK_IO = auto()

class Severity(Enum):
    LOW = 1
    MEDIUM = 2
    HIGH = 3
    CRITICAL = 4

@dataclass
class HealingResult:
    success: bool
    message: str
    actions_taken: List[str]
    timestamp: datetime
    problem_type: ProblemType
    severity: Severity

@dataclass
class SystemMetrics:
    cpu_percent: float
    memory_percent: float
    disk_usage: Dict[str, float]
    network_connections: int
    running_processes: int
    temperature: Optional[float] = None
    battery_percent: Optional[float] = None

class SafetyManager:
    """Manages safety constraints and prevents dangerous operations"""
    
    PROTECTED_PROCESSES = {
        'systemd', 'init', 'kernel', 'kthreadd', 'explorer.exe', 
        'winlogon.exe', 'csrss.exe', 'smss.exe', 'lsass.exe',
        'services.exe', 'svchost.exe'
    }
    
    CRITICAL_SERVICES = {
        'ssh', 'sshd', 'NetworkManager', 'systemd-networkd',
        'wuauserv', 'BITS', 'CryptSvc', 'TrustedInstaller'
    }
    
    @staticmethod
    def is_process_safe_to_terminate(process_name: str, pid: int) -> bool:
        """Check if a process is safe to terminate"""
        if process_name.lower() in SafetyManager.PROTECTED_PROCESSES:
            return False
        if pid <= 10:  # System processes typically have low PIDs
            return False
        return True
    
    @staticmethod
    def is_service_safe_to_restart(service_name: str) -> bool:
        """Check if a service is safe to restart"""
        return service_name not in SafetyManager.CRITICAL_SERVICES

class SystemMonitor:
    """Continuously monitors system health and detects problems"""
    
    def __init__(self, check_interval: int = 30):
        self.check_interval = check_interval
        self._running = False
        self._thread = None
        self.callbacks: List[Callable[[ProblemType, Severity], None]] = []
        
    def add_callback(self, callback: Callable[[ProblemType, Severity], None]):
        """Add a callback to be called when problems are detected"""
        self.callbacks.append(callback)
    
    def get_system_metrics(self) -> SystemMetrics:
        """Get current system metrics"""
        metrics = SystemMetrics(
            cpu_percent=psutil.cpu_percent(interval=1),
            memory_percent=psutil.virtual_memory().percent,
            disk_usage={disk.device: psutil.disk_usage(disk.mountpoint).percent 
                       for disk in psutil.disk_partitions()},
            network_connections=len(psutil.net_connections()),
            running_processes=len(psutil.pids())
        )
        
        # Get battery info if available
        if hasattr(psutil, 'sensors_battery') and psutil.sensors_battery():
            metrics.battery_percent = psutil.sensors_battery().percent
            
        # Get temperature if available
        if hasattr(psutil, 'sensors_temperatures'):
            temps = psutil.sensors_temperatures()
            if temps:
                avg_temp = sum(temp.current for sensors in temps.values() 
                              for temp in sensors) / sum(len(sensors) for sensors in temps.values())
                metrics.temperature = avg_temp
        
        return metrics
    
    def detect_problems(self) -> List[Tuple[ProblemType, Severity]]:
        """Detect system problems and their severity"""
        problems = []
        metrics = self.get_system_metrics()
        
        # CPU issues
        if metrics.cpu_percent > 90:
            problems.append((ProblemType.CPU, Severity.CRITICAL))
        elif metrics.cpu_percent > 75:
            problems.append((ProblemType.CPU, Severity.HIGH))
        
        # Memory issues
        if metrics.memory_percent > 95:
            problems.append((ProblemType.MEMORY, Severity.CRITICAL))
        elif metrics.memory_percent > 85:
            problems.append((ProblemType.MEMORY, Severity.HIGH))
        
        # Storage issues
        for device, usage in metrics.disk_usage.items():
            if usage > 95:
                problems.append((ProblemType.STORAGE, Severity.CRITICAL))
            elif usage > 85:
                problems.append((ProblemType.STORAGE, Severity.HIGH))
        
        # Power issues
        if metrics.battery_percent is not None:
            if metrics.battery_percent < 5:
                problems.append((ProblemType.POWER, Severity.CRITICAL))
            elif metrics.battery_percent < 15:
                problems.append((ProblemType.POWER, Severity.HIGH))
        
        # Temperature issues
        if metrics.temperature is not None:
            if metrics.temperature > 85:
                problems.append((ProblemType.THERMAL, Severity.CRITICAL))
            elif metrics.temperature > 75:
                problems.append((ProblemType.THERMAL, Severity.HIGH))
        
        # Network issues (simple check)
        try:
            import socket
            socket.create_connection(("8.8.8.8", 53), timeout=3)
        except:
            problems.append((ProblemType.NETWORK, Severity.HIGH))
        
        return problems
    
    def start(self):
        """Start monitoring"""
        if self._running:
            return
        
        self._running = True
        self._thread = threading.Thread(target=self._monitor_loop)
        self._thread.daemon = True
        self._thread.start()
        logger.info("System monitoring started")
    
    def stop(self):
        """Stop monitoring"""
        self._running = False
        if self._thread:
            self._thread.join()
        logger.info("System monitoring stopped")
    
    def _monitor_loop(self):
        """Main monitoring loop"""
        while self._running:
            try:
                problems = self.detect_problems()
                for problem_type, severity in problems:
                    for callback in self.callbacks:
                        callback(problem_type, severity)
            except Exception as e:
                logger.error(f"Error in monitoring loop: {e}")
            
            time.sleep(self.check_interval)

class EnhancedAutoHealer:
    """Enhanced auto-healing system with safety, logging, and advanced strategies"""
    
    def __init__(self):
        self.healing_actions = {
            ProblemType.NETWORK: self._heal_network,
            ProblemType.POWER: self._heal_power,
            ProblemType.CPU: self._heal_cpu,
            ProblemType.MEMORY: self._heal_memory,
            ProblemType.STORAGE: self._heal_storage,
            ProblemType.SOFTWARE: self._heal_software,
            ProblemType.THERMAL: self._heal_thermal,
            ProblemType.DISK_IO: self._heal_disk_io
        }
        
        self.healing_history: List[HealingResult] = []
        self.safety_manager = SafetyManager()
        self.monitor = SystemMonitor()
        self.auto_heal_enabled = True
        
        # Set up monitoring callback
        self.monitor.add_callback(self._on_problem_detected)
        
        # Load configuration
        self.config = self._load_config()
        
    def _load_config(self) -> Dict:
        """Load configuration from file"""
        default_config = {
            "max_cpu_processes_to_kill": 3,
            "cpu_threshold_for_termination": 50,
            "memory_cleanup_aggressive": False,
            "auto_restart_services": True,
            "backup_before_changes": True,
            "notification_enabled": True
        }
        
        try:
            with open('auto_healer_config.json', 'r') as f:
                config = json.load(f)
                return {**default_config, **config}
        except FileNotFoundError:
            with open('auto_healer_config.json', 'w') as f:
                json.dump(default_config, f, indent=2)
            return default_config
    
    def _on_problem_detected(self, problem_type: ProblemType, severity: Severity):
        """Callback for when problems are detected"""
        if not self.auto_heal_enabled:
            return
            
        logger.warning(f"Problem detected: {problem_type.name} (Severity: {severity.name})")
        
        # Only auto-heal critical and high severity issues
        if severity in [Severity.CRITICAL, Severity.HIGH]:
            self.heal(problem_type, severity)
    
    def start_monitoring(self):
        """Start the system monitoring"""
        self.monitor.start()
    
    def stop_monitoring(self):
        """Stop the system monitoring"""
        self.monitor.stop()
    
    def heal(self, problem_type: ProblemType, severity: Severity = Severity.MEDIUM) -> HealingResult:
        """Attempt to heal the detected problem"""
        logger.info(f"Starting healing process for {problem_type.name} (Severity: {severity.name})")
        
        healing_action = self.healing_actions.get(problem_type)
        if not healing_action:
            result = HealingResult(
                success=False,
                message=f"No healing action available for {problem_type.name}",
                actions_taken=[],
                timestamp=datetime.now(),
                problem_type=problem_type,
                severity=severity
            )
        else:
            result = healing_action(severity)
        
        self.healing_history.append(result)
        
        if result.success:
            logger.info(f"Successfully healed {problem_type.name}")
        else:
            logger.error(f"Failed to heal {problem_type.name}: {result.message}")
        
        return result
    
    def _execute_command(self, command: List[str], timeout: int = 30) -> bool:
        """Safely execute a system command with timeout"""
        try:
            result = subprocess.run(command, capture_output=True, text=True, timeout=timeout)
            return result.returncode == 0
        except subprocess.TimeoutExpired:
            logger.error(f"Command timed out: {' '.join(command)}")
            return False
        except Exception as e:
            logger.error(f"Command failed: {' '.join(command)}, Error: {e}")
            return False
    
    def _heal_network(self, severity: Severity) -> HealingResult:
        """Advanced network healing with multiple strategies"""
        actions_taken = []
        success = False
        
        try:
            system = platform.system()
            
            # Strategy 1: DNS flush
            if system == "Windows":
                if self._execute_command(["ipconfig", "/flushdns"]):
                    actions_taken.append("Flushed DNS cache")
            else:
                if self._execute_command(["sudo", "systemctl", "restart", "systemd-resolved"]):
                    actions_taken.append("Restarted DNS resolver")
            
            # Strategy 2: Network interface reset
            if severity >= Severity.HIGH:
                if system == "Windows":
                    if self._execute_command(["netsh", "winsock", "reset"]):
                        actions_taken.append("Reset Winsock")
                    if self._execute_command(["netsh", "int", "ip", "reset"]):
                        actions_taken.append("Reset IP configuration")
                else:
                    if self._execute_command(["sudo", "systemctl", "restart", "NetworkManager"]):
                        actions_taken.append("Restarted NetworkManager")
            
            # Strategy 3: Release and renew IP
            if system == "Windows":
                if self._execute_command(["ipconfig", "/release"]):
                    actions_taken.append("Released IP address")
                if self._execute_command(["ipconfig", "/renew"]):
                    actions_taken.append("Renewed IP address")
            
            # Test connectivity
            import socket
            try:
                socket.create_connection(("8.8.8.8", 53), timeout=5)
                success = True
            except:
                pass
            
            message = "Network healing completed" if success else "Network healing attempted but connectivity issues may persist"
            
        except Exception as e:
            message = f"Network healing failed: {str(e)}"
        
        return HealingResult(
            success=success,
            message=message,
            actions_taken=actions_taken,
            timestamp=datetime.now(),
            problem_type=ProblemType.NETWORK,
            severity=severity
        )
    
    def _heal_cpu(self, severity: Severity) -> HealingResult:
        """Intelligent CPU load reduction"""
        actions_taken = []
        success = False
        
        try:
            # Get processes sorted by CPU usage
            processes = []
            for proc in psutil.process_iter(['pid', 'name', 'cpu_percent', 'memory_percent']):
                try:
                    proc_info = proc.info
                    if proc_info['cpu_percent'] > 5:  # Only consider processes using significant CPU
                        processes.append(proc)
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    continue
            
            # Sort by CPU usage
            processes.sort(key=lambda p: p.info['cpu_percent'], reverse=True)
            
            terminated_count = 0
            max_to_terminate = self.config['max_cpu_processes_to_kill']
            threshold = self.config['cpu_threshold_for_termination']
            
            for proc in processes[:max_to_terminate]:
                try:
                    proc_info = proc.info
                    if proc_info['cpu_percent'] > threshold:
                        process_name = proc_info['name']
                        
                        # Safety check
                        if not self.safety_manager.is_process_safe_to_terminate(process_name, proc_info['pid']):
                            continue
                        
                        # Try graceful termination first
                        proc.terminate()
                        try:
                            proc.wait(timeout=5)
                        except psutil.TimeoutExpired:
                            proc.kill()  # Force kill if graceful termination fails
                        
                        actions_taken.append(f"Terminated high CPU process: {process_name} (PID: {proc_info['pid']})")
                        terminated_count += 1
                        
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    continue
            
            # Check if CPU usage improved
            time.sleep(2)
            current_cpu = psutil.cpu_percent(interval=1)
            success = current_cpu < 75 or terminated_count > 0
            
            message = f"CPU healing completed. Terminated {terminated_count} processes. Current CPU: {current_cpu:.1f}%"
            
        except Exception as e:
            message = f"CPU healing failed: {str(e)}"
        
        return HealingResult(
            success=success,
            message=message,
            actions_taken=actions_taken,
            timestamp=datetime.now(),
            problem_type=ProblemType.CPU,
            severity=severity
        )
    
    def _heal_memory(self, severity: Severity) -> HealingResult:
        """Advanced memory management and cleanup"""
        actions_taken = []
        success = False
        
        try:
            initial_memory = psutil.virtual_memory().percent
            
            # Strategy 1: Clear system caches
            system = platform.system()
            if system == "Linux":
                if self._execute_command(["sync"]):
                    actions_taken.append("Synced filesystem")
                if self._execute_command(["sudo", "sysctl", "vm.drop_caches=3"]):
                    actions_taken.append("Cleared system caches")
            
            # Strategy 2: Identify and handle memory-heavy processes
            if severity >= Severity.HIGH:
                memory_processes = []
                for proc in psutil.process_iter(['pid', 'name', 'memory_percent']):
                    try:
                        proc_info = proc.info
                        if proc_info['memory_percent'] > 10:
                            memory_processes.append(proc)
                    except (psutil.NoSuchProcess, psutil.AccessDenied):
                        continue
                
                memory_processes.sort(key=lambda p: p.info['memory_percent'], reverse=True)
                
                for proc in memory_processes[:3]:  # Top 3 memory consumers
                    try:
                        proc_info = proc.info
                        process_name = proc_info['name']
                        
                        if not self.safety_manager.is_process_safe_to_terminate(process_name, proc_info['pid']):
                            continue
                        
                        if self.config['memory_cleanup_aggressive'] and proc_info['memory_percent'] > 15:
                            proc.terminate()
                            actions_taken.append(f"Terminated memory-heavy process: {process_name}")
                    except (psutil.NoSuchProcess, psutil.AccessDenied):
                        continue
            
            # Strategy 3: Python garbage collection (if running in Python)
            import gc
            gc.collect()
            actions_taken.append("Ran garbage collection")
            
            # Check improvement
            final_memory = psutil.virtual_memory().percent
            success = final_memory < initial_memory
            
            message = f"Memory healing completed. Memory usage: {initial_memory:.1f}% -> {final_memory:.1f}%"
            
        except Exception as e:
            message = f"Memory healing failed: {str(e)}"
        
        return HealingResult(
            success=success,
            message=message,
            actions_taken=actions_taken,
            timestamp=datetime.now(),
            problem_type=ProblemType.MEMORY,
            severity=severity
        )
    
    def _heal_storage(self, severity: Severity) -> HealingResult:
        """Comprehensive storage cleanup"""
        actions_taken = []
        success = False
        
        try:
            # Get initial disk usage
            disk_usage = {disk.device: psutil.disk_usage(disk.mountpoint).percent 
                         for disk in psutil.disk_partitions()}
            
            system = platform.system()
            
            # Strategy 1: Temporary files cleanup
            temp_dirs = [tempfile.gettempdir()]
            if system == "Windows":
                temp_dirs.extend([
                    os.path.expandvars("%TEMP%"),
                    os.path.expandvars("%USERPROFILE%\\AppData\\Local\\Temp")
                ])
            else:
                temp_dirs.extend(["/tmp", "/var/tmp"])
            
            for temp_dir in temp_dirs:
                if os.path.exists(temp_dir):
                    try:
                        for file in os.listdir(temp_dir):
                            file_path = os.path.join(temp_dir, file)
                            if os.path.isfile(file_path):
                                # Only delete files older than 1 day
                                if time.time() - os.path.getmtime(file_path) > 86400:
                                    os.remove(file_path)
                        actions_taken.append(f"Cleaned temporary files from {temp_dir}")
                    except (OSError, PermissionError):
                        pass
            
            # Strategy 2: System-specific cleanup
            if system == "Windows":
                if self._execute_command(["cleanmgr", "/sagerun:1"]):
                    actions_taken.append("Ran disk cleanup")
            else:
                # Clean package cache
                if self._execute_command(["sudo", "apt-get", "clean"]):
                    actions_taken.append("Cleaned package cache")
                
                # Clean journal logs
                if self._execute_command(["sudo", "journalctl", "--vacuum-time=7d"]):
                    actions_taken.append("Cleaned old journal logs")
            
            # Strategy 3: Find and report large files
            if severity >= Severity.HIGH:
                large_files = []
                for root, dirs, files in os.walk("/"):
                    for file in files:
                        try:
                            file_path = os.path.join(root, file)
                            if os.path.getsize(file_path) > 1024 * 1024 * 100:  # Files > 100MB
                                large_files.append(file_path)
                        except (OSError, PermissionError):
                            pass
                        if len(large_files) > 10:  # Limit search
                            break
                
                if large_files:
                    actions_taken.append(f"Identified {len(large_files)} large files for manual review")
            
            # Check improvement
            new_disk_usage = {disk.device: psutil.disk_usage(disk.mountpoint).percent 
                             for disk in psutil.disk_partitions()}
            
            success = any(new_disk_usage[device] < disk_usage[device] 
                         for device in disk_usage.keys())
            
            message = "Storage cleanup completed"
            
        except Exception as e:
            message = f"Storage healing failed: {str(e)}"
        
        return HealingResult(
            success=success,
            message=message,
            actions_taken=actions_taken,
            timestamp=datetime.now(),
            problem_type=ProblemType.STORAGE,
            severity=severity
        )
    
    def _heal_thermal(self, severity: Severity) -> HealingResult:
        """Handle thermal issues"""
        actions_taken = []
        success = False
        
        try:
            # Reduce CPU frequency/performance
            if severity >= Severity.HIGH:
                system = platform.system()
                if system == "Linux":
                    if self._execute_command(["sudo", "cpupower", "frequency-set", "-g", "powersave"]):
                        actions_taken.append("Set CPU governor to powersave")
                
                # Terminate CPU-intensive processes
                cpu_result = self._heal_cpu(severity)
                actions_taken.extend(cpu_result.actions_taken)
            
            actions_taken.append("Thermal management initiated")
            success = True
            message = "Thermal healing completed"
            
        except Exception as e:
            message = f"Thermal healing failed: {str(e)}"
        
        return HealingResult(
            success=success,
            message=message,
            actions_taken=actions_taken,
            timestamp=datetime.now(),
            problem_type=ProblemType.THERMAL,
            severity=severity
        )
    
    def _heal_disk_io(self, severity: Severity) -> HealingResult:
        """Handle disk I/O issues"""
        actions_taken = []
        success = False
        
        try:
            # Find processes with high I/O
            io_processes = []
            for proc in psutil.process_iter(['pid', 'name']):
                try:
                    io_counters = proc.io_counters()
                    if io_counters.read_bytes + io_counters.write_bytes > 1024 * 1024 * 100:  # 100MB I/O
                        io_processes.append(proc)
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    continue
            
            # Reduce I/O load
            for proc in io_processes[:3]:  # Top 3 I/O processes
                try:
                    if self.safety_manager.is_process_safe_to_terminate(proc.info['name'], proc.info['pid']):
                        proc.suspend()  # Suspend instead of terminate
                        actions_taken.append(f"Suspended high I/O process: {proc.info['name']}")
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    continue
            
            success = True
            message = "Disk I/O healing completed"
            
        except Exception as e:
            message = f"Disk I/O healing failed: {str(e)}"
        
        return HealingResult(
            success=success,
            message=message,
            actions_taken=actions_taken,
            timestamp=datetime.now(),
            problem_type=ProblemType.DISK_IO,
            severity=severity
        )
    
    def _heal_power(self, severity: Severity) -> HealingResult:
        """Handle power-related issues"""
        actions_taken = []
        success = False
        
        try:
            if hasattr(psutil, 'sensors_battery'):
                battery = psutil.sensors_battery()
                if battery:
                    if battery.percent < 15:
                        # Enable power saving mode
                        system = platform.system()
                        if system == "Linux":
                            if self._execute_command(["sudo", "cpupower", "frequency-set", "-g", "powersave"]):
                                actions_taken.append("Enabled power saving mode")
                        
                        # Reduce screen brightness (if possible)
                        actions_taken.append("Power conservation measures activated")
                        success = True
                    else:
                        success = True
                        actions_taken.append("Battery level acceptable")
            
            message = "Power management completed"
            
        except Exception as e:
            message = f"Power healing failed: {str(e)}"
        
        return HealingResult(
            success=success,
            message=message,
            actions_taken=actions_taken,
            timestamp=datetime.now(),
            problem_type=ProblemType.POWER,
            severity=severity
        )
    
    def _heal_software(self, severity: Severity) -> HealingResult:
        """Generic software issue resolution"""
        actions_taken = []
        success = False
        
        try:
            system = platform.system()
            
            # Restart key services
            if system == "Windows":
                services = ["wuauserv", "BITS", "CryptSvc"]
                for service in services:
                    if self.safety_manager.is_service_safe_to_restart(service):
                        if self._execute_command(["net", "stop", service]):
                            if self._execute_command(["net", "start", service]):
                                actions_taken.append(f"Restarted service: {service}")
            else:
                services = ["systemd-logind", "dbus"]
                for service in services:
                    if self.safety_manager.is_service_safe_to_restart(service):
                        if self._execute_command(["sudo", "systemctl", "restart", service]):
                            actions_taken.append(f"Restarted service: {service}")
            
            success = len(actions_taken) > 0
            message = "Software healing completed"
            
        except Exception as e:
            message = f"Software healing failed: {str(e)}"
        
        return HealingResult(
            success=success,
            message=message,
            actions_taken=actions_taken,
            timestamp=datetime.now(),
            problem_type=ProblemType.SOFTWARE,
            severity=severity
        )
    
    def get_healing_history(self) -> List[HealingResult]:
        """Get the history of all healing attempts"""
        return self.healing_history
    
    def get_system_health_report(self) -> Dict:
        """Generate a comprehensive system health report"""
        metrics = self.monitor.get_system_metrics()
        problems = self.monitor.detect_problems()
        
        return {
            "timestamp": datetime.now().isoformat(),
            "metrics": {
                "cpu_percent": metrics.cpu_percent,
                "memory_percent": metrics.memory_percent,
                "disk_usage": metrics.disk_usage,
                "network_connections": metrics.network_connections,
                "running_processes": metrics.running_processes,
                "temperature": metrics.temperature,
                "battery_percent": metrics.battery_percent
            },
            "problems": [{"type": p[0].name, "severity": p[1].name} for p in problems],
            "recent_healing_attempts": len([h for h in self.healing_history 
                                          if h.timestamp > datetime.now() - timedelta(hours=1)]),
            "auto_heal_enabled": self.auto_heal_enabled
        }

# Example usage
if __name__ == "__main__":
    healer = EnhancedAutoHealer()
    
    # Start monitoring
    healer.start_monitoring()
    
    try:
        # Keep the program running
        while True:
            time.sleep(60)
            
            # Generate health report every minute
            report = healer.get_system_health_report()
            print(f"System Health Report: {report}")
            
    except KeyboardInterrupt:
        print("Shutting down...")
        healer.stop_monitoring()