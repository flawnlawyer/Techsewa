import platform
import psutil
import subprocess
import json
import logging
import re
import socket
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, asdict
from pathlib import Path
import concurrent.futures
import time

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class CPUInfo:
    """CPU information structure"""
    name: str
    brand: str
    architecture: str
    physical_cores: int
    logical_cores: int
    base_frequency: Optional[float] = None
    max_frequency: Optional[float] = None
    cache_size: Optional[str] = None
    features: List[str] = None

@dataclass
class GPUInfo:
    """GPU information structure"""
    name: str
    vendor: str
    driver_version: Optional[str] = None
    memory_total: Optional[int] = None
    memory_used: Optional[int] = None
    temperature: Optional[float] = None

@dataclass
class DiskInfo:
    """Disk information structure"""
    device: str
    mountpoint: str
    filesystem: str
    total_gb: float
    used_gb: float
    free_gb: float
    usage_percent: float
    disk_type: str = "Unknown"
    serial_number: Optional[str] = None

@dataclass
class NetworkInterface:
    """Network interface information"""
    name: str
    display_name: str
    mac_address: str
    ip_addresses: List[str]
    is_up: bool
    speed: Optional[int] = None
    duplex: Optional[str] = None

@dataclass
class SystemInfo:
    """Complete system information"""
    hostname: str
    os_name: str
    os_version: str
    architecture: str
    boot_time: float
    uptime_seconds: float
    cpu: CPUInfo
    memory_total_gb: float
    memory_available_gb: float
    disks: List[DiskInfo]
    gpus: List[GPUInfo]
    network_interfaces: List[NetworkInterface]
    printers: List[str]
    usb_devices: List[Dict[str, str]]

