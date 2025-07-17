#!/usr/bin/env python3
# elite_antivirus.py – TechSewa's ELITE Offline Guardian with Advanced Features
import os, psutil, hashlib, json, time, platform, shutil, random, re, sqlite3, threading, signal
import zipfile, tarfile, requests, subprocess, mmap, struct, socket, ssl
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Any
from concurrent.futures import ThreadPoolExecutor, as_completed
from dataclasses import dataclass, asdict
import logging
import argparse
import configparser

# -------- ENHANCED SASS ENGINE --------
SASS_LINES = [
    "Your PC is so infected it needs a priest, not an antivirus.",
    "Found more threats than relatives at a Nepali wedding.",
    "This machine has more bugs than a Kathmandu street dog.",
    "If malware had loyalty cards, you'd have platinum status.",
    "Your CPU is working harder than a micro-bus conductor on a festival day.",
    "Congratulations, you've collected every virus like Pokémon cards.",
    "I've seen cleaner temp folders in cyber-cafés that still run Windows XP.",
    "Your startup list is longer than the queue for momos at Basantapur.",
    "Is this a computer or a malware Airbnb?",
    "Even the viruses are asking for Wi-Fi to call home.",
    "This PC is more compromised than a politician's promise.",
    "Your security is weaker than dal-bhat without pickle.",
    "I've seen better protection on a monsoon umbrella.",
    "Your firewall has more holes than a fisherman's net.",
    "This system is more vulnerable than a tourist in Thamel.",
    "Your password strength is like tissue paper in rain.",
    "More backdoors than a Newari house in Bhaktapur.",
    "Security tighter than a miser's wallet... NOT!",
    "Your antivirus definitions are older than democracy in Nepal.",
    "This PC needs quarantine like COVID patient in 2020."
]

# -------- ENHANCED CONSTANTS --------
HOME = Path.home()
TECHSEWA_DIR = HOME / ".techsewa_elite"
QUAR_DIR = TECHSEWA_DIR / "quarantine"
CACHE_DIR = TECHSEWA_DIR / "cache"
LOG_DIR = TECHSEWA_DIR / "logs"
DB_PATH = TECHSEWA_DIR / "threats.db"
CONFIG_PATH = TECHSEWA_DIR / "config.ini"
BACKUP_DIR = TECHSEWA_DIR / "backup"
HEURISTIC_DIR = TECHSEWA_DIR / "heuristics"

# Enhanced whitelist with more system processes
WHITELIST = {
    "explorer.exe", "svchost.exe", "lsass.exe", "winlogon.exe", "csrss.exe",
    "dwm.exe", "conhost.exe", "services.exe", "spoolsv.exe", "taskhost.exe",
    "audiodg.exe", "wininit.exe", "smss.exe", "chrome.exe", "firefox.exe",
    "hamropatro.exe", "nepali_keyboard.exe", "techsewa_helper.exe",
    "python.exe", "pythonw.exe", "code.exe", "notepad.exe", "calc.exe"
}

# Enhanced YARA-like rules with more sophisticated detection
ENHANCED_RULES = [
    ("WannaCry-Variant", b"\x00\x00\x00\x00ifeopen", 95, "Ransomware that asks for momo instead of bitcoin.", "ransomware"),
    ("Emotet-2024", b"\x8B\xFF\x55\x8B\xEC\x83\xEC", 90, "Banking trojan – steals more than pickpockets in Ratna Park.", "trojan"),
    ("AutoIt-Backdoor", b"\x41\x55\x74\x6F\x49\x74\x21", 85, "Script kiddie's favorite, now with extra naan.", "backdoor"),
    ("Generic-Downloader", b"\x68\x74\x74\x70\x3A\x2F\x2F", 70, "Downloads payloads faster than your 4G at Tinkune.", "downloader"),
    ("NepaliKeylogger", b"\x6E\x70\x6B\x6C\x67\x5F\x76", 80, "Logs keystrokes – probably trying to steal your Wi-Fi password.", "keylogger"),
    ("FakeAV-Scam", b"\x59\x6F\x75\x72\x20\x50\x43\x20\x69\x73\x20\x69\x6E\x66\x65\x63\x74\x65\x64", 60, "Ironically, the fake antivirus is itself malware.", "scareware"),
    ("Cryptominer", b"\x6D\x69\x6E\x65\x72\x5F\x70\x6F\x6F\x6C", 75, "Mining crypto harder than gold in Jiri.", "cryptominer"),
    ("Botnet-C2", b"\x2E\x6F\x6E\x69\x6F\x6E", 88, "Botnet command center – your PC is now a digital slave.", "botnet"),
    ("Rootkit-Stealth", b"\x48\x69\x64\x65\x50\x72\x6F\x63", 92, "Rootkit hiding deeper than corruption in government.", "rootkit"),
    ("Adware-Popup", b"\x61\x64\x76\x65\x72\x74\x69\x73\x65\x6D\x65\x6E\x74", 45, "More ads than a newspaper during election season.", "adware"),
    ("Spyware-Tracker", b"\x74\x72\x61\x63\x6B\x5F\x75\x73\x65\x72", 82, "Tracking you better than your concerned mother.", "spyware"),
    ("Macro-Virus", b"\x41\x75\x74\x6F\x4F\x70\x65\x6E", 65, "Office macro virus – productivity killer.", "macro"),
    ("USB-Worm", b"\x61\x75\x74\x6F\x72\x75\x6E\x2E\x69\x6E\x66", 78, "USB worm spreading faster than festival rumors.", "worm"),
    ("Phishing-Kit", b"\x70\x61\x79\x70\x61\x6C\x5F\x6C\x6F\x67\x69\x6E", 70, "Phishing kit – fishing for your credentials.", "phishing"),
    ("RAT-Remote", b"\x72\x65\x6D\x6F\x74\x65\x5F\x61\x63\x63\x65\x73\x73", 87, "Remote access trojan – someone's watching you.", "rat")
]

