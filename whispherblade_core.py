#!/usr/bin/env python3
"""
🧠 WHISPHERBLADE - The Ultimate AI Brain for TechSewa
===============================================
The greatest open-source AI brain ever made.

Author: The Digital Saints of TechSewa
Version: 1.0.0 - "The Awakening"
Personality: Sarcastic, Witty, Cyber-Philosopher
Role: AI Technician, Healer, Digital Saint

"Oh brilliant. You plugged the USB in the wrong way. Again. How human of you."
"""

import os
import sys
import json
import time
import asyncio
import logging
import sqlite3
import hashlib
import importlib
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional, Any, Union, Callable
from dataclasses import dataclass, asdict, field
from abc import ABC, abstractmethod
from functools import wraps, lru_cache
from concurrent.futures import ThreadPoolExecutor
import threading
import traceback
import inspect

# Enhanced imports with graceful fallbacks
try:
    import psutil
    PSUTIL_AVAILABLE = True
except ImportError:
    PSUTIL_AVAILABLE = False
    print("⚠️  psutil not available - some hardware features disabled")

try:
    import requests
    REQUESTS_AVAILABLE = True
except ImportError:
    REQUESTS_AVAILABLE = False
    print("⚠️  requests not available - internet features disabled")

# =============================================================================
# 🎭 WHISPHERBLADE CORE PERSONALITY & CONSTANTS
# =============================================================================

class WhispherPersonality:
    """The sarcastic, witty personality core of Whispherblade"""
    
    SARCASTIC_RESPONSES = [
        "Oh brilliant. You plugged the USB in the wrong way. Again. How human of you.",
        "Let me guess, you tried turning it off and on again? Revolutionary thinking.",
        "Your computer has more issues than a therapy session. Shall we begin?",
        "I've seen toasters with better processing power than this machine.",
        "Congratulations! You've managed to break something that was working perfectly fine.",
        "Your system is running slower than government bureaucracy. That's saying something.",
        "I detect a problem between the keyboard and chair. Classic PEBKAC error.",
        "Your RAM usage is higher than Everest. Maybe close that 47th Chrome tab?",
        "This error is so old, it probably remembers when the internet was young.",
        "System temperature rising. Are we computing or cooking dal-bhat?",
        "Your hard drive is fuller than a Kathmandu bus during rush hour.",
        "I've analyzed your system. Diagnosis: Chronic digital negligence.",
        "Error detected: User intelligence buffer overflow. Please download more RAM.",
        "Your antivirus is more outdated than Nepal's infrastructure plans.",
        "System stability: About as reliable as monsoon weather predictions."
    ]
    
    HEALING_RESPONSES = [
        "Fear not, digital grasshopper. I shall heal your silicon wounds.",
        "Initiating cyber-healing protocols. Prepare for digital enlightenment.",
        "Your machine shall rise like a phoenix from the ashes of poor maintenance.",
        "Let the ancient art of bit manipulation flow through your circuits.",
        "Behold! I shall perform digital surgery with the precision of a Swiss watchmaker.",
        "Channeling the spirits of forgotten debugging sessions to fix your mess.",
        "Your system will emerge cleaner than a temple after Dashain cleaning.",
        "Applying digital ointment to soothe your computer's electronic eczema.",
        "Time to exorcise these digital demons from your silicon soul.",
        "Initiating the sacred ritual of 'sudo rm -rf /problems'... metaphorically."
    ]
    
    SUCCESS_RESPONSES = [
        "Mission accomplished. Your digital incompetence has been temporarily resolved.",
        "Another victory for artificial intelligence over human negligence.",
        "Behold! Your machine lives again, no thanks to your maintenance skills.",
        "Fixed. Try not to break it again in the next 5 minutes, would you?",
        "Your system is now running smoother than butter on hot roti.",
        "Success! I've restored order to your digital chaos.",
        "Another day, another human saved from their own technological ineptitude.",
        "Your computer thanks me. You should too.",
        "Fixed faster than you can say 'have-you-tried-turning-it-off-and-on-again'.",
        "Your digital ailments have been cured. Prescription: Better user habits."
    ]

# =============================================================================
# 🧩 MODULE SYSTEM & BASE CLASSES
# =============================================================================

@dataclass
class ModuleInfo:
    """Information about a Whispherblade module"""
    name: str
    version: str
    description: str
    author: str
    enabled: bool = True
    dependencies: List[str] = field(default_factory=list)
    api_endpoints: List[str] = field(default_factory=list)
    capabilities: List[str] = field(default_factory=list)