class HardwareScanner:
    """Enhanced hardware scanning with cross-platform support"""
    
    def __init__(self, timeout: int = 30):
        """
        Initialize hardware scanner
        
        Args:
            timeout: Maximum time to wait for hardware detection commands
        """
        self.timeout = timeout
        self.system = platform.system()
        self.cache = {}
        self.cache_timeout = 300  # 5 minutes
        
    def _run_command(self, command: List[str], shell: bool = False, timeout: Optional[int] = None) -> Optional[str]:
        """
        Safely run a system command with timeout and error handling
        
        Args:
            command: Command to run
            shell: Whether to use shell
            timeout: Command timeout
            
        Returns:
            Command output or None if failed
        """
        try:
            result = subprocess.run(
                command,
                capture_output=True,
                text=True,
                shell=shell,
                timeout=timeout or self.timeout,
                check=False
            )
            return result.stdout.strip() if result.returncode == 0 else None
        except (subprocess.TimeoutExpired, subprocess.SubprocessError, OSError) as e:
            logger.warning(f"Command failed: {' '.join(command if isinstance(command, list) else [command])}: {e}")
            return None
    
    def _get_cached_or_compute(self, key: str, compute_func, cache_duration: int = None) -> Any:
        """Get cached result or compute and cache it"""
        cache_duration = cache_duration or self.cache_timeout
        current_time = time.time()
        
        if key in self.cache:
            cached_time, cached_value = self.cache[key]
            if current_time - cached_time < cache_duration:
                return cached_value
        
        result = compute_func()
        self.cache[key] = (current_time, result)
        return result
    
    def get_cpu_info(self) -> CPUInfo:
        """Get detailed CPU information"""
        def _compute_cpu_info():
            try:
                # Basic info from psutil
                cpu_freq = psutil.cpu_freq()
                
                cpu_info = CPUInfo(
                    name=platform.processor() or "Unknown",
                    brand=platform.processor() or "Unknown",
                    architecture=platform.architecture()[0],
                    physical_cores=psutil.cpu_count(logical=False) or 0,
                    logical_cores=psutil.cpu_count(logical=True) or 0,
                    base_frequency=cpu_freq.current if cpu_freq else None,
                    max_frequency=cpu_freq.max if cpu_freq else None,
                    features=[]
                )
                
                # Platform-specific enhancements
                if self.system == "Windows":
                    self._enhance_cpu_info_windows(cpu_info)
                elif self.system == "Linux":
                    self._enhance_cpu_info_linux(cpu_info)
                elif self.system == "Darwin":
                    self._enhance_cpu_info_macos(cpu_info)
                
                return cpu_info
                
            except Exception as e:
                logger.error(f"Error getting CPU info: {e}")
                return CPUInfo(
                    name="Unknown",
                    brand="Unknown",
                    architecture=platform.architecture()[0],
                    physical_cores=psutil.cpu_count(logical=False) or 0,
                    logical_cores=psutil.cpu_count(logical=True) or 0
                )
        
        return self._get_cached_or_compute("cpu_info", _compute_cpu_info)
    
    def _enhance_cpu_info_windows(self, cpu_info: CPUInfo):
        """Enhance CPU info on Windows"""
        try:
            # Get CPU name from wmic
            output = self._run_command(["wmic", "cpu", "get", "name", "/value"])
            if output:
                for line in output.split('\n'):
                    if line.startswith('Name='):
                        cpu_info.name = line.split('=', 1)[1].strip()
                        break
            
            # Get CPU features
            output = self._run_command(["wmic", "cpu", "get", "Description", "/value"])
            if output:
                cpu_info.features = [line.strip() for line in output.split('\n') if line.strip()]
                
        except Exception as e:
            logger.warning(f"Error enhancing Windows CPU info: {e}")
    
    def _enhance_cpu_info_linux(self, cpu_info: CPUInfo):
        """Enhance CPU info on Linux"""
        try:
            # Read from /proc/cpuinfo
            if Path("/proc/cpuinfo").exists():
                with open("/proc/cpuinfo", "r") as f:
                    content = f.read()
                    
                # Extract model name
                model_match = re.search(r'model name\s*:\s*(.+)', content)
                if model_match:
                    cpu_info.name = model_match.group(1).strip()
                
                # Extract cache size
                cache_match = re.search(r'cache size\s*:\s*(.+)', content)
                if cache_match:
                    cpu_info.cache_size = cache_match.group(1).strip()
                
                # Extract flags/features
                flags_match = re.search(r'flags\s*:\s*(.+)', content)
                if flags_match:
                    cpu_info.features = flags_match.group(1).strip().split()
                    
        except Exception as e:
            logger.warning(f"Error enhancing Linux CPU info: {e}")
    
    def _enhance_cpu_info_macos(self, cpu_info: CPUInfo):
        """Enhance CPU info on macOS"""
        try:
            # Get CPU brand
            output = self._run_command(["sysctl", "-n", "machdep.cpu.brand_string"])
            if output:
                cpu_info.name = output
                cpu_info.brand = output.split()[0] if output.split() else "Unknown"
            
            # Get CPU features
            output = self._run_command(["sysctl", "-n", "machdep.cpu.features"])
            if output:
                cpu_info.features = output.split()
                
        except Exception as e:
            logger.warning(f"Error enhancing macOS CPU info: {e}")
    
    def get_gpu_info(self) -> List[GPUInfo]:
        """Get detailed GPU information"""
        def _compute_gpu_info():
            gpus = []
            
            try:
                if self.system == "Windows":
                    gpus = self._get_gpu_info_windows()
                elif self.system == "Linux":
                    gpus = self._get_gpu_info_linux()
                elif self.system == "Darwin":
                    gpus = self._get_gpu_info_macos()
                
                return gpus if gpus else [GPUInfo(name="No GPU detected", vendor="Unknown")]
                
            except Exception as e:
                logger.error(f"Error getting GPU info: {e}")
                return [GPUInfo(name="GPU detection failed", vendor="Unknown")]
        
        return self._get_cached_or_compute("gpu_info", _compute_gpu_info)
    
    def _get_gpu_info_windows(self) -> List[GPUInfo]:
        """Get GPU info on Windows"""
        gpus = []
        try:
            output = self._run_command([
                "wmic", "path", "win32_VideoController", "get", 
                "name,AdapterRAM,DriverVersion", "/format:csv"
            ])
            
            if output:
                lines = output.strip().split('\n')[1:]  # Skip header
                for line in lines:
                    if line.strip():
                        parts = line.split(',')
                        if len(parts) >= 4:
                            gpu = GPUInfo(
                                name=parts[3].strip() if len(parts) > 3 else "Unknown",
                                vendor=self._extract_gpu_vendor(parts[3].strip() if len(parts) > 3 else ""),
                                driver_version=parts[2].strip() if len(parts) > 2 and parts[2].strip() else None,
                                memory_total=int(parts[1]) if len(parts) > 1 and parts[1].strip().isdigit() else None
                            )
                            gpus.append(gpu)
        except Exception as e:
            logger.warning(f"Error getting Windows GPU info: {e}")
        
        return gpus
    
    def _get_gpu_info_linux(self) -> List[GPUInfo]:
        """Get GPU info on Linux"""
        gpus = []
        try:
            # Try lspci first
            output = self._run_command(["lspci", "-nn"], shell=False)
            if output:
                for line in output.split('\n'):
                    if 'VGA' in line or 'Display' in line or '3D' in line:
                        gpu_name = line.split(': ', 1)[1] if ': ' in line else line
                        gpu = GPUInfo(
                            name=gpu_name.strip(),
                            vendor=self._extract_gpu_vendor(gpu_name)
                        )
                        gpus.append(gpu)
            
            # Try nvidia-smi for NVIDIA GPUs
            nvidia_output = self._run_command(["nvidia-smi", "--query-gpu=name,driver_version,memory.total,memory.used,temperature.gpu", "--format=csv,noheader,nounits"])
            if nvidia_output:
                for line in nvidia_output.split('\n'):
                    if line.strip():
                        parts = [p.strip() for p in line.split(',')]
                        if len(parts) >= 5:
                            gpu = GPUInfo(
                                name=parts[0],
                                vendor="NVIDIA",
                                driver_version=parts[1],
                                memory_total=int(parts[2]) if parts[2].isdigit() else None,
                                memory_used=int(parts[3]) if parts[3].isdigit() else None,
                                temperature=float(parts[4]) if parts[4].replace('.', '').isdigit() else None
                            )
                            # Update existing or add new
                            existing = next((g for g in gpus if g.name == gpu.name), None)
                            if existing:
                                existing.driver_version = gpu.driver_version
                                existing.memory_total = gpu.memory_total
                                existing.memory_used = gpu.memory_used
                                existing.temperature = gpu.temperature
                            else:
                                gpus.append(gpu)
                                
        except Exception as e:
            logger.warning(f"Error getting Linux GPU info: {e}")
        
        return gpus
    
    def _get_gpu_info_macos(self) -> List[GPUInfo]:
        """Get GPU info on macOS"""
        gpus = []
        try:
            output = self._run_command(["system_profiler", "SPDisplaysDataType", "-json"])
            if output:
                data = json.loads(output)
                displays = data.get('SPDisplaysDataType', [])
                
                for display in displays:
                    gpu = GPUInfo(
                        name=display.get('sppci_model', 'Unknown GPU'),
                        vendor=self._extract_gpu_vendor(display.get('sppci_model', '')),
                        memory_total=self._parse_memory_size(display.get('sppci_vram', ''))
                    )
                    gpus.append(gpu)
                    
        except Exception as e:
            logger.warning(f"Error getting macOS GPU info: {e}")
        
        return gpus
    
    def _extract_gpu_vendor(self, gpu_name: str) -> str:
        """Extract GPU vendor from name"""
        gpu_name_lower = gpu_name.lower()
        if 'nvidia' in gpu_name_lower or 'geforce' in gpu_name_lower or 'quadro' in gpu_name_lower:
            return "NVIDIA"
        elif 'amd' in gpu_name_lower or 'radeon' in gpu_name_lower:
            return "AMD"
        elif 'intel' in gpu_name_lower:
            return "Intel"
        else:
            return "Unknown"
    
    def _parse_memory_size(self, memory_str: str) -> Optional[int]:
        """Parse memory size string to MB"""
        if not memory_str:
            return None
        
        memory_str = memory_str.lower()
        if 'gb' in memory_str:
            try:
                return int(float(memory_str.replace('gb', '').strip()) * 1024)
            except ValueError:
                return None
        elif 'mb' in memory_str:
            try:
                return int(float(memory_str.replace('mb', '').strip()))
            except ValueError:
                return None
        return None
    
    def get_disk_info(self) -> List[DiskInfo]:
        """Get detailed disk information"""
        def _compute_disk_info():
            disks = []
            
            try:
                for partition in psutil.disk_partitions():
                    try:
                        usage = psutil.disk_usage(partition.mountpoint)
                        
                        disk = DiskInfo(
                            device=partition.device,
                            mountpoint=partition.mountpoint,
                            filesystem=partition.fstype,
                            total_gb=round(usage.total / (1024 ** 3), 2),
                            used_gb=round(usage.used / (1024 ** 3), 2),
                            free_gb=round(usage.free / (1024 ** 3), 2),
                            usage_percent=round((usage.used / usage.total) * 100, 1),
                            disk_type=self._get_disk_type(partition.device)
                        )
                        
                        disks.append(disk)
                        
                    except (PermissionError, OSError) as e:
                        logger.warning(f"Cannot access {partition.mountpoint}: {e}")
                        continue
                        
            except Exception as e:
                logger.error(f"Error getting disk info: {e}")
            
            return disks
        
        return self._get_cached_or_compute("disk_info", _compute_disk_info)
    
    def _get_disk_type(self, device: str) -> str:
        """Determine disk type (SSD/HDD)"""
        try:
            if self.system == "Linux":
                # Check rotational flag
                device_name = device.split('/')[-1].rstrip('0123456789')
                rotational_path = f"/sys/block/{device_name}/queue/rotational"
                
                if Path(rotational_path).exists():
                    with open(rotational_path, 'r') as f:
                        return "HDD" if f.read().strip() == "1" else "SSD"
                        
            elif self.system == "Windows":
                # Use wmic to check media type
                output = self._run_command([
                    "wmic", "diskdrive", "get", "Model,MediaType", "/format:csv"
                ])
                if output and "SSD" in output:
                    return "SSD"
                    
        except Exception as e:
            logger.warning(f"Error determining disk type for {device}: {e}")
        
        return "Unknown"
    
    def get_network_interfaces(self) -> List[NetworkInterface]:
        """Get network interface information"""
        def _compute_network_info():
            interfaces = []
            
            try:
                # Get interface statistics
                if_stats = psutil.net_if_stats()
                if_addrs = psutil.net_if_addrs()
                
                for interface_name, stats in if_stats.items():
                    # Skip loopback and virtual interfaces
                    if interface_name.startswith(('lo', 'docker', 'veth', 'br-')):
                        continue
                    
                    addresses = if_addrs.get(interface_name, [])
                    ip_addresses = []
                    mac_address = "Unknown"
                    
                    for addr in addresses:
                        if addr.family == socket.AF_INET:
                            ip_addresses.append(addr.address)
                        elif addr.family == psutil.AF_LINK:  # MAC address
                            mac_address = addr.address
                    
                    interface = NetworkInterface(
                        name=interface_name,
                        display_name=interface_name,
                        mac_address=mac_address,
                        ip_addresses=ip_addresses,
                        is_up=stats.isup,
                        speed=stats.speed if stats.speed > 0 else None,
                        duplex=stats.duplex.name if hasattr(stats.duplex, 'name') else None
                    )
                    
                    interfaces.append(interface)
                    
            except Exception as e:
                logger.error(f"Error getting network interfaces: {e}")
            
            return interfaces
        
        return self._get_cached_or_compute("network_info", _compute_network_info)
    
    def scan_printers(self) -> List[str]:
        """Scan for connected printers"""
        def _compute_printers():
            printers = []
            
            try:
                if self.system == "Windows":
                    output = self._run_command(["wmic", "printer", "get", "name", "/value"])
                    if output:
                        for line in output.split('\n'):
                            if line.startswith('Name=') and line.split('=', 1)[1].strip():
                                printers.append(line.split('=', 1)[1].strip())
                
                elif self.system == "Linux":
                    # Try CUPS
                    output = self._run_command(["lpstat", "-p"])
                    if output:
                        for line in output.split('\n'):
                            if line.startswith('printer'):
                                printer_name = line.split()[1]
                                printers.append(printer_name)
                    
                    # Try lsusb for USB printers
                    output = self._run_command(["lsusb"])
                    if output:
                        for line in output.split('\n'):
                            if any(keyword in line.lower() for keyword in ['printer', 'hewlett', 'canon', 'epson']):
                                printers.append(line.strip())
                
                elif self.system == "Darwin":
                    output = self._run_command(["lpstat", "-p"])
                    if output:
                        for line in output.split('\n'):
                            if line.startswith('printer'):
                                printer_name = line.split()[1]
                                printers.append(printer_name)
                
            except Exception as e:
                logger.warning(f"Error scanning printers: {e}")
            
            return printers if printers else ["No printers found"]
        
        return self._get_cached_or_compute("printers", _compute_printers)
    
    def get_usb_devices(self) -> List[Dict[str, str]]:
        """Get USB device information"""
        def _compute_usb_devices():
            devices = []
            
            try:
                if self.system == "Windows":
                    output = self._run_command([
                        "wmic", "path", "Win32_USBDevice", "get", 
                        "DeviceID,Description,Manufacturer", "/format:csv"
                    ])
                    if output:
                        lines = output.strip().split('\n')[1:]  # Skip header
                        for line in lines:
                            if line.strip():
                                parts = line.split(',')
                                if len(parts) >= 4:
                                    devices.append({
                                        'device_id': parts[1].strip(),
                                        'description': parts[2].strip(),
                                        'manufacturer': parts[3].strip()
                                    })
                
                elif self.system == "Linux":
                    output = self._run_command(["lsusb"])
                    if output:
                        for line in output.split('\n'):
                            if line.strip():
                                # Parse lsusb output
                                match = re.match(r'Bus \d+ Device \d+: ID ([0-9a-f:]+) (.+)', line)
                                if match:
                                    devices.append({
                                        'device_id': match.group(1),
                                        'description': match.group(2),
                                        'manufacturer': 'Unknown'
                                    })
                
                elif self.system == "Darwin":
                    output = self._run_command(["system_profiler", "SPUSBDataType", "-json"])
                    if output:
                        data = json.loads(output)
                        usb_data = data.get('SPUSBDataType', [])
                        
                        def extract_devices(items):
                            for item in items:
                                if '_name' in item:
                                    devices.append({
                                        'device_id': item.get('product_id', 'Unknown'),
                                        'description': item.get('_name', 'Unknown'),
                                        'manufacturer': item.get('manufacturer', 'Unknown')
                                    })
                                if '_items' in item:
                                    extract_devices(item['_items'])
                        
                        extract_devices(usb_data)
                
            except Exception as e:
                logger.warning(f"Error getting USB devices: {e}")
            
            return devices
        
        return self._get_cached_or_compute("usb_devices", _compute_usb_devices)
    
    def get_system_info(self) -> SystemInfo:
        """Get complete system information"""
        try:
            boot_time = psutil.boot_time()
            current_time = time.time()
            memory = psutil.virtual_memory()
            
            # Use concurrent futures to speed up data collection
            with concurrent.futures.ThreadPoolExecutor(max_workers=6) as executor:
                futures = {
                    'cpu': executor.submit(self.get_cpu_info),
                    'gpus': executor.submit(self.get_gpu_info),
                    'disks': executor.submit(self.get_disk_info),
                    'network': executor.submit(self.get_network_interfaces),
                    'printers': executor.submit(self.scan_printers),
                    'usb': executor.submit(self.get_usb_devices)
                }
                
                # Wait for all tasks to complete
                results = {}
                for key, future in futures.items():
                    try:
                        results[key] = future.result(timeout=self.timeout)
                    except Exception as e:
                        logger.error(f"Error getting {key}: {e}")
                        results[key] = [] if key != 'cpu' else CPUInfo(
                            name="Unknown", brand="Unknown", architecture="Unknown",
                            physical_cores=0, logical_cores=0
                        )
            
            return SystemInfo(
                hostname=socket.gethostname(),
                os_name=platform.system(),
                os_version=platform.release(),
                architecture=platform.architecture()[0],
                boot_time=boot_time,
                uptime_seconds=current_time - boot_time,
                cpu=results['cpu'],
                memory_total_gb=round(memory.total / (1024 ** 3), 2),
                memory_available_gb=round(memory.available / (1024 ** 3), 2),
                disks=results['disks'],
                gpus=results['gpus'],
                network_interfaces=results['network'],
                printers=results['printers'],
                usb_devices=results['usb']
            )
            
        except Exception as e:
            logger.error(f"Error getting system info: {e}")
            raise
    
    def get_system_summary(self) -> Dict[str, Any]:
        """Get a condensed system summary"""
        try:
            system_info = self.get_system_info()
            return {
                'hostname': system_info.hostname,
                'os': f"{system_info.os_name} {system_info.os_version}",
                'architecture': system_info.architecture,
                'uptime_hours': round(system_info.uptime_seconds / 3600, 1),
                'cpu_name': system_info.cpu.name,
                'cpu_cores': f"{system_info.cpu.physical_cores} physical, {system_info.cpu.logical_cores} logical",
                'memory_gb': system_info.memory_total_gb,
                'disk_count': len(system_info.disks),
                'total_disk_gb': sum(disk.total_gb for disk in system_info.disks),
                'gpu_count': len(system_info.gpus),
                'network_interfaces': len(system_info.network_interfaces),
                'printers': len(system_info.printers),
                'usb_devices': len(system_info.usb_devices)
            }
        except Exception as e:
            logger.error(f"Error getting system summary: {e}")
            return {'error': str(e)}
    
    def export_to_json(self, filename: str = None) -> str:
        """Export system information to JSON file"""
        try:
            system_info = self.get_system_info()
            data = asdict(system_info)
            
            if filename is None:
                filename = f"system_info_{int(time.time())}.json"
            
            with open(filename, 'w') as f:
                json.dump(data, f, indent=2, default=str)
            
            logger.info(f"System information exported to {filename}")
            return filename
            
        except Exception as e:
            logger.error(f"Error exporting to JSON: {e}")
            raise