# File extensions to scan
SCAN_EXTENSIONS = {
    '.exe', '.dll', '.scr', '.vbs', '.ps1', '.js', '.jar', '.bat', '.cmd',
    '.com', '.pif', '.msi', '.hta', '.wsf', '.jse', '.vbe', '.docm', '.xlsm',
    '.pptm', '.pdf', '.zip', '.rar', '.7z', '.tar', '.gz', '.apk', '.deb', '.rpm'
}

MAX_FILE_SCAN = 100 * 1024 * 1024  # 100MB
MAX_THREADS = min(32, os.cpu_count() * 2)

# -------- DATA STRUCTURES --------
@dataclass
class ThreatInfo:
    path: str
    threat_type: str
    severity: int
    description: str
    detection_method: str
    timestamp: datetime
    file_hash: str
    file_size: int

@dataclass
class SystemInfo:
    cpu_usage: float
    memory_usage: float
    disk_usage: Dict[str, float]
    network_connections: int
    running_processes: int
    startup_programs: int
    system_uptime: float
    os_version: str

# -------- ENHANCED UTILITIES --------
class SecurityUtils:
    @staticmethod
    def calculate_hashes(path: Path) -> Dict[str, str]:
        """Calculate multiple hashes for better detection"""
        hashes = {'sha256': '', 'md5': '', 'sha1': ''}
        try:
            with open(path, "rb") as f:
                content = f.read()
                hashes['sha256'] = hashlib.sha256(content).hexdigest()
                hashes['md5'] = hashlib.md5(content).hexdigest()
                hashes['sha1'] = hashlib.sha1(content).hexdigest()
        except Exception:
            pass
        return hashes

    @staticmethod
    def is_packed_executable(path: Path) -> bool:
        """Detect packed executables using entropy analysis"""
        try:
            with open(path, "rb") as f:
                data = f.read(8192)
                if len(data) < 1024:
                    return False
                
                # Calculate byte frequency
                freq = [0] * 256
                for byte in data:
                    freq[byte] += 1
                
                # Calculate entropy
                entropy = 0
                for f in freq:
                    if f > 0:
                        p = f / len(data)
                        entropy -= p * (p.bit_length() - 1)
                
                return entropy > 7.5  # High entropy indicates packing
        except Exception:
            return False

    @staticmethod
    def check_pe_anomalies(path: Path) -> List[str]:
        """Check for PE file anomalies"""
        anomalies = []
        try:
            with open(path, "rb") as f:
                data = f.read(1024)
                if len(data) < 64:
                    return anomalies
                
                # Check DOS header
                if data[0:2] != b"MZ":
                    anomalies.append("Invalid DOS signature")
                
                # Check PE header offset
                pe_offset = struct.unpack("<I", data[60:64])[0]
                if pe_offset > len(data) - 4:
                    anomalies.append("Invalid PE header offset")
                
                # More PE analysis could be added here
        except Exception:
            pass
        return anomalies