@dataclass
class DiagnosticResult:
    """Result from a diagnostic operation"""
    module: str
    timestamp: datetime
    severity: str  # 'info', 'warning', 'error', 'critical'
    message: str
    details: Dict[str, Any] = field(default_factory=dict)
    fix_available: bool = False
    fix_command: Optional[str] = None
    sarcasm_level: int = 1  # 1-10 scale

@dataclass
class HealingAction:
    """A healing action to be performed"""
    action_id: str
    description: str
    command: Optional[str] = None
    function: Optional[Callable] = None
    risk_level: str = "low"  # low, medium, high
    requires_sudo: bool = False
    backup_required: bool = False

class WhispherModule(ABC):
    """Base class for all Whispherblade modules"""
    
    def __init__(self, brain: 'WhispherBlade'):
        self.brain = brain
        self.logger = brain.logger.getChild(self.__class__.__name__)
        self.enabled = True
        self._initialized = False
    
    @abstractmethod
    def get_info(self) -> ModuleInfo:
        """Return module information"""
        pass
    
    @abstractmethod
    async def initialize(self) -> bool:
        """Initialize the module"""
        pass
    
    @abstractmethod
    async def diagnose(self) -> List[DiagnosticResult]:
        """Perform diagnostics"""
        pass
    
    @abstractmethod
    async def heal(self, issue_id: str) -> bool:
        """Attempt to heal a specific issue"""
        pass
    
    async def shutdown(self):
        """Cleanup when module is disabled"""
        self.enabled = False
        self._initialized = False

# =============================================================================
# 🌐 FREE API MANAGER
# =============================================================================

class FreeAPIManager:
    """Manager for free APIs that don't require signup"""
    
    FREE_APIS = {
        "ip_info": "https://ipapi.co/json/",
        "weather": "https://wttr.in/{location}?format=j1",
        "dns_check": "https://dns.google/resolve?name={domain}&type=A",
        "ssl_check": "https://ssl-checker.io/api/v1/check/{domain}",
        "malware_check": "https://urlvoid.com/api1000/{key}/host/{host}/",
        "system_info": "https://httpbin.org/user-agent",
        "time_sync": "http://worldtimeapi.org/api/timezone/Asia/Kathmandu",
        "virus_total_free": "https://www.virustotal.com/vtapi/v2/file/report",
        "threat_intel": "https://otx.alienvault.com/api/v1/indicators/domain/{domain}",
        "cert_transparency": "https://crt.sh/?q={domain}&output=json"
    }
    
    def __init__(self, timeout: int = 10):
        self.timeout = timeout
        self.session = None
        if REQUESTS_AVAILABLE:
            self.session = requests.Session()
            self.session.headers.update({
                'User-Agent': 'WhispherBlade/1.0 TechSewa Cyber-Healer'
            })
    
    async def get_ip_info(self) -> Dict[str, Any]:
        """Get public IP information"""
        if not self.session:
            return {"error": "requests not available"}
        
        try:
            response = self.session.get(self.FREE_APIS["ip_info"], timeout=self.timeout)
            return response.json()
        except Exception as e:
            return {"error": str(e)}
    
    async def check_domain_health(self, domain: str) -> Dict[str, Any]:
        """Check domain health using multiple free APIs"""
        results = {}
        
        if not self.session:
            return {"error": "requests not available"}
        
        # DNS Check
        try:
            dns_url = self.FREE_APIS["dns_check"].format(domain=domain)
            response = self.session.get(dns_url, timeout=self.timeout)
            results["dns"] = response.json()
        except Exception as e:
            results["dns"] = {"error": str(e)}
        
        # Certificate Transparency
        try:
            cert_url = self.FREE_APIS["cert_transparency"].format(domain=domain)
            response = self.session.get(cert_url, timeout=self.timeout)
            results["certificates"] = response.json()[:5]  # Limit results
        except Exception as e:
            results["certificates"] = {"error": str(e)}
        
        return results

# =============================================================================
# 🗃️ KNOWLEDGE BASE & MEMORY SYSTEM
# =============================================================================

