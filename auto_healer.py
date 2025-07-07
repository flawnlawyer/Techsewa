import psutil
import os
import platform
import subprocess
from enum import Enum, auto

class ProblemType(Enum):
    NETWORK = auto()
    POWER = auto()
    CPU = auto()
    MEMORY = auto()
    STORAGE = auto()
    SOFTWARE = auto()

class AutoHealer:
    def __init__(self):
        self.healing_actions = {
            ProblemType.NETWORK: self._heal_network,
            ProblemType.POWER: self._heal_power,
            ProblemType.CPU: self._heal_cpu,
            ProblemType.MEMORY: self._heal_memory,
            ProblemType.STORAGE: self._heal_storage,
            ProblemType.SOFTWARE: self._heal_software
        }
        
    def heal(self, problem_type: ProblemType) -> bool:
        """Attempt to heal the detected problem"""
        healing_action = self.healing_actions.get(problem_type)
        if healing_action:
            return healing_action()
        return False
    
    def _heal_network(self) -> bool:
        """Attempt to fix network issues"""
        try:
            if platform.system() == "Windows":
                subprocess.run(["ipconfig", "/release"], check=True)
                subprocess.run(["ipconfig", "/renew"], check=True)
                subprocess.run(["netsh", "winsock", "reset"], check=True)
            else:
                subprocess.run(["sudo", "service", "network-manager", "restart"], check=True)
            return True
        except subprocess.CalledProcessError:
            return False
    
    def _heal_power(self) -> bool:
        """Attempt to fix power-related issues"""
        try:
            # Check battery status if on laptop
            if hasattr(psutil, "sensors_battery"):
                battery = psutil.sensors_battery()
                if battery and battery.percent < 10:
                    return False  # Critical battery level
            return True
        except:
            return False
    
    def _heal_cpu(self) -> bool:
        """Attempt to reduce CPU load"""
        try:
            # Get top 3 CPU-consuming processes
            procs = sorted(psutil.process_iter(['pid', 'name', 'cpu_percent']), 
                          key=lambda p: p.info['cpu_percent'], reverse=True)[:3]
            
            for proc in procs:
                try:
                    if proc.info['cpu_percent'] > 50:  # If process using >50% CPU
                        proc.terminate()
                except:
                    continue
            return True
        except:
            return False
    
    def _heal_memory(self) -> bool:
        """Attempt to free up memory"""
        try:
            # Clear memory cache (works differently per OS)
            if platform.system() == "Linux":
                subprocess.run(["sync"])
                subprocess.run(["echo", "3", ">", "/proc/sys/vm/drop_caches"], shell=True)
            return True
        except:
            return False
    
    def _heal_storage(self) -> bool:
        """Attempt to free up storage space"""
        try:
            # Check disk space and suggest cleanup
            if platform.system() == "Windows":
                subprocess.run(["cleanmgr", "/sagerun:1"], check=True)
            return True
        except:
            return False
    
    def _heal_software(self) -> bool:
        """Generic software issue resolution"""
        try:
            # Try restarting critical services
            if platform.system() == "Windows":
                subprocess.run(["net", "stop", "wuauserv"], check=True)
                subprocess.run(["net", "start", "wuauserv"], check=True)
            return True
        except:
            return False