# Example usage
if __name__ == "__main__":
    scanner = HardwareScanner()
    
    print("=== System Summary ===")
    summary = scanner.get_system_summary()
    for key, value in summary.items():
        print(f"{key.replace('_', ' ').title()}: {value}")
    
    print("\n=== Detailed System Information ===")
    system_info = scanner.get_system_info()
    
    print(f"\nCPU: {system_info.cpu.name}")
    print(f"Cores: {system_info.cpu.physical_cores} physical, {system_info.cpu.logical_cores} logical")
    
    print(f"\nMemory: {system_info.memory_total_gb} GB total, {system_info.memory_available_gb} GB available")
    
    print(f"\nDisks:")
    for disk in system_info.disks:
        print(f"  {disk.device} ({disk.disk_type}): {disk.total_gb} GB total, {disk.free_gb} GB free")
    
    print(f"\nGPUs:")
    for gpu in system_info.gpus:
        print(f"  {gpu.name} ({gpu.vendor})")
    
    print(f"\nNetwork Interfaces:")
    for interface in system_info.network_interfaces:
        status = "UP" if interface.is_up else "DOWN"
        print(f"  {interface.name} ({status}): {', '.join(interface.ip_addresses) if interface.ip_addresses else 'No IP'}")
    
    # Export to JSON
    try:
        filename = scanner.export_to_json()
        print(f"\nDetailed information exported to: {filename}")
    except Exception as e:
        print(f"Export failed: {e}")