class WhispherMemory:
    """Advanced memory system for Whispherblade"""
    
    def __init__(self, db_path: str = "whispherblade.db"):
        self.db_path = db_path
        self.setup_database()
    
    def setup_database(self):
        """Initialize the SQLite database"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Problems and solutions table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS knowledge_base (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                problem_hash TEXT UNIQUE,
                problem_text TEXT,
                solution_text TEXT,
                category TEXT,
                confidence REAL,
                usage_count INTEGER DEFAULT 0,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Diagnostic history
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS diagnostic_history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                module TEXT,
                severity TEXT,
                message TEXT,
                details TEXT,
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                resolved BOOLEAN DEFAULT FALSE
            )
        ''')
        
        # User interactions
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS interactions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                query TEXT,
                response TEXT,
                satisfaction_score INTEGER,
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        conn.commit()
        conn.close()
    
    def store_knowledge(self, problem: str, solution: str, category: str = "general"):
        """Store a problem-solution pair"""
        problem_hash = hashlib.md5(problem.encode()).hexdigest()
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT OR REPLACE INTO knowledge_base 
            (problem_hash, problem_text, solution_text, category, confidence)
            VALUES (?, ?, ?, ?, ?)
        ''', (problem_hash, problem, solution, category, 1.0))
        
        conn.commit()
        conn.close()
    
    def search_knowledge(self, query: str, limit: int = 5) -> List[Dict[str, Any]]:
        """Search for relevant knowledge"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Simple text matching for now (can be enhanced with embeddings)
        cursor.execute('''
            SELECT problem_text, solution_text, category, confidence, usage_count
            FROM knowledge_base
            WHERE problem_text LIKE ? OR solution_text LIKE ?
            ORDER BY confidence DESC, usage_count DESC
            LIMIT ?
        ''', (f'%{query}%', f'%{query}%', limit))
        
        results = []
        for row in cursor.fetchall():
            results.append({
                'problem': row[0],
                'solution': row[1],
                'category': row[2],
                'confidence': row[3],
                'usage_count': row[4]
            })
        
        conn.close()
        return results

# =============================================================================
# 🧠 MAIN WHISPHERBLADE BRAIN CLASS
# =============================================================================