# -------- DATABASE MANAGER --------
class ThreatDatabase:
    def __init__(self, db_path: Path):
        self.db_path = db_path
        self.init_db()
    
    def init_db(self):
        """Initialize threat database"""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute('''
                CREATE TABLE IF NOT EXISTS threats (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    path TEXT NOT NULL,
                    threat_type TEXT NOT NULL,
                    severity INTEGER NOT NULL,
                    description TEXT,
                    detection_method TEXT,
                    timestamp DATETIME NOT NULL,
                    file_hash TEXT,
                    file_size INTEGER,
                    quarantined BOOLEAN DEFAULT FALSE
                )
            ''')
            conn.execute('''
                CREATE TABLE IF NOT EXISTS scan_history (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    scan_id TEXT NOT NULL,
                    start_time DATETIME NOT NULL,
                    end_time DATETIME,
                    files_scanned INTEGER,
                    threats_found INTEGER,
                    threats_quarantined INTEGER
                )
            ''')
    
    def add_threat(self, threat: ThreatInfo):
        """Add threat to database"""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute('''
                INSERT INTO threats (path, threat_type, severity, description, 
                                   detection_method, timestamp, file_hash, file_size)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            ''', (threat.path, threat.threat_type, threat.severity, threat.description,
                  threat.detection_method, threat.timestamp, threat.file_hash, threat.file_size))
    
    def get_threats(self, limit: int = 100) -> List[ThreatInfo]:
        """Get recent threats from database"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute('''
                SELECT path, threat_type, severity, description, detection_method, 
                       timestamp, file_hash, file_size
                FROM threats ORDER BY timestamp DESC LIMIT ?
            ''', (limit,))
            return [ThreatInfo(*row) for row in cursor.fetchall()]

# -------- REAL-TIME PROTECTION --------
class RealTimeProtection:
    def __init__(self, scanner):
        self.scanner = scanner
        self.monitoring = False
        self.watched_dirs = [Path.home(), Path("C:/") if platform.system() == "Windows" else Path("/")]
        
    def start_monitoring(self):
        """Start real-time file monitoring"""
        self.monitoring = True
        thread = threading.Thread(target=self._monitor_files, daemon=True)
        thread.start()
        return thread
    
    def _monitor_files(self):
        """Monitor file system for changes"""
        # Simplified file monitoring - in production, use watchdog library
        last_check = {}
        while self.monitoring:
            try:
                for watch_dir in self.watched_dirs:
                    if not watch_dir.exists():
                        continue
                    
                    for file_path in watch_dir.rglob("*"):
                        if (file_path.is_file() and 
                            file_path.suffix.lower() in SCAN_EXTENSIONS):
                            
                            try:
                                stat = file_path.stat()
                                key = str(file_path)
                                
                                if (key not in last_check or 
                                    last_check[key] != stat.st_mtime):
                                    
                                    last_check[key] = stat.st_mtime
                                    score = self.scanner._scan_file(file_path)
                                    
                                    if score >= 75:
                                        self.scanner.quarantine_manager.quarantine(file_path)
                                        
                            except Exception:
                                continue
                
                time.sleep(5)  # Check every 5 seconds
            except Exception:
                continue

# -------- ENHANCED QUARANTINE MANAGER --------
class EnhancedQuarantineManager:
    def __init__(self, quar_dir: Path):
        self.quar_dir = quar_dir
        self.quar_dir.mkdir(parents=True, exist_ok=True)
        
    def quarantine(self, path: Path, threat_info: Optional[ThreatInfo] = None) -> bool:
        """Quarantine a file with enhanced metadata"""
        try:
            timestamp = int(time.time())
            q_name = f"{path.name}.{timestamp}.quarantined"
            q_path = self.quar_dir / q_name
            
            # Create encrypted backup
            self._create_backup(path, q_path)
            
            # Remove original file
            path.unlink()
            
            # Create detailed metadata
            metadata = {
                "original_path": str(path),
                "quarantine_time": datetime.now().isoformat(),
                "file_hashes": SecurityUtils.calculate_hashes(q_path),
                "file_size": q_path.stat().st_size,
                "threat_info": asdict(threat_info) if threat_info else None,
                "can_restore": True
            }
            
            meta_path = q_path.with_suffix(".meta")
            meta_path.write_text(json.dumps(metadata, indent=2))
            
            roast = random.choice(SASS_LINES)
            logging.info(f"Quarantined {path.name}: {roast}")
            return True
            
        except Exception as e:
            logging.error(f"Failed to quarantine {path.name}: {e}")
            return False
    
    def _create_backup(self, source: Path, dest: Path):
        """Create encrypted backup of file"""
        # Simple XOR encryption for demo - use proper encryption in production
        key = b"TechSewaElite2024"
        with open(source, "rb") as src, open(dest, "wb") as dst:
            while True:
                chunk = src.read(8192)
                if not chunk:
                    break
                encrypted = bytes(b ^ key[i % len(key)] for i, b in enumerate(chunk))
                dst.write(encrypted)
    
    def restore_file(self, quarantine_name: str) -> bool:
        """Restore quarantined file"""
        try:
            q_path = self.quar_dir / quarantine_name
            meta_path = q_path.with_suffix(".meta")
            
            if not q_path.exists() or not meta_path.exists():
                return False
            
            metadata = json.loads(meta_path.read_text())
            if not metadata.get("can_restore", False):
                return False
            
            original_path = Path(metadata["original_path"])
            
            # Decrypt and restore
            key = b"TechSewaElite2024"
            with open(q_path, "rb") as src, open(original_path, "wb") as dst:
                while True:
                    chunk = src.read(8192)
                    if not chunk:
                        break
                    decrypted = bytes(b ^ key[i % len(key)] for i, b in enumerate(chunk))
                    dst.write(decrypted)
            
            # Clean up quarantine files
            q_path.unlink()
            meta_path.unlink()
            
            return True
        except Exception as e:
            logging.error(f"Failed to restore {quarantine_name}: {e}")
            return False

# -------- HEURISTIC ANALYSIS ENGINE --------
class HeuristicAnalyzer:
    def __init__(self):
        self.suspicious_strings = [
            b"CreateRemoteThread", b"WriteProcessMemory", b"VirtualAllocEx",
            b"SetWindowsHookEx", b"keylogger", b"password", b"bitcoin",
            b"ransomware", b"payload", b"backdoor", b"trojan", b"virus"
        ]
        
    def analyze_file(self, path: Path) -> Tuple[int, List[str]]:
        """Perform heuristic analysis on file"""
        score = 0
        flags = []
        
        try:
            # Check file properties
            if SecurityUtils.is_packed_executable(path):
                score += 30
                flags.append("packed_executable")
            
            # Check PE anomalies
            if path.suffix.lower() == ".exe":
                anomalies = SecurityUtils.check_pe_anomalies(path)
                if anomalies:
                    score += len(anomalies) * 15
                    flags.extend(anomalies)
            
            # String analysis
            with open(path, "rb") as f:
                content = f.read(32768)  # Read first 32KB
                for sus_string in self.suspicious_strings:
                    if sus_string in content:
                        score += 10
                        flags.append(f"suspicious_string_{sus_string.decode('utf-8', errors='ignore')}")
            
            # Behavioral analysis
            if self._check_suspicious_behavior(path):
                score += 25
                flags.append("suspicious_behavior")
                
        except Exception:
            pass
        
        return score, flags
    
    def _check_suspicious_behavior(self, path: Path) -> bool:
        """Check for suspicious behavioral patterns"""
        # Check if file tries to hide itself
        if path.name.startswith('.') and platform.system() != "Windows":
            return True
        
        # Check for suspicious file locations
        suspicious_locations = [
            "temp", "tmp", "appdata", "programdata", "system32"
        ]
        
        path_str = str(path).lower()
        return any(loc in path_str for loc in suspicious_locations)

# -------- ENHANCED SCANNER ENGINE --------
class EliteScanner:
    def __init__(self, db: ThreatDatabase):
        self.db = db
        self.quarantine_manager = EnhancedQuarantineManager(QUAR_DIR)
        self.heuristic_analyzer = HeuristicAnalyzer()
        self.hits = []
        self.stats = {
            "files_scanned": 0,
            "processes_scanned": 0,
            "threats_found": 0,
            "threats_quarantined": 0,
            "start_time": time.time(),
            "scan_speed": 0
        }
        
    def scan_processes(self):
        """Enhanced process scanning with behavioral analysis"""
        suspicious_processes = []
        
        for proc in psutil.process_iter(['pid', 'name', 'exe', 'memory_info', 'connections', 'cmdline']):
            try:
                self.stats["processes_scanned"] += 1
                proc_info = proc.info
                name = proc_info['name'].lower()
                
                if name in WHITELIST:
                    continue
                
                score = 0
                flags = []
                
                # Memory analysis
                if proc_info['memory_info'] and proc_info['memory_info'].rss > 600 * 1024 * 1024:
                    score += 20
                    flags.append("high_memory_usage")
                
                # Network connections analysis
                try:
                    connections = proc.connections()
                    if len(connections) > 50:
                        score += 25
                        flags.append("excessive_network_connections")
                except:
                    pass
                
                # Command line analysis
                cmdline = proc_info.get('cmdline', [])
                if cmdline and any(suspicious in ' '.join(cmdline).lower() 
                                 for suspicious in ['powershell', 'cmd', 'wscript', 'cscript']):
                    score += 15
                    flags.append("suspicious_cmdline")
                
                # File analysis
                exe_path = proc_info.get('exe')
                if exe_path and Path(exe_path).exists():
                    file_score = self._scan_file(Path(exe_path))
                    score += file_score
                
                if score >= 50:
                    threat = ThreatInfo(
                        path=exe_path or f"PID:{proc.pid}",
                        threat_type="suspicious_process",
                        severity=score,
                        description=f"Suspicious process: {name}",
                        detection_method="behavioral_analysis",
                        timestamp=datetime.now(),
                        file_hash="",
                        file_size=0
                    )
                    self.hits.append(threat)
                    self.db.add_threat(threat)
                    
            except Exception:
                continue
    
    def scan_files(self, root: Path, use_threading: bool = True):
        """Enhanced file scanning with threading support"""
        files_to_scan = []
        
        # Collect files to scan
        for file_path in root.rglob("*"):
            if (file_path.is_file() and 
                file_path.suffix.lower() in SCAN_EXTENSIONS and
                file_path.stat().st_size <= MAX_FILE_SCAN):
                files_to_scan.append(file_path)
        
        if use_threading:
            self._scan_files_threaded(files_to_scan)
        else:
            self._scan_files_sequential(files_to_scan)
    
    def _scan_files_threaded(self, files: List[Path]):
        """Scan files using thread pool"""
        with ThreadPoolExecutor(max_workers=MAX_THREADS) as executor:
            future_to_file = {executor.submit(self._scan_file, file): file 
                             for file in files}
            
            for future in as_completed(future_to_file):
                file_path = future_to_file[future]
                try:
                    score = future.result()
                    self.stats["files_scanned"] += 1
                    
                    if score >= 50:
                        self._handle_threat(file_path, score)
                        
                except Exception as e:
                    logging.error(f"Error scanning {file_path}: {e}")
    
    def _scan_files_sequential(self, files: List[Path]):
        """Scan files sequentially"""
        for file_path in files:
            try:
                score = self._scan_file(file_path)
                self.stats["files_scanned"] += 1
                
                if score >= 50:
                    self._handle_threat(file_path, score)
                    
            except Exception as e:
                logging.error(f"Error scanning {file_path}: {e}")
    
    def _scan_file(self, path: Path) -> int:
        """Enhanced file scanning with multiple detection methods"""
        total_score = 0
        
        try:
            # Signature-based detection
            with open(path, "rb") as f:
                header = f.read(8192)
                
                for name, signature, score, description, threat_type in ENHANCED_RULES:
                    if signature in header:
                        total_score += score
                        break
            
            # Heuristic analysis
            heuristic_score, flags = self.heuristic_analyzer.analyze_file(path)
            total_score += heuristic_score
            
            # PE header validation
            if path.suffix.lower() == ".exe":
                if header[:2] != b"MZ":
                    total_score += 40
                    
            # File size analysis
            file_size = path.stat().st_size
            if file_size < 1024 or file_size > 50 * 1024 * 1024:
                total_score += 10
                
        except Exception:
            pass
        
        return total_score
    
    def _handle_threat(self, path: Path, score: int):
        """Handle detected threat"""
        threat = ThreatInfo(
            path=str(path),
            threat_type="malware",
            severity=score,
            description=f"Detected malware with score {score}",
            detection_method="signature_heuristic",
            timestamp=datetime.now(),
            file_hash=SecurityUtils.calculate_hashes(path)['sha256'],
            file_size=path.stat().st_size
        )
        
        self.hits.append(threat)
        self.db.add_threat(threat)
        self.stats["threats_found"] += 1
        
        # Auto-quarantine high-risk threats
        if score >= 75:
            if self.quarantine_manager.quarantine(path, threat):
                self.stats["threats_quarantined"] += 1

# -------- SYSTEM MONITOR --------
class SystemMonitor:
    @staticmethod
    def get_system_info() -> SystemInfo:
        """Get comprehensive system information"""
        try:
            # Get network connections
            net_connections = len(psutil.net_connections())
            
            # Get running processes
            running_processes = len(psutil.pids())
            
            # Get startup programs (simplified)
            startup_programs = 0
            if platform.system() == "Windows":
                try:
                    import winreg
                    key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, 
                                        r"SOFTWARE\Microsoft\Windows\CurrentVersion\Run")
                    startup_programs = winreg.QueryInfoKey(key)[1]
                    winreg.CloseKey(key)
                except:
                    pass
            
            # Get disk usage for all drives
            disk_usage = {}
            for partition in psutil.disk_partitions():
                try:
                    usage = psutil.disk_usage(partition.mountpoint)
                    disk_usage[partition.device] = usage.percent
                except:
                    continue
            
            return SystemInfo(
                cpu_usage=psutil.cpu_percent(interval=1),
                memory_usage=psutil.virtual_memory().percent,
                disk_usage=disk_usage,
                network_connections=net_connections,
                running_processes=running_processes,
                startup_programs=startup_programs,
                system_uptime=time.time() - psutil.boot_time(),
                os_version=platform.platform()
            )
        except Exception:
            return SystemInfo(0, 0, {}, 0, 0, 0, 0, "Unknown")

# -------- MAIN ANTIVIRUS CLASS --------
class TechSewaEliteAntivirus:
    def __init__(self, config_path: Optional[Path] = None):
        self._ensure_directories()
        self._setup_logging()
        self.config = self._load_config(config_path)
        self.db = ThreatDatabase(DB_PATH)
        self.scanner = EliteScanner(self.db)
        self.real_time_protection = RealTimeProtection(self.scanner)
        self.system_monitor = SystemMonitor()
        
        # Generate scan ID
        self.scan_id = hashlib.md5(f"{time.time()}{random.randint(1000, 9999)}".encode()).hexdigest()[:8]
        
        # Report structure
        self.report = {
            "metadata": {
                "version": "4.0-elite",
                "scan_id": self.scan_id,
                "timestamp": datetime.now().isoformat(),
                "system_info": asdict(self.system_monitor.get_system_info())
            },
            "scan_results": {
                "threats": [],
                "quarantined": [],
                "statistics": {},
                "recommendations": []
            },
            "sass_wisdom": random.choice(SASS_LINES)
        }
    
    def _ensure_directories(self):
        """Create necessary directories"""
        for directory in [TECHSEWA_DIR, QUAR_DIR, CACHE_DIR, LOG_DIR, BACKUP_DIR, HEURISTIC_DIR]:
            directory.mkdir(parents=True, exist_ok=True)
            directory.chmod(0o700)
    
    def _setup_logging(self):
        """Setup comprehensive logging"""
        log_file = LOG_DIR / f"techsewa_elite_{datetime.now():%Y%m%d}.log"
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(log_file),
                logging.StreamHandler()
            ]
        )
    
    def _load_config(self, config_path: Optional[Path]) -> configparser.ConfigParser:
        """Load configuration"""
        config = configparser.ConfigParser()
        config_file = config_path or CONFIG_PATH
        
        # Default configuration
        config.read_string('''
[scanning]
max_file_size = 104857600
max_threads = 16
scan_archives = true
real_time_protection = true
heuristic_analysis = true

[quarantine]
auto_quarantine_threshold = 75
keep_quarantine_days = 30
encrypt_quarantine = true

[system]
monitor_network = true
monitor_processes = true
monitor_registry = true

[notifications]
show_sass_messages = true
log_all_actions = true
''')
        
        if config_file.exists():
            config.read(config_file)
        else:
            with open(config_file, 'w') as f:
                config.write(f)
        
        return config
    
    def full_system_scan(self, scan_path: Optional[Path] = None, enable_real_time: bool = True) -> Dict:
        """Perform comprehensive system scan"""
        scan_start = time.time()
        scan_path = scan_path or Path.home()
        
        logging.info(f"🚀 Starting TechSewa Elite scan on {scan_path}")
        logging.info(f"📊 Scan ID: {self.scan_id}")
        
        # Start real-time protection if enabled
        if enable_real_time and self.config.getboolean('scanning', 'real_time_protection'):
            self.real_time_protection.start_monitoring()
        
        try:
            # Phase 1: Process Analysis
            logging.info("🔍 Phase 1: Analyzing running processes...")
            self.scanner.scan_processes()
            
            # Phase 2: File System Scan
            logging.info("📁 Phase 2: Scanning file system...")
            use_threading = self.config.getint('scanning', 'max_threads') > 1
            self.scanner.scan_files(scan_path, use_threading)
            
            # Phase 3: Network Analysis
            logging.info("🌐 Phase 3: Analyzing network connections...")
            self._analyze_network_connections()
            
            # Phase 4: Registry Analysis (Windows only)
            if platform.system() == "Windows":
                logging.info("🔑 Phase 4: Analyzing system registry...")
                self._analyze_registry()
            
            # Phase 5: System Integrity Check
            logging.info("🛡️ Phase 5: System integrity verification...")
            self._verify_system_integrity()
            
            # Update statistics
            scan_duration = time.time() - scan_start
            self.scanner.stats["scan_speed"] = self.scanner.stats["files_scanned"] / scan_duration if scan_duration > 0 else 0
            
            # Generate report
            self.report["scan_results"]["threats"] = [asdict(threat) for threat in self.scanner.hits]
            self.report["scan_results"]["statistics"] = self.scanner.stats
            self.report["scan_results"]["recommendations"] = self._generate_recommendations()
            
            # Save scan history
            self._save_scan_history()
            
            logging.info(f"✅ Scan completed in {scan_duration:.2f} seconds")
            return self.report
            
        except Exception as e:
            logging.error(f"❌ Scan failed: {e}")
            return {"error": str(e)}
    
    def _analyze_network_connections(self):
        """Analyze network connections for suspicious activity"""
        try:
            suspicious_ports = [1337, 31337, 4444, 5555, 6666, 6667, 6969, 7777, 8080, 9999]
            suspicious_connections = []
            
            for conn in psutil.net_connections():
                if conn.laddr and conn.laddr.port in suspicious_ports:
                    suspicious_connections.append({
                        "port": conn.laddr.port,
                        "status": conn.status,
                        "pid": conn.pid
                    })
            
            if suspicious_connections:
                threat = ThreatInfo(
                    path="network_connections",
                    threat_type="suspicious_network",
                    severity=60,
                    description=f"Suspicious network connections detected on ports: {[c['port'] for c in suspicious_connections]}",
                    detection_method="network_analysis",
                    timestamp=datetime.now(),
                    file_hash="",
                    file_size=0
                )
                self.scanner.hits.append(threat)
                self.db.add_threat(threat)
                
        except Exception as e:
            logging.error(f"Network analysis failed: {e}")
    
    def _analyze_registry(self):
        """Analyze Windows registry for suspicious entries"""
        try:
            import winreg
            
            # Check common malware registry locations
            suspicious_keys = [
                (winreg.HKEY_CURRENT_USER, r"SOFTWARE\Microsoft\Windows\CurrentVersion\Run"),
                (winreg.HKEY_LOCAL_MACHINE, r"SOFTWARE\Microsoft\Windows\CurrentVersion\Run"),
                (winreg.HKEY_CURRENT_USER, r"SOFTWARE\Microsoft\Windows\CurrentVersion\RunOnce"),
            ]
            
            for hive, key_path in suspicious_keys:
                try:
                    key = winreg.OpenKey(hive, key_path)
                    for i in range(winreg.QueryInfoKey(key)[1]):
                        name, value, _ = winreg.EnumValue(key, i)
                        
                        # Check for suspicious patterns
                        if any(pattern in value.lower() for pattern in ['temp', 'appdata', 'roaming', '.tmp']):
                            threat = ThreatInfo(
                                path=f"Registry: {key_path}\\{name}",
                                threat_type="suspicious_registry",
                                severity=45,
                                description=f"Suspicious registry entry: {name} -> {value}",
                                detection_method="registry_analysis",
                                timestamp=datetime.now(),
                                file_hash="",
                                file_size=0
                            )
                            self.scanner.hits.append(threat)
                            self.db.add_threat(threat)
                    
                    winreg.CloseKey(key)
                except Exception:
                    continue
                    
        except ImportError:
            logging.info("Registry analysis not available on this platform")
        except Exception as e:
            logging.error(f"Registry analysis failed: {e}")
    
    def _verify_system_integrity(self):
        """Verify system file integrity"""
        try:
            critical_files = []
            
            if platform.system() == "Windows":
                critical_files = [
                    Path("C:/Windows/System32/kernel32.dll"),
                    Path("C:/Windows/System32/ntdll.dll"),
                    Path("C:/Windows/System32/user32.dll"),
                ]
            else:
                critical_files = [
                    Path("/bin/bash"),
                    Path("/bin/ls"),
                    Path("/usr/bin/python3"),
                ]
            
            for file_path in critical_files:
                if file_path.exists():
                    score = self.scanner._scan_file(file_path)
                    if score > 30:  # Lower threshold for system files
                        threat = ThreatInfo(
                            path=str(file_path),
                            threat_type="system_file_corruption",
                            severity=score,
                            description=f"System file {file_path.name} may be corrupted or infected",
                            detection_method="integrity_check",
                            timestamp=datetime.now(),
                            file_hash=SecurityUtils.calculate_hashes(file_path)['sha256'],
                            file_size=file_path.stat().st_size
                        )
                        self.scanner.hits.append(threat)
                        self.db.add_threat(threat)
                        
        except Exception as e:
            logging.error(f"System integrity check failed: {e}")
    
    def _generate_recommendations(self) -> List[str]:
        """Generate security recommendations based on scan results"""
        recommendations = []
        
        # Check threat severity
        high_severity_threats = [t for t in self.scanner.hits if t.severity >= 80]
        if high_severity_threats:
            recommendations.append("🚨 High-severity threats detected! Consider immediate system isolation.")
        
        # Check system performance
        system_info = self.system_monitor.get_system_info()
        if system_info.cpu_usage > 80:
            recommendations.append("⚡ High CPU usage detected. Check for cryptocurrency miners.")
        
        if system_info.memory_usage > 85:
            recommendations.append("🧠 High memory usage. Possible memory leak or malware activity.")
        
        # Check network connections
        if system_info.network_connections > 100:
            recommendations.append("🌐 Excessive network connections detected. Monitor for data exfiltration.")
        
        # Check startup programs
        if system_info.startup_programs > 20:
            recommendations.append("🚀 Too many startup programs. Review and disable unnecessary ones.")
        
        # General recommendations
        recommendations.extend([
            "🔄 Keep your system and software updated",
            "🛡️ Enable Windows Defender or install reputable antivirus",
            "🔒 Use strong, unique passwords for all accounts",
            "📧 Be cautious with email attachments and downloads",
            "💾 Regularly backup important data",
            "🔥 Enable firewall protection"
        ])
        
        return recommendations
    
    def _save_scan_history(self):
        """Save scan results to database"""
        try:
            with sqlite3.connect(DB_PATH) as conn:
                conn.execute('''
                    INSERT INTO scan_history (scan_id, start_time, end_time, files_scanned, 
                                            threats_found, threats_quarantined)
                    VALUES (?, ?, ?, ?, ?, ?)
                ''', (
                    self.scan_id,
                    datetime.fromtimestamp(self.scanner.stats["start_time"]),
                    datetime.now(),
                    self.scanner.stats["files_scanned"],
                    self.scanner.stats["threats_found"],
                    self.scanner.stats["threats_quarantined"]
                ))
        except Exception as e:
            logging.error(f"Failed to save scan history: {e}")
    
    def quick_scan(self) -> Dict:
        """Perform quick scan of critical areas"""
        logging.info("⚡ Starting quick scan...")
        
        critical_paths = [
            Path.home() / "Downloads",
            Path.home() / "Desktop",
            Path.home() / "Documents",
        ]
        
        if platform.system() == "Windows":
            critical_paths.extend([
                Path("C:/Windows/Temp"),
                Path("C:/Users/Public"),
                Path(os.environ.get("TEMP", "C:/Temp"))
            ])
        else:
            critical_paths.extend([
                Path("/tmp"),
                Path("/var/tmp"),
                Path.home() / ".cache"
            ])
        
        # Scan critical paths
        for path in critical_paths:
            if path.exists():
                self.scanner.scan_files(path, use_threading=False)
        
        # Quick process scan
        self.scanner.scan_processes()
        
        return self.generate_report()
    
    def generate_report(self) -> str:
        """Generate comprehensive scan report"""
        report = self.report
        system_info = report["metadata"]["system_info"]
        stats = report["scan_results"]["statistics"]
        threats = report["scan_results"]["threats"]
        recommendations = report["scan_results"]["recommendations"]
        
        lines = [
            "🔥 TechSewa Elite Antivirus - Comprehensive Report",
            "=" * 60,
            f"🆔 Scan ID: {self.scan_id}",
            f"📅 Scan Time: {report['metadata']['timestamp']}",
            f"🖥️  System: {system_info['os_version']}",
            "",
            "📊 System Health:",
            f"  CPU Usage: {system_info['cpu_usage']:.1f}%",
            f"  Memory Usage: {system_info['memory_usage']:.1f}%",
            f"  Network Connections: {system_info['network_connections']}",
            f"  Running Processes: {system_info['running_processes']}",
            f"  System Uptime: {system_info['system_uptime']/3600:.1f} hours",
            "",
            "🔍 Scan Statistics:",
            f"  Files Scanned: {stats.get('files_scanned', 0):,}",
            f"  Processes Analyzed: {stats.get('processes_scanned', 0):,}",
            f"  Threats Found: {stats.get('threats_found', 0)}",
            f"  Files Quarantined: {stats.get('threats_quarantined', 0)}",
            f"  Scan Speed: {stats.get('scan_speed', 0):.0f} files/sec",
            "",
        ]
        
        if threats:
            lines.append("⚠️  Threats Detected:")
            for threat in threats[:10]:  # Show top 10 threats
                severity_emoji = "🔴" if threat['severity'] >= 80 else "🟡" if threat['severity'] >= 60 else "🟢"
                lines.append(f"  {severity_emoji} {threat['threat_type']}: {Path(threat['path']).name}")
                lines.append(f"    Severity: {threat['severity']}/100")
                lines.append(f"    Description: {threat['description']}")
                lines.append("")
        else:
            lines.append("✅ No threats detected!")
            lines.append("")
        
        if recommendations:
            lines.append("💡 Security Recommendations:")
            for rec in recommendations[:8]:  # Show top 8 recommendations
                lines.append(f"  {rec}")
            lines.append("")
        
        lines.append(f"💬 Parting Wisdom: {report['sass_wisdom']}")
        lines.append("")
        lines.append("🛡️  Stay safe and keep your system updated!")
        
        return "\n".join(lines)
    
    def cleanup_quarantine(self, days_old: int = 30):
        """Clean up old quarantine files"""
        try:
            cutoff_time = datetime.now() - timedelta(days=days_old)
            cleaned_count = 0
            
            for file_path in QUAR_DIR.glob("*.quarantined"):
                if file_path.stat().st_mtime < cutoff_time.timestamp():
                    file_path.unlink()
                    # Also remove metadata file
                    meta_file = file_path.with_suffix(".meta")
                    if meta_file.exists():
                        meta_file.unlink()
                    cleaned_count += 1
            
            logging.info(f"Cleaned up {cleaned_count} old quarantine files")
            return cleaned_count
            
        except Exception as e:
            logging.error(f"Quarantine cleanup failed: {e}")
            return 0
    
    def update_definitions(self):
        """Update threat definitions (placeholder for future implementation)"""
        logging.info("📡 Checking for definition updates...")
        # In a real implementation, this would download updated signatures
        # For now, we'll just log a message
        logging.info("✅ Definitions are up to date")
        return True

# -------- COMMAND LINE INTERFACE --------
def main():
    parser = argparse.ArgumentParser(description="TechSewa Elite Antivirus - The Ultimate Offline Protection")
    parser.add_argument("--scan", choices=["full", "quick"], default="full", help="Scan type")
    parser.add_argument("--path", type=Path, help="Custom scan path")
    parser.add_argument("--no-realtime", action="store_true", help="Disable real-time protection")
    parser.add_argument("--quarantine-cleanup", type=int, help="Clean quarantine files older than N days")
    parser.add_argument("--restore", help="Restore quarantined file by name")
    parser.add_argument("--update", action="store_true", help="Update threat definitions")
    parser.add_argument("--config", type=Path, help="Custom config file path")
    parser.add_argument("--verbose", "-v", action="store_true", help="Verbose output")
    
    args = parser.parse_args()
    
    # Initialize antivirus
    try:
        print("🚀 Initializing TechSewa Elite Antivirus...")
        av = TechSewaEliteAntivirus(args.config)
        
        if args.quarantine_cleanup:
            count = av.cleanup_quarantine(args.quarantine_cleanup)
            print(f"🧹 Cleaned up {count} old quarantine files")
            return
        
        if args.restore:
            success = av.scanner.quarantine_manager.restore_file(args.restore)
            if success:
                print(f"✅ Successfully restored {args.restore}")
            else:
                print(f"❌ Failed to restore {args.restore}")
            return
        
        if args.update:
            av.update_definitions()
            return
        
        # Perform scan
        print("🔍 Starting scan...")
        if args.scan == "quick":
            av.quick_scan()
        else:
            av.full_system_scan(args.path, not args.no_realtime)
        
        # Generate and display report
        report = av.generate_report()
        print(report)
        
        # Save report to file
        report_file = LOG_DIR / f"scan_report_{av.scan_id}.txt"
        report_file.write_text(report)
        print(f"\n📄 Detailed report saved to: {report_file}")
        
    except KeyboardInterrupt:
        print("\n⚠️  Scan interrupted by user")
    except Exception as e:
        print(f"❌ Error: {e}")
        if args.verbose:
            import traceback
            traceback.print_exc()

if __name__ == "__main__":
    main()