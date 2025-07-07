import platform
import psutil
import subprocess
from typing import Dict, List

class HardwareScanner:
    """Basic hardware scanning functionality"""
    
    def __init__(self):
        self.system_info = self.get_system_info()
    
    def get_system_info(self) -> Dict:
        """Get basic system hardware information"""
        return {
            'system': platform.system(),
            'processor': platform.processor(),
            'architecture': platform.architecture()[0],
            'physical_cores': psutil.cpu_count(logical=False),
            'total_cores': psutil.cpu_count(logical=True),
            'ram': round(psutil.virtual_memory().total / (1024 ** 3), 2),  # in GB
            'disks': self.get_disk_info(),
            'gpu': self.get_gpu_info()
        }
    
    def get_disk_info(self) -> List[Dict]:
        """Get information about all disks"""
        disks = []
        for partition in psutil.disk_partitions():
            usage = psutil.disk_usage(partition.mountpoint)
            disks.append({
                'device': partition.device,
                'mountpoint': partition.mountpoint,
                'total_gb': round(usage.total / (1024 ** 3), 2),
                'used_gb': round(usage.used / (1024 ** 3), 2),
                'free_gb': round(usage.free / (1024 ** 3), 2)
            })
        return disks
    
    def get_gpu_info(self) -> str:
        """Try to get GPU information"""
        try:
            if platform.system() == "Windows":
                result = subprocess.run(
                    ["wmic", "path", "win32_VideoController", "get", "name"],
                    capture_output=True, text=True
                )
                return result.stdout.strip().split('\n')[-1]
            elif platform.system() == "Linux":
                result = subprocess.run(
                    ["lspci", "|", "grep", "-i", "vga"],
                    capture_output=True, text=True, shell=True
                )
                return result.stdout.strip()
            else:
                return "Unknown GPU"
        except:
            return "GPU info unavailable"
    
    def scan_printers(self) -> List[str]:
        """Scan for connected printers"""
        try:
            if platform.system() == "Windows":
                result = subprocess.run(
                    ["wmic", "printer", "get", "name"],
                    capture_output=True, text=True
                )
                return [p.strip() for p in result.stdout.split('\n')[1:] if p.strip()]
            else:
                return ["Printer scanning not implemented for this OS"]
        except:
            return ["Printer scan failed"]