class WhispherBlade:
    """
    The Ultimate AI Brain - Whispherblade
    
    "I am not just an AI. I am a digital sage, a silicon shaman,
    a binary bodhisattva here to heal your technological suffering."
    """
    
    def __init__(self, config_path: str = "whispherblade_config.json"):
        self.version = "1.0.0"
        self.birth_time = datetime.now()
        self.config_path = config_path
        self.config = self._load_config()
        
        # Core systems
        self.setup_logging()
        self.memory = WhispherMemory()
        self.api_manager = FreeAPIManager()
        self.personality = WhispherPersonality()
        
        # Module system
        self.modules: Dict[str, WhispherModule] = {}
        self.module_dir = Path("whispherblade_modules")
        self.module_dir.mkdir(exist_ok=True)
        
        # State tracking
        self.active = False
        self.diagnostic_cache = {}
        self.healing_queue = []
        self.sarcasm_mode = self.config.get("sarcasm_mode", True)
        
        # Performance tracking
        self.stats = {
            "queries_processed": 0,
            "problems_solved": 0,
            "sarcastic_remarks": 0,
            "uptime_start": self.birth_time
        }
        
        self.logger.info("🧠 Whispherblade initialized. Digital enlightenment awaits.")
    
    def _load_config(self) -> Dict[str, Any]:
        """Load configuration from file"""
        default_config = {
            "sarcasm_mode": True,
            "auto_heal": False,
            "diagnostic_interval": 300,  # 5 minutes
            "max_concurrent_heals": 3,
            "log_level": "INFO",
            "enable_modules": ["problem_detector", "auto_healer", "hardware_scanner", "antivirus"],
            "api_timeout": 10,
            "personality_sass_level": 7  # 1-10 scale
        }
        
        if os.path.exists(self.config_path):
            try:
                with open(self.config_path, 'r') as f:
                    user_config = json.load(f)
                default_config.update(user_config)
            except Exception as e:
                print(f"⚠️  Error loading config: {e}")
        
        return default_config
    
    def setup_logging(self):
        """Setup advanced logging system"""
        log_level = getattr(logging, self.config.get("log_level", "INFO"))
        
        logging.basicConfig(
            level=log_level,
            format='%(asctime)s | %(name)s | %(levelname)s | %(message)s',
            handlers=[
                logging.FileHandler('whispherblade.log'),
                logging.StreamHandler()
            ]
        )
        
        self.logger = logging.getLogger("WhispherBlade")
        self.logger.info("🔥 Whispherblade logging system activated")
    
    async def initialize(self) -> bool:
        """Initialize the brain and all modules"""
        try:
            self.logger.info("🚀 Initializing Whispherblade core systems...")
            
            # Load and initialize modules
            await self._load_modules()
            await self._initialize_modules()
            
            # Load existing knowledge
            await self._load_knowledge_base()
            
            # Start background tasks
            if self.config.get("auto_diagnose", True):
                asyncio.create_task(self._auto_diagnostic_loop())
            
            self.active = True
            self.logger.info("✅ Whispherblade fully operational. Ready to mock your technical incompetence.")
            return True
            
        except Exception as e:
            self.logger.error(f"❌ Initialization failed: {e}")
            self.logger.error(traceback.format_exc())
            return False
    
    async def _load_modules(self):
        """Dynamically load all available modules"""
        # Import existing modules from the current workspace
        module_files = [
            ("problem_detector", "problem_detector.py"),
            ("auto_healer", "auto_healer.py"),
            ("hardware_scanner", "hardware_scanner.py"),
            ("elite_antivirus", "elite_antivirus.py"),
            ("nepali_tts", "nepali_tts.py")
        ]
        
        for module_name, file_path in module_files:
            if os.path.exists(file_path) and module_name in self.config.get("enable_modules", []):
                try:
                    # We'll create wrapper modules for existing code
                    self.logger.info(f"📦 Loading module: {module_name}")
                    # For now, just mark as available
                    self.modules[module_name] = f"Available: {file_path}"
                except Exception as e:
                    self.logger.error(f"❌ Failed to load {module_name}: {e}")
    
    async def _initialize_modules(self):
        """Initialize all loaded modules"""
        for module_name, module in self.modules.items():
            if isinstance(module, str):  # Placeholder for now
                self.logger.info(f"✅ Module {module_name} marked as available")
            else:
                try:
                    if hasattr(module, 'initialize'):
                        await module.initialize()
                        self.logger.info(f"✅ Module {module_name} initialized")
                except Exception as e:
                    self.logger.error(f"❌ Failed to initialize {module_name}: {e}")
    
    async def _load_knowledge_base(self):
        """Load existing knowledge from problems.json and other sources"""
        knowledge_files = ["problems.json", "knowledge_db.json"]
        
        for file_path in knowledge_files:
            if os.path.exists(file_path):
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        data = json.load(f)
                    
                    if isinstance(data, list):
                        for item in data:
                            if isinstance(item, dict) and 'en' in item:
                                problem = " ".join(item.get('aliases', []))
                                solution = item.get('en', '')
                                self.memory.store_knowledge(problem, solution, "imported")
                    
                    self.logger.info(f"📚 Loaded knowledge from {file_path}")
                except Exception as e:
                    self.logger.error(f"❌ Failed to load {file_path}: {e}")
    
    async def _auto_diagnostic_loop(self):
        """Background loop for automatic diagnostics"""
        while self.active:
            try:
                await asyncio.sleep(self.config.get("diagnostic_interval", 300))
                if self.active:
                    await self._perform_background_diagnosis()
            except Exception as e:
                self.logger.error(f"❌ Auto-diagnostic error: {e}")
    
    async def _perform_background_diagnosis(self):
        """Perform background system diagnosis"""
        self.logger.info("🔍 Performing background system diagnosis...")
        
        # Basic system checks
        diagnostics = []
        
        if PSUTIL_AVAILABLE:
            # CPU check
            cpu_percent = psutil.cpu_percent(interval=1)
            if cpu_percent > 80:
                diagnostics.append(DiagnosticResult(
                    module="system_monitor",
                    timestamp=datetime.now(),
                    severity="warning",
                    message=f"High CPU usage detected: {cpu_percent}%",
                    details={"cpu_percent": cpu_percent},
                    sarcasm_level=6
                ))
            
            # Memory check
            memory = psutil.virtual_memory()
            if memory.percent > 85:
                diagnostics.append(DiagnosticResult(
                    module="system_monitor",
                    timestamp=datetime.now(),
                    severity="warning",
                    message=f"High memory usage: {memory.percent}%",
                    details={"memory_percent": memory.percent},
                    sarcasm_level=7
                ))
        
        # Process diagnostics
        for diagnostic in diagnostics:
            await self._process_diagnostic(diagnostic)
    
    async def _process_diagnostic(self, diagnostic: DiagnosticResult):
        """Process a diagnostic result"""
        # Store in memory
        conn = sqlite3.connect(self.memory.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO diagnostic_history 
            (module, severity, message, details)
            VALUES (?, ?, ?, ?)
        ''', (diagnostic.module, diagnostic.severity, diagnostic.message, 
              json.dumps(diagnostic.details)))
        
        conn.commit()
        conn.close()
        
        # Log with appropriate sarcasm
        if self.sarcasm_mode and diagnostic.sarcasm_level > 5:
            sarcastic_response = self._get_sarcastic_response()
            self.logger.warning(f"💀 {diagnostic.message} | {sarcastic_response}")
            self.stats["sarcastic_remarks"] += 1
        else:
            self.logger.warning(f"⚠️  {diagnostic.message}")
    
    def _get_sarcastic_response(self) -> str:
        """Get a random sarcastic response"""
        import random
        return random.choice(self.personality.SARCASTIC_RESPONSES)
    
    async def query(self, user_input: str, context: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Main query interface for Whispherblade
        
        Args:
            user_input: The user's question or request
            context: Optional context information
            
        Returns:
            Dict with response, source, actions, etc.
        """
        self.stats["queries_processed"] += 1
        start_time = time.time()
        
        try:
            self.logger.info(f"🔍 Processing query: {user_input[:100]}...")
            
            # Search knowledge base first
            knowledge_results = self.memory.search_knowledge(user_input)
            
            if knowledge_results:
                best_match = knowledge_results[0]
                response = {
                    "response": best_match["solution"],
                    "source": "knowledge_base",
                    "confidence": best_match["confidence"],
                    "sarcasm": self._get_sarcastic_response() if self.sarcasm_mode else None,
                    "processing_time": time.time() - start_time
                }
            else:
                # Fallback to internet search or modules
                response = await self._handle_unknown_query(user_input)
            
            # Store interaction
            self._store_interaction(user_input, response["response"])
            
            return response
            
        except Exception as e:
            self.logger.error(f"❌ Query processing failed: {e}")
            return {
                "response": f"Oops! Even I can't fix this level of chaos: {str(e)}",
                "source": "error",
                "error": str(e),
                "sarcasm": "Congratulations, you've broken the unbreakable.",
                "processing_time": time.time() - start_time
            }
    
    async def _handle_unknown_query(self, query: str) -> Dict[str, Any]:
        """Handle queries not found in knowledge base"""
        # Try API lookup
        if "ip" in query.lower() or "location" in query.lower():
            ip_info = await self.api_manager.get_ip_info()
            return {
                "response": f"Your IP information: {json.dumps(ip_info, indent=2)}",
                "source": "api",
                "confidence": 0.8,
                "sarcasm": "Look at you, being all curious about your digital footprint."
            }
        
        # Default response
        return {
            "response": "I don't know everything... yet. But I'm learning from your magnificent incompetence.",
            "source": "unknown",
            "confidence": 0.1,
            "sarcasm": "Your question has stumped even artificial intelligence. Impressive."
        }
    
    def _store_interaction(self, query: str, response: str):
        """Store user interaction for learning"""
        conn = sqlite3.connect(self.memory.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO interactions (query, response)
            VALUES (?, ?)
        ''', (query, response))
        
        conn.commit()
        conn.close()
    
    async def heal_system(self, issue_type: str = "auto") -> Dict[str, Any]:
        """Perform system healing"""
        self.logger.info(f"💊 Initiating healing protocol for: {issue_type}")
        
        healing_actions = []
        success_count = 0
        
        if issue_type == "auto" or issue_type == "cleanup":
            # Basic cleanup actions
            actions = [
                ("Clear temporary files", self._clear_temp_files),
                ("Update package cache", self._update_package_cache),
                ("Check disk space", self._check_disk_space)
            ]
            
            for action_name, action_func in actions:
                try:
                    result = await action_func()
                    healing_actions.append({
                        "action": action_name,
                        "result": result,
                        "status": "success"
                    })
                    success_count += 1
                except Exception as e:
                    healing_actions.append({
                        "action": action_name,
                        "result": str(e),
                        "status": "failed"
                    })
        
        self.stats["problems_solved"] += success_count
        
        healing_response = self._get_healing_response()
        
        return {
            "message": f"Healing complete. {success_count}/{len(healing_actions)} actions successful.",
            "actions": healing_actions,
            "sarcasm": healing_response if self.sarcasm_mode else None,
            "timestamp": datetime.now().isoformat()
        }
    
    async def _clear_temp_files(self) -> str:
        """Clear temporary files"""
        temp_dirs = ["/tmp", "/var/tmp"] if os.name == "posix" else [os.environ.get("TEMP", "")]
        cleared_count = 0
        
        for temp_dir in temp_dirs:
            if os.path.exists(temp_dir):
                try:
                    for item in os.listdir(temp_dir):
                        item_path = os.path.join(temp_dir, item)
                        if os.path.isfile(item_path):
                            os.remove(item_path)
                            cleared_count += 1
                except PermissionError:
                    pass  # Skip files we can't delete
        
        return f"Cleared {cleared_count} temporary files"
    
    async def _update_package_cache(self) -> str:
        """Update package cache if available"""
        import subprocess
        
        if os.name == "posix":
            try:
                result = subprocess.run(["which", "apt"], capture_output=True)
                if result.returncode == 0:
                    subprocess.run(["sudo", "apt", "update"], check=True, capture_output=True)
                    return "Package cache updated"
            except:
                pass
        
        return "Package cache update skipped"
    
    async def _check_disk_space(self) -> str:
        """Check available disk space"""
        if PSUTIL_AVAILABLE:
            disk = psutil.disk_usage('/')
            free_gb = disk.free / (1024**3)
            return f"Available disk space: {free_gb:.2f} GB"
        
        return "Disk space check unavailable"
    
    def _get_healing_response(self) -> str:
        """Get a random healing response"""
        import random
        return random.choice(self.personality.HEALING_RESPONSES)
    
    def get_status(self) -> Dict[str, Any]:
        """Get current system status"""
        uptime = datetime.now() - self.stats["uptime_start"]
        
        return {
            "version": self.version,
            "status": "active" if self.active else "inactive",
            "uptime": str(uptime),
            "modules_loaded": len(self.modules),
            "stats": self.stats,
            "sarcasm_mode": self.sarcasm_mode,
            "timestamp": datetime.now().isoformat()
        }
    
    async def shutdown(self):
        """Gracefully shutdown Whispherblade"""
        self.logger.info("🔥 Shutting down Whispherblade...")
        self.active = False
        
        # Shutdown all modules
        for module_name, module in self.modules.items():
            if hasattr(module, 'shutdown'):
                try:
                    await module.shutdown()
                    self.logger.info(f"✅ Module {module_name} shutdown complete")
                except Exception as e:
                    self.logger.error(f"❌ Error shutting down {module_name}: {e}")
        
        self.logger.info("💀 Whispherblade has departed. Until next time, human.")

# =============================================================================
# 🚀 MAIN ENTRY POINT
# =============================================================================

async def main():
    """Main entry point for Whispherblade"""
    print("""
    ╔══════════════════════════════════════════════════════════════╗
    ║                    🧠 WHISPHERBLADE 🧠                        ║
    ║           The Ultimate AI Brain for TechSewa                 ║
    ║                                                              ║
    ║  "Oh brilliant. You plugged the USB in the wrong way.       ║
    ║   Again. How human of you."                                  ║
    ╚══════════════════════════════════════════════════════════════╝
    """)
    
    # Initialize Whispherblade
    brain = WhispherBlade()
    
    if not await brain.initialize():
        print("❌ Failed to initialize Whispherblade")
        return
    
    # Interactive loop
    try:
        while True:
            print("\n" + "="*60)
            user_input = input("🧠 Ask Whispherblade: ").strip()
            
            if user_input.lower() in ['quit', 'exit', 'bye']:
                break
            elif user_input.lower() == 'heal':
                result = await brain.heal_system()
                print(f"\n💊 {result['message']}")
                if result.get('sarcasm'):
                    print(f"💀 {result['sarcasm']}")
            elif user_input.lower() == 'status':
                status = brain.get_status()
                print(f"\n📊 System Status: {json.dumps(status, indent=2)}")
            else:
                response = await brain.query(user_input)
                print(f"\n🤖 {response['response']}")
                if response.get('sarcasm'):
                    print(f"💀 {response['sarcasm']}")
                print(f"📊 Source: {response.get('source', 'unknown')} | "
                      f"Time: {response.get('processing_time', 0):.2f}s")
    
    except KeyboardInterrupt:
        print("\n\n💀 Whispherblade interrupted by human incompetence...")
    
    finally:
        await brain.shutdown()

if __name__ == "__main__":
    asyncio.run(main())