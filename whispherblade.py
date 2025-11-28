import os
import json
import re
import time
import hashlib
import asyncio
import aiohttp
import sqlite3
from pathlib import Path
from datetime import datetime, timedelta
from dataclasses import dataclass, asdict
from typing import Dict, List, Optional, Tuple, Any, Union
from functools import lru_cache, wraps
from contextlib import asynccontextmanager
import logging
from concurrent.futures import ThreadPoolExecutor
from urllib.parse import quote_plus

# Enhanced imports with better fallback handling
try:
    import psutil
    HW_MONITOR_OK = True
except ImportError:
    HW_MONITOR_OK = False
    print("⚠️  psutil not available - hardware monitoring disabled")

try:
    from sentence_transformers import SentenceTransformer, util
    import torch
    SEMANTIC_OK = True
except ImportError:
    SEMANTIC_OK = False
    print("⚠️  sentence_transformers not available - semantic search disabled")

# Use dynamic imports to avoid static analyzer errors when the package is not installed
try:
    import importlib
    sr = importlib.import_module('speech_recognition')
    pyttsx3 = importlib.import_module('pyttsx3')
    SPEECH_OK = True
except Exception:
    SPEECH_OK = False
    sr = None
    pyttsx3 = None
    print("⚠️  speech libraries not available - voice interface disabled")

try:
    import PyPDF2
    import docx
    DOCUMENT_OK = True
except ImportError:
    DOCUMENT_OK = False
    print("⚠️  document libraries not available - PDF/Word processing disabled")

try:
    import requests
    from bs4 import BeautifulSoup
    WEB_OK = True
except ImportError:
    WEB_OK = False
    print("⚠️  web libraries not available - web search disabled")

try:
    from fuzzywuzzy import fuzz, process
    FUZZY_OK = True
except ImportError:
    FUZZY_OK = False
    print("⚠️  fuzzywuzzy not available - fuzzy matching disabled")

# ==================== CONFIGURATION ====================
@dataclass
class Config:
    """Configuration settings"""
    DB_PATH: str = "whisperblade.db"
    CACHE_SIZE: int = 5000
    MAX_RESPONSE_TIME: float = 3.0
    SEMANTIC_THRESHOLD: float = 0.65
    FUZZY_THRESHOLD: int = 70
    LOG_LEVEL: str = "INFO"
    ENABLE_VOICE: bool = True
    ENABLE_HARDWARE_MONITORING: bool = True
    ENABLE_WEB_SEARCH: bool = True
    SUPPORT_CONTACT: str = """
📌 TechSewa Support:
🏢 Learner Mission & Training Center
🗺️ Thuphandanda, Dadeldhura, Nepal
📞 +977-9867315931
📧 learnermission@gmail.com
⏰ 24/7 Support Available
"""

# ==================== DATA MODELS ====================
@dataclass
class KnowledgeEntry:
    """Enhanced knowledge entry with metadata"""
    id: str
    content_en: str
    content_np: str
    aliases_en: List[str]
    aliases_np: List[str]
    category: str
    priority: int = 1
    error_codes: List[str] = None
    created_at: datetime = None
    updated_at: datetime = None
    usage_count: int = 0
    success_rate: float = 1.0
    
    def __post_init__(self):
        if self.error_codes is None:
            self.error_codes = []
        if self.created_at is None:
            self.created_at = datetime.now()
        if self.updated_at is None:
            self.updated_at = datetime.now()

@dataclass
class QueryResult:
    """Query result with metadata"""
    answer: str
    source: str
    confidence: float
    response_time: float
    lang: str
    entry_id: Optional[str] = None
    suggestions: List[str] = None
    
    def __post_init__(self):
        if self.suggestions is None:
            self.suggestions = []

@dataclass
class SystemHealth:
    """System health metrics"""
    cpu_usage: float
    memory_usage: float
    disk_usage: float
    network_active: bool
    temperature: Dict[str, float]
    uptime: float
    processes: int
    load_average: List[float]
    timestamp: datetime = None
    
    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = datetime.now()

# ==================== ENHANCED DATABASE ====================
class DatabaseManager:
    """SQLite database manager with async support"""
    
    def __init__(self, db_path: str):
        self.db_path = db_path
        self.init_db()
    
    def init_db(self):
        """Initialize database with proper schema"""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute('''
                CREATE TABLE IF NOT EXISTS knowledge_entries (
                    id TEXT PRIMARY KEY,
                    content_en TEXT NOT NULL,
                    content_np TEXT NOT NULL,
                    aliases_en TEXT,
                    aliases_np TEXT,
                    category TEXT,
                    priority INTEGER DEFAULT 1,
                    error_codes TEXT,
                    created_at TIMESTAMP,
                    updated_at TIMESTAMP,
                    usage_count INTEGER DEFAULT 0,
                    success_rate REAL DEFAULT 1.0
                )
            ''')
            
            conn.execute('''
                CREATE TABLE IF NOT EXISTS query_logs (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp TIMESTAMP,
                    user_id TEXT,
                    query TEXT,
                    response TEXT,
                    source TEXT,
                    confidence REAL,
                    response_time REAL,
                    lang TEXT,
                    success BOOLEAN
                )
            ''')
            
            conn.execute('''
                CREATE TABLE IF NOT EXISTS system_metrics (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp TIMESTAMP,
                    cpu_usage REAL,
                    memory_usage REAL,
                    disk_usage REAL,
                    network_active BOOLEAN,
                    temperature TEXT,
                    uptime REAL
                )
            ''')
            
            # Create indexes for better performance
            conn.execute('CREATE INDEX IF NOT EXISTS idx_category ON knowledge_entries(category)')
            conn.execute('CREATE INDEX IF NOT EXISTS idx_priority ON knowledge_entries(priority)')
            conn.execute('CREATE INDEX IF NOT EXISTS idx_timestamp ON query_logs(timestamp)')
            
            # Insert default knowledge if empty
            if not self.get_entry_count():
                self._insert_default_knowledge()
    
    def _insert_default_knowledge(self):
        """Insert default knowledge entries"""
        default_entries = [
            KnowledgeEntry(
                id="startup_issue",
                content_en="To fix startup problems: 1) Check power connections 2) Run system diagnostics 3) Try safe mode boot 4) Check for hardware failures",
                content_np="स्टार्टअप समस्या समाधान: १) पावर जडान जाँच गर्नुहोस् २) सिस्टम निदान चलाउनुहोस् ३) सेफ मोड बुट प्रयास गर्नुहोस् ४) हार्डवेयर विफलता जाँच गर्नुहोस्",
                aliases_en=["startup problem", "boot issue", "won't start", "slow boot"],
                aliases_np=["सुरु हुन्न", "धिलो खुल्छ", "बुट समस्या"],
                category="system",
                priority=1,
                error_codes=["0x800F0922", "0x80070570"]
            ),
            KnowledgeEntry(
                id="internet_issue",
                content_en="Internet troubleshooting: 1) Check router power and cables 2) Restart network adapter 3) Run network diagnostics 4) Check DNS settings",
                content_np="इन्टरनेट समस्या निवारण: १) राउटर पावर र केबल जाँच गर्नुहोस् २) नेटवर्क एडाप्टर रिस्टार्ट गर्नुहोस् ३) नेटवर्क निदान चलाउनुहोस् ४) DNS सेटिंग्स जाँच गर्नुहोस्",
                aliases_en=["no internet", "wifi not working", "connection problem", "network down"],
                aliases_np=["इन्टरनेट छैन", "वाइफाई काम गर्दैन", "नेटवर्क समस्या"],
                category="network",
                priority=1
            ),
            KnowledgeEntry(
                id="slow_performance",
                content_en="To improve system performance: 1) Close unnecessary programs 2) Clear temporary files 3) Check for malware 4) Add more RAM if needed",
                content_np="सिस्टम प्रदर्शन सुधार गर्न: १) अनावश्यक प्रोग्राम बन्द गर्नुहोस् २) अस्थायी फाइल सफा गर्नुहोस् ३) मालवेयर जाँच गर्नुहोस् ४) आवश्यक भएमा RAM थप्नुहोस्",
                aliases_en=["slow computer", "performance issue", "system lag", "running slow"],
                aliases_np=["धिलो कम्प्युटर", "प्रदर्शन समस्या", "सिस्टम ढिलो"],
                category="performance",
                priority=2
            )
        ]
        
        for entry in default_entries:
            self.save_entry(entry)
    
    def save_entry(self, entry: KnowledgeEntry) -> bool:
        """Save knowledge entry to database"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.execute('''
                    INSERT OR REPLACE INTO knowledge_entries 
                    (id, content_en, content_np, aliases_en, aliases_np, category, priority, 
                     error_codes, created_at, updated_at, usage_count, success_rate)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', (
                    entry.id, entry.content_en, entry.content_np,
                    json.dumps(entry.aliases_en), json.dumps(entry.aliases_np),
                    entry.category, entry.priority,
                    json.dumps(entry.error_codes),
                    entry.created_at.isoformat(), entry.updated_at.isoformat(),
                    entry.usage_count, entry.success_rate
                ))
            return True
        except Exception as e:
            logging.error(f"Error saving entry: {e}")
            return False
    
    def get_all_entries(self) -> List[KnowledgeEntry]:
        """Get all knowledge entries"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.execute('''
                    SELECT * FROM knowledge_entries ORDER BY priority, usage_count DESC
                ''')
                
                entries = []
                for row in cursor.fetchall():
                    entries.append(KnowledgeEntry(
                        id=row[0],
                        content_en=row[1],
                        content_np=row[2],
                        aliases_en=json.loads(row[3]) if row[3] else [],
                        aliases_np=json.loads(row[4]) if row[4] else [],
                        category=row[5],
                        priority=row[6],
                        error_codes=json.loads(row[7]) if row[7] else [],
                        created_at=datetime.fromisoformat(row[8]),
                        updated_at=datetime.fromisoformat(row[9]),
                        usage_count=row[10],
                        success_rate=row[11]
                    ))
                return entries
        except Exception as e:
            logging.error(f"Error getting entries: {e}")
            return []
    
    def get_entry_count(self) -> int:
        """Get total number of entries"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.execute('SELECT COUNT(*) FROM knowledge_entries')
                return cursor.fetchone()[0]
        except:
            return 0
    
    def log_query(self, query: str, result: QueryResult, user_id: str = None):
        """Log query and result"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.execute('''
                    INSERT INTO query_logs 
                    (timestamp, user_id, query, response, source, confidence, response_time, lang, success)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', (
                    datetime.now().isoformat(),
                    user_id,
                    query[:500],  # Truncate long queries
                    result.answer[:1000],  # Truncate long responses
                    result.source,
                    result.confidence,
                    result.response_time,
                    result.lang,
                    result.confidence > 0.5
                ))
        except Exception as e:
            logging.error(f"Error logging query: {e}")
    
    def update_entry_usage(self, entry_id: str, success: bool = True):
        """Update entry usage statistics"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                # Get current stats
                cursor = conn.execute(
                    'SELECT usage_count, success_rate FROM knowledge_entries WHERE id = ?',
                    (entry_id,)
                )
                row = cursor.fetchone()
                if row:
                    usage_count, success_rate = row
                    new_usage_count = usage_count + 1
                    new_success_rate = ((success_rate * usage_count) + (1 if success else 0)) / new_usage_count
                    
                    conn.execute('''
                        UPDATE knowledge_entries 
                        SET usage_count = ?, success_rate = ?, updated_at = ?
                        WHERE id = ?
                    ''', (new_usage_count, new_success_rate, datetime.now().isoformat(), entry_id))
        except Exception as e:
            logging.error(f"Error updating entry usage: {e}")

# ==================== ENHANCED KNOWLEDGE ENGINE ====================
class AdvancedKnowledgeEngine:
    """Advanced knowledge engine with multiple search strategies"""
    
    def __init__(self, config: Config):
        self.config = config
        self.db = DatabaseManager(config.DB_PATH)
        self.semantic_model = None
        self.semantic_embeddings = {}
        self.executor = ThreadPoolExecutor(max_workers=4)
        
        # Initialize semantic model
        if SEMANTIC_OK:
            self._init_semantic_model()
        
        # Build search indices
        self._build_indices()
    
    def _init_semantic_model(self):
        """Initialize semantic search model"""
        try:
            self.semantic_model = SentenceTransformer("all-MiniLM-L6-v2")
            self._build_semantic_embeddings()
        except Exception as e:
            logging.error(f"Failed to initialize semantic model: {e}")
            self.semantic_model = None
    
    def _build_semantic_embeddings(self):
        """Build semantic embeddings for all entries"""
        if not self.semantic_model:
            return
        
        try:
            entries = self.db.get_all_entries()
            texts = []
            entry_ids = []
            
            for entry in entries:
                # Create combined text for embedding
                combined_text = f"{entry.content_en} {' '.join(entry.aliases_en)}"
                texts.append(combined_text)
                entry_ids.append(entry.id)
            
            if texts:
                embeddings = self.semantic_model.encode(texts)
                self.semantic_embeddings = {
                    entry_id: embedding 
                    for entry_id, embedding in zip(entry_ids, embeddings)
                }
        except Exception as e:
            logging.error(f"Error building semantic embeddings: {e}")
    
    def _build_indices(self):
        """Build search indices for fast lookup"""
        self.indices = {
            'en_aliases': {},
            'np_aliases': {},
            'error_codes': {},
            'categories': {}
        }
        
        entries = self.db.get_all_entries()
        for entry in entries:
            # English aliases
            for alias in entry.aliases_en:
                self.indices['en_aliases'][alias.lower()] = entry.id
            
            # Nepali aliases
            for alias in entry.aliases_np:
                self.indices['np_aliases'][alias.lower()] = entry.id
            
            # Error codes
            for code in entry.error_codes:
                self.indices['error_codes'][code.upper()] = entry.id
            
            # Categories
            if entry.category not in self.indices['categories']:
                self.indices['categories'][entry.category] = []
            self.indices['categories'][entry.category].append(entry.id)
    
    @lru_cache(maxsize=2000)
    def search(self, query: str, lang: str = None, user_id: str = None) -> QueryResult:
        """Enhanced search with multiple strategies"""
        start_time = time.time()
        
        # Auto-detect language
        if lang is None:
            lang = self._detect_language(query)
        
        # Search strategies in order of preference
        strategies = [
            self._search_error_codes,
            self._search_exact_match,
            self._search_fuzzy_match,
            self._search_semantic_match,
            self._search_category_match
        ]
        
        best_result = None
        best_confidence = 0.0
        
        for strategy in strategies:
            try:
                result = strategy(query, lang)
                if result and result.confidence > best_confidence:
                    best_result = result
                    best_confidence = result.confidence
                    
                    # If we have a high confidence match, use it
                    if result.confidence >= 0.9:
                        break
            except Exception as e:
                logging.error(f"Search strategy error: {e}")
        
        # Fallback if no good match found
        if not best_result or best_confidence < 0.3:
            best_result = self._generate_fallback_response(query, lang)
        
        # Set response time
        best_result.response_time = time.time() - start_time
        
        # Log the query
        self.db.log_query(query, best_result, user_id)
        
        # Update entry usage if we found a match
        if best_result.entry_id:
            self.db.update_entry_usage(best_result.entry_id, best_result.confidence > 0.5)
        
        return best_result
    
    def _detect_language(self, text: str) -> str:
        """Detect language of input text"""
        # Simple heuristic: if text contains Devanagari characters, it's Nepali
        return 'np' if any(ord(c) > 2303 and ord(c) < 2432 for c in text) else 'en'
    
    def _search_error_codes(self, query: str, lang: str) -> Optional[QueryResult]:
        """Search for error codes in query"""
        error_pattern = r'0x[0-9A-F]{6,8}'
        matches = re.findall(error_pattern, query.upper())
        
        for code in matches:
            if code in self.indices['error_codes']:
                entry_id = self.indices['error_codes'][code]
                entry = self._get_entry_by_id(entry_id)
                if entry:
                    return QueryResult(
                        answer=entry.content_np if lang == 'np' else entry.content_en,
                        source='error_code',
                        confidence=1.0,
                        response_time=0.0,
                        lang=lang,
                        entry_id=entry_id
                    )
        return None
    
    def _search_exact_match(self, query: str, lang: str) -> Optional[QueryResult]:
        """Search for exact matches in aliases"""
        query_lower = query.lower()
        index_key = 'np_aliases' if lang == 'np' else 'en_aliases'
        
        if query_lower in self.indices[index_key]:
            entry_id = self.indices[index_key][query_lower]
            entry = self._get_entry_by_id(entry_id)
            if entry:
                return QueryResult(
                    answer=entry.content_np if lang == 'np' else entry.content_en,
                    source='exact_match',
                    confidence=1.0,
                    response_time=0.0,
                    lang=lang,
                    entry_id=entry_id
                )
        return None
    
    def _search_fuzzy_match(self, query: str, lang: str) -> Optional[QueryResult]:
        """Search using fuzzy string matching"""
        if not FUZZY_OK:
            return None
        
        index_key = 'np_aliases' if lang == 'np' else 'en_aliases'
        aliases = list(self.indices[index_key].keys())
        
        if aliases:
            match = process.extractOne(query.lower(), aliases, scorer=fuzz.token_sort_ratio)
            if match and match[1] >= self.config.FUZZY_THRESHOLD:
                entry_id = self.indices[index_key][match[0]]
                entry = self._get_entry_by_id(entry_id)
                if entry:
                    confidence = match[1] / 100.0
                    return QueryResult(
                        answer=entry.content_np if lang == 'np' else entry.content_en,
                        source='fuzzy_match',
                        confidence=confidence,
                        response_time=0.0,
                        lang=lang,
                        entry_id=entry_id
                    )
        return None
    
    def _search_semantic_match(self, query: str, lang: str) -> Optional[QueryResult]:
        """Search using semantic similarity"""
        if not self.semantic_model or not self.semantic_embeddings:
            return None
        
        try:
            query_embedding = self.semantic_model.encode(query)
            best_match_id = None
            best_similarity = 0.0
            
            for entry_id, entry_embedding in self.semantic_embeddings.items():
                similarity = util.cos_sim(query_embedding, entry_embedding).item()
                if similarity > best_similarity:
                    best_similarity = similarity
                    best_match_id = entry_id
            
            if best_similarity >= self.config.SEMANTIC_THRESHOLD:
                entry = self._get_entry_by_id(best_match_id)
                if entry:
                    return QueryResult(
                        answer=entry.content_np if lang == 'np' else entry.content_en,
                        source='semantic_match',
                        confidence=best_similarity,
                        response_time=0.0,
                        lang=lang,
                        entry_id=best_match_id
                    )
        except Exception as e:
            logging.error(f"Semantic search error: {e}")
        
        return None
    
    def _search_category_match(self, query: str, lang: str) -> Optional[QueryResult]:
        """Search by category keywords"""
        category_keywords = {
            'system': ['system', 'startup', 'boot', 'computer', 'सिस्टम', 'कम्प्युटर'],
            'network': ['internet', 'network', 'wifi', 'connection', 'इन्टरनेट', 'नेटवर्क'],
            'performance': ['slow', 'performance', 'speed', 'lag', 'धिलो', 'प्रदर्शन'],
            'hardware': ['hardware', 'device', 'monitor', 'keyboard', 'हार्डवेयर'],
            'software': ['software', 'program', 'application', 'app', 'सफ्टवेयर']
        }
        
        query_lower = query.lower()
        for category, keywords in category_keywords.items():
            if any(keyword in query_lower for keyword in keywords):
                if category in self.indices['categories']:
                    entry_ids = self.indices['categories'][category]
                    if entry_ids:
                        # Return the highest priority entry from this category
                        entry_id = entry_ids[0]  # Already sorted by priority
                        entry = self._get_entry_by_id(entry_id)
                        if entry:
                            return QueryResult(
                                answer=entry.content_np if lang == 'np' else entry.content_en,
                                source='category_match',
                                confidence=0.6,
                                response_time=0.0,
                                lang=lang,
                                entry_id=entry_id
                            )
        return None
    
    def _get_entry_by_id(self, entry_id: str) -> Optional[KnowledgeEntry]:
        """Get entry by ID from database"""
        entries = self.db.get_all_entries()
        for entry in entries:
            if entry.id == entry_id:
                return entry
        return None
    
    def _generate_fallback_response(self, query: str, lang: str) -> QueryResult:
        """Generate fallback response when no match is found"""
        if lang == 'np':
            answer = f"माफ गर्नुहोस्, '{query}' को बारेमा विशिष्ट जानकारी फेला परेन। कृपया हाम्रो सहयोग टोलीलाई सम्पर्क गर्नुहोस्।"
        else:
            answer = f"I couldn't find specific information about '{query}'. Please contact our support team for detailed assistance."
        
        return QueryResult(
            answer=answer,
            source='fallback',
            confidence=0.1,
            response_time=0.0,
            lang=lang,
            suggestions=self._generate_suggestions(query, lang)
        )
    
    def _generate_suggestions(self, query: str, lang: str) -> List[str]:
        """Generate suggestions for similar queries"""
        suggestions = []
        try:
            entries = self.db.get_all_entries()
            
            # Get top 3 most used entries as suggestions
            top_entries = sorted(entries, key=lambda x: x.usage_count, reverse=True)[:3]
            
            for entry in top_entries:
                if lang == 'np' and entry.aliases_np:
                    suggestions.append(entry.aliases_np[0])
                elif lang == 'en' and entry.aliases_en:
                    suggestions.append(entry.aliases_en[0])
        except Exception as e:
            logging.error(f"Error generating suggestions: {e}")
        
        return suggestions

# ==================== ENHANCED HARDWARE MONITOR ====================
class EnhancedHardwareMonitor:
    """Advanced hardware monitoring with predictive analytics"""
    
    def __init__(self, config: Config):
        self.config = config
        self.enabled = HW_MONITOR_OK and config.ENABLE_HARDWARE_MONITORING
        self.alert_thresholds = {
            'cpu': 80.0,
            'memory': 85.0,
            'disk': 90.0,
            'temperature': 70.0
        }
    
    def get_system_health(self) -> SystemHealth:
        """Get comprehensive system health metrics"""
        if not self.enabled:
            return SystemHealth(
                cpu_usage=0.0,
                memory_usage=0.0,
                disk_usage=0.0,
                network_active=False,
                temperature={},
                uptime=0.0,
                processes=0,
                load_average=[]
            )
        
        try:
            # Get system metrics
            cpu_percent = psutil.cpu_percent(interval=1)
            memory = psutil.virtual_memory()
            disk = psutil.disk_usage('/')
            network = psutil.net_io_counters()
            
            # Temperature monitoring
            temperatures = {}
            try:
                if hasattr(psutil, 'sensors_temperatures'):
                    temp_sensors = psutil.sensors_temperatures()
                    for sensor_name, sensor_list in temp_sensors.items():
                        if sensor_list:
                            temperatures[sensor_name] = sensor_list[0].current
            except Exception:
                pass
            
            # Load average (Unix-like systems)
            load_avg = []
            try:
                if hasattr(os, 'getloadavg'):
                    load_avg = list(os.getloadavg())
            except Exception:
                pass
            
            return SystemHealth(
                cpu_usage=cpu_percent,
                memory_usage=memory.percent,
                disk_usage=disk.percent,
                network_active=network.bytes_sent > 0 or network.bytes_recv > 0,
                temperature=temperatures,
                uptime=time.time() - psutil.boot_time(),
                processes=len(psutil.pids()),
                load_average=load_avg
            )
        except Exception as e:
            logging.error(f"Error getting system health: {e}")
            return SystemHealth(
                cpu_usage=0.0,
                memory_usage=0.0,
                disk_usage=0.0,
                network_active=False,
                temperature={},
                uptime=0.0,
                processes=0,
                load_average=[]
            )
    
    def get_health_alerts(self) -> List[str]:
        """Get current health alerts"""
        if not self.enabled:
            return []
        
        alerts = []
        health = self.get_system_health()
        
        if health.cpu_usage > self.alert_thresholds['cpu']:
            alerts.append(f"High CPU usage: {health.cpu_usage:.1f}%")
        
        if health.memory_usage > self.alert_thresholds['memory']:
            alerts.append(f"High memory usage: {health.memory_usage:.1f}%")
        
        if health.disk_usage > self.alert_thresholds['disk']:
            alerts.append(f"High disk usage: {health.disk_usage:.1f}%")
        
        for sensor, temp in health.temperature.items():
            if temp > self.alert_thresholds['temperature']:
                alerts.append(f"High temperature {sensor}: {temp:.1f}°C")
        
        return alerts
    
    def generate_health_report(self, lang: str = 'en') -> str:
        """Generate comprehensive health report"""
        if not self.enabled:
            return "Hardware monitoring is disabled" if lang == 'en' else "हार्डवेयर मनिटरिङ असक्षम छ"
        
        health = self.get_system_health()
        alerts = self.get_health_alerts()
        
        if lang == 'np':
            report = f"""
🖥️ सिस्टम स्वास्थ्य रिपोर्ट
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
⚡ CPU उपयोग: {health.cpu_usage:.1f}%
💾 मेमोरी उपयोग: {health.memory_usage:.1f}%
💿 डिस्क उपयोग: {health.disk_usage:.1f}%
🌐 नेटवर्क: {'सक्रिय' if health.network_active else 'निष्क्रिय'}
🔄 प्रक्रियाहरू: {health.processes}
⏱️ अपटाइम: {health.uptime/3600:.1f} घण्टा
"""
            if health.temperature:
                report += "\n🌡️ तापमान:\n"
                for sensor, temp in health.temperature.items():
                    report += f"  • {sensor}: {temp:.1f}°C\n"
            
            if alerts:
                report += "\n⚠️ चेतावनीहरू:\n"
                for alert in alerts:
                    report += f"  • {alert}\n"
            else:
                report += "\n✅ सबै सिस्टम सामान्य छन्\n"
        else:
            report = f"""
🖥️ System Health Report
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
⚡ CPU Usage: {health.cpu_usage:.1f}%
💾 Memory Usage: {health.memory_usage:.1f}%
💿 Disk Usage: {health.disk_usage:.1f}%
🌐 Network: {'Active' if health.network_active else 'Inactive'}
🔄 Processes: {health.processes}
⏱️ Uptime: {health.uptime/3600:.1f} hours
"""
            if health.temperature:
                report += "\n🌡️ Temperatures:\n"
                for sensor, temp in health.temperature.items():
                    report += f"  • {sensor}: {temp:.1f}°C\n"
            
            if alerts:
                report += "\n⚠️ Alerts:\n"
                for alert in alerts:
                    report += f"  • {alert}\n"
            else:
                report += "\n✅ All systems normal\n"
        
        return report

# ==================== ENHANCED VOICE INTERFACE ====================
class EnhancedVoiceInterface:
    """Advanced voice interface with TTS support"""
    
    def __init__(self, config: Config):
        self.config = config
        self.enabled = SPEECH_OK and config.ENABLE_VOICE
        self.recognizer = None
        self.tts_engine = None
        
        if self.enabled:
            self._init_voice_components()
    
    def _init_voice_components(self):
        """Initialize voice recognition and TTS components"""
        try:
            self.recognizer = sr.Recognizer()
            self.tts_engine = pyttsx3.init()
            
            # Configure TTS settings
            self.tts_engine.setProperty('rate', 150)  # Speed of speech
            self.tts_engine.setProperty('volume', 0.8)  # Volume level
            
            # Try to set voice (prefer female voice for better clarity)
            voices = self.tts_engine.getProperty('voices')
            if voices:
                for voice in voices:
                    if 'female' in voice.name.lower() or 'zira' in voice.name.lower():
                        self.tts_engine.setProperty('voice', voice.id)
                        break
                        
        except Exception as e:
            logging.error(f"Error initializing voice components: {e}")
            self.enabled = False
    
    async def listen_async(self, lang: str = 'en', timeout: int = 5) -> Optional[str]:
        """Asynchronous voice input with timeout"""
        if not self.enabled:
            return None
        
        try:
            loop = asyncio.get_event_loop()
            return await loop.run_in_executor(None, self._listen_sync, lang, timeout)
        except Exception as e:
            logging.error(f"Async voice recognition error: {e}")
            return None
    
    def _listen_sync(self, lang: str, timeout: int) -> Optional[str]:
        """Synchronous voice input"""
        try:
            with sr.Microphone() as source:
                print("🎤 Listening..." if lang == 'en' else "🎤 सुन्दै...")
                
                # Adjust for ambient noise
                self.recognizer.adjust_for_ambient_noise(source, duration=1)
                
                # Listen for audio
                audio = self.recognizer.listen(source, timeout=timeout, phrase_time_limit=10)
            
            # Recognize speech
            language_code = 'ne-NP' if lang == 'np' else 'en-US'
            text = self.recognizer.recognize_google(audio, language=language_code)
            
            print(f"🎯 Recognized: {text}")
            return text
            
        except sr.WaitTimeoutError:
            print("⏱️ No speech detected")
            return None
        except sr.UnknownValueError:
            print("❌ Could not understand audio")
            return None
        except Exception as e:
            logging.error(f"Voice recognition error: {e}")
            return None
    
    def speak(self, text: str, lang: str = 'en'):
        """Text-to-speech output"""
        if not self.enabled or not text:
            return
        
        try:
            # For Nepali, we might need to use a different approach
            # or convert to English pronunciation
            if lang == 'np':
                # For now, we'll speak in English about Nepali content
                text = f"Response in Nepali: {text}"
            
            self.tts_engine.say(text)
            self.tts_engine.runAndWait()
            
        except Exception as e:
            logging.error(f"TTS error: {e}")
    
    async def speak_async(self, text: str, lang: str = 'en'):
        """Asynchronous text-to-speech"""
        if not self.enabled:
            return
        
        try:
            loop = asyncio.get_event_loop()
            await loop.run_in_executor(None, self.speak, text, lang)
        except Exception as e:
            logging.error(f"Async TTS error: {e}")

# ==================== ENHANCED WEB SEARCH PLUGIN ====================
class EnhancedWebSearchPlugin:
    """Enhanced web search plugin with multiple search strategies"""
    
    def __init__(self, config: Config):
        self.config = config
        self.enabled = True  # We'll handle availability internally
        self.cache = {}
        self.cache_timeout = 3600  # 1 hour
        self.session = None
        
        # Headers for web requests
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1'
        }
    
    async def __aenter__(self):
        """Async context manager entry"""
        self.session = aiohttp.ClientSession(
            headers=self.headers,
            timeout=aiohttp.ClientTimeout(total=30),
            connector=aiohttp.TCPConnector(ssl=False)
        )
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit"""
        if self.session:
            await self.session.close()
    
    async def search_async(self, query: str, lang: str = 'en') -> Optional[str]:
        """Enhanced asynchronous web search with multiple fallback strategies"""
        if not self.enabled:
            return None
        
        # Check cache first
        cache_key = f"{query}_{lang}"
        if cache_key in self.cache:
            cached_result, timestamp = self.cache[cache_key]
            if time.time() - timestamp < self.cache_timeout:
                return cached_result
        
        # Try different search strategies
        search_strategies = [
            self._search_duckduckgo_instant,
            self._search_wikipedia,
            self._search_stackoverflow,
            self._search_technical_sites,
            self._search_fallback_scraping
        ]
        
        async with self:
            for strategy in search_strategies:
                try:
                    result = await strategy(query, lang)
                    if result and len(result) > 50:  # Ensure we have substantial content
                        # Cache the result
                        self.cache[cache_key] = (result, time.time())
                        logging.info(f"Web search successful using {strategy.__name__}")
                        return result
                except Exception as e:
                    logging.warning(f"Search strategy {strategy.__name__} failed: {e}")
                    continue
        
        return None
    
    async def _search_duckduckgo_instant(self, query: str, lang: str) -> Optional[str]:
        """Search using DuckDuckGo Instant Answer API"""
        try:
            # Format query for technical searches
            tech_query = self._format_tech_query(query)
            
            url = f"https://api.duckduckgo.com/?q={quote_plus(tech_query)}&format=json&no_html=1&skip_disambig=1"
            
            async with self.session.get(url) as response:
                if response.status == 200:
                    data = await response.json()
                    
                    # Try to get instant answer
                    if data.get('Answer'):
                        return f"Quick Answer: {data['Answer']}"
                    
                    # Try abstract
                    if data.get('Abstract'):
                        return f"Information: {data['Abstract']}"
                    
                    # Try definition
                    if data.get('Definition'):
                        return f"Definition: {data['Definition']}"
                    
                    # Try related topics
                    if data.get('RelatedTopics'):
                        for topic in data['RelatedTopics'][:2]:
                            if isinstance(topic, dict) and topic.get('Text'):
                                return f"Related: {topic['Text']}"
        
        except Exception as e:
            logging.error(f"DuckDuckGo search error: {e}")
        
        return None
    
    async def _search_wikipedia(self, query: str, lang: str) -> Optional[str]:
        """Search Wikipedia for general information"""
        try:
            lang_code = 'ne' if lang == 'np' else 'en'
            
            # Search for articles
            search_url = f"https://{lang_code}.wikipedia.org/api/rest_v1/page/summary/{quote_plus(query)}"
            
            async with self.session.get(search_url) as response:
                if response.status == 200:
                    data = await response.json()
                    
                    if data.get('extract'):
                        extract = data['extract']
                        if len(extract) > 100:
                            return f"Wikipedia: {extract[:500]}..."
        
        except Exception as e:
            logging.error(f"Wikipedia search error: {e}")
        
        return None
    
    async def _search_stackoverflow(self, query: str, lang: str) -> Optional[str]:
        """Search Stack Overflow for technical issues"""
        try:
            # Only search technical queries
            if not self._is_technical_query(query):
                return None
            
            # Format query for Stack Overflow
            tech_query = f"{query} computer troubleshooting"
            
            url = f"https://api.stackexchange.com/2.3/search/advanced?order=desc&sort=relevance&q={quote_plus(tech_query)}&site=stackoverflow&filter=withbody"
            
            async with self.session.get(url) as response:
                if response.status == 200:
                    data = await response.json()
                    
                    if data.get('items'):
                        for item in data['items'][:2]:
                            if item.get('body'):
                                # Clean HTML tags
                                clean_body = re.sub(r'<[^>]+>', '', item['body'])
                                if len(clean_body) > 100:
                                    return f"Technical Solution: {clean_body[:400]}..."
        
        except Exception as e:
            logging.error(f"Stack Overflow search error: {e}")
        
        return None
    
    async def _search_technical_sites(self, query: str, lang: str) -> Optional[str]:
        """Search specific technical support sites"""
        try:
            # Sites to search for technical content
            tech_sites = [
                'support.microsoft.com',
                'support.google.com',
                'support.apple.com',
                'technet.microsoft.com'
            ]
            
            for site in tech_sites:
                try:
                    search_query = f"site:{site} {query}"
                    result = await self._search_with_custom_engine(search_query)
                    if result:
                        return f"Technical Support: {result}"
                except Exception:
                    continue
        
        except Exception as e:
            logging.error(f"Technical sites search error: {e}")
        
        return None
    
    async def _search_with_custom_engine(self, query: str) -> Optional[str]:
        """Search using a custom search approach"""
        try:
            # This is a simplified approach - you can enhance this
            # with your own search API or scraping logic
            
            # For now, return a formatted response based on common issues
            return self._get_common_solution(query)
        
        except Exception as e:
            logging.error(f"Custom search error: {e}")
        
        return None
    
    async def _search_fallback_scraping(self, query: str, lang: str) -> Optional[str]:
        """Fallback web scraping with improved reliability"""
        try:
            # Use alternative search engines
            search_engines = [
                f"https://www.startpage.com/sp/search?query={quote_plus(query)}",
                f"https://duckduckgo.com/html/?q={quote_plus(query)}",
                f"https://www.bing.com/search?q={quote_plus(query)}"
            ]
            
            for search_url in search_engines:
                try:
                    async with self.session.get(search_url) as response:
                        if response.status == 200:
                            html = await response.text()
                            result = self._parse_search_results(html, query)
                            if result:
                                return result
                except Exception:
                    continue
        
        except Exception as e:
            logging.error(f"Fallback scraping error: {e}")
        
        return None
    
    def _parse_search_results(self, html: str, query: str) -> Optional[str]:
        """Enhanced parsing of search results"""
        try:
            # Try to find relevant content snippets
            import re
            
            # Look for common result patterns
            patterns = [
                r'<div[^>]*class="[^"]*result[^"]*"[^>]*>(.*?)</div>',
                r'<p[^>]*class="[^"]*snippet[^"]*"[^>]*>(.*?)</p>',
                r'<span[^>]*class="[^"]*description[^"]*"[^>]*>(.*?)</span>'
            ]
            
            for pattern in patterns:
                matches = re.findall(pattern, html, re.DOTALL | re.IGNORECASE)
                for match in matches:
                    # Clean HTML tags
                    clean_text = re.sub(r'<[^>]+>', '', match).strip()
                    if len(clean_text) > 50 and query.lower() in clean_text.lower():
                        return f"Search Result: {clean_text[:300]}..."
            
            # Fallback: look for any substantial text blocks
            text_blocks = re.findall(r'<p[^>]*>([^<]{50,})</p>', html)
            for block in text_blocks:
                clean_text = re.sub(r'<[^>]+>', '', block).strip()
                if query.lower() in clean_text.lower():
                    return f"Web Information: {clean_text[:250]}..."
        
        except Exception as e:
            logging.error(f"Error parsing search results: {e}")
        
        return None
    
    def _format_tech_query(self, query: str) -> str:
        """Format query for better technical search results"""
        # Add common technical terms
        tech_terms = [
            "troubleshooting", "fix", "solution", "error", "problem",
            "computer", "windows", "software", "hardware"
        ]
        
        query_lower = query.lower()
        
        # If it's already technical, return as is
        if any(term in query_lower for term in tech_terms):
            return query
        
        # Add context for better results
        if "internet" in query_lower or "network" in query_lower:
            return f"{query} network troubleshooting fix"
        elif "slow" in query_lower or "performance" in query_lower:
            return f"{query} computer performance troubleshooting"
        elif "startup" in query_lower or "boot" in query_lower:
            return f"{query} computer startup troubleshooting"
        else:
            return f"{query} computer troubleshooting solution"
    
    def _is_technical_query(self, query: str) -> bool:
        """Check if query is technical in nature"""
        technical_keywords = [
            'error', 'bug', 'crash', 'freeze', 'slow', 'performance',
            'network', 'internet', 'wifi', 'connection', 'hardware',
            'software', 'driver', 'update', 'install', 'troubleshoot',
            'fix', 'repair', 'startup', 'boot', 'blue screen', 'bsod'
        ]
        
        return any(keyword in query.lower() for keyword in technical_keywords)
    
    def _get_common_solution(self, query: str) -> Optional[str]:
        """Get common solutions for frequent issues"""
        common_solutions = {
            'internet': """
Common internet troubleshooting steps:
1. Check your router/modem - ensure all cables are connected and power lights are on
2. Restart your router by unplugging for 30 seconds
3. Check if other devices can connect to the internet
4. Run Windows Network Troubleshooter
5. Reset network settings: Open Command Prompt as admin and run:
   - ipconfig /release
   - ipconfig /flushdns
   - ipconfig /renew
6. Check DNS settings - try using 8.8.8.8 or 1.1.1.1
7. Disable and re-enable your network adapter
8. Update network drivers
""",
            'slow': """
Computer performance troubleshooting:
1. Check Task Manager for high CPU/Memory usage programs
2. Disable startup programs you don't need
3. Run Disk Cleanup to free up space
4. Check for malware with Windows Defender or Malwarebytes
5. Update drivers and Windows
6. Check hard drive health with chkdsk
7. Consider adding more RAM if usage is consistently high
8. Restart your computer regularly
""",
            'startup': """
Startup/Boot troubleshooting:
1. Try Safe Mode - hold F8 during startup
2. Check power connections and cables
3. Remove recently installed hardware/software
4. Run System File Checker: sfc /scannow
5. Use Windows Startup Repair
6. Check BIOS/UEFI settings
7. Test with minimal hardware configuration
8. Check hard drive for errors
""",
            'network': """
Network troubleshooting steps:
1. Check physical connections (cables, WiFi signal)
2. Restart networking equipment
3. Update network drivers
4. Check firewall and antivirus settings
5. Reset TCP/IP stack
6. Check IP configuration
7. Test with different DNS servers
8. Disable VPN if active
"""
        }
        
        query_lower = query.lower()
        
        for key, solution in common_solutions.items():
            if key in query_lower:
                return solution.strip()
        
        return None

# ==================== DOCUMENT PROCESSOR ====================
class DocumentProcessor:
    """Enhanced document processing plugin"""
    
    def __init__(self, config: Config):
        self.config = config
        self.enabled = DOCUMENT_OK
        self.supported_formats = ['.pdf', '.docx', '.txt']
    
    def process_document(self, file_path: str) -> Optional[str]:
        """Process various document formats"""
        if not self.enabled:
            return None
        
        try:
            file_ext = Path(file_path).suffix.lower()
            
            if file_ext == '.pdf':
                return self._process_pdf(file_path)
            elif file_ext == '.docx':
                return self._process_docx(file_path)
            elif file_ext == '.txt':
                return self._process_txt(file_path)
            else:
                return f"Unsupported file format: {file_ext}"
                
        except Exception as e:
            logging.error(f"Document processing error: {e}")
            return None
    
    def _process_pdf(self, file_path: str) -> str:
        """Process PDF files"""
        try:
            text = ""
            with open(file_path, 'rb') as file:
                pdf_reader = PyPDF2.PdfReader(file)
                for page in pdf_reader.pages:
                    text += page.extract_text() + "\n"
            return text.strip()
        except Exception as e:
            return f"Error processing PDF: {e}"
    
    def _process_docx(self, file_path: str) -> str:
        """Process DOCX files"""
        try:
            doc = docx.Document(file_path)
            text = ""
            for paragraph in doc.paragraphs:
                text += paragraph.text + "\n"
            return text.strip()
        except Exception as e:
            return f"Error processing DOCX: {e}"
    
    def _process_txt(self, file_path: str) -> str:
        """Process text files"""
        try:
            with open(file_path, 'r', encoding='utf-8') as file:
                return file.read()
        except Exception as e:
            return f"Error processing text file: {e}"

# ==================== MAIN WHISPERBLADE SYSTEM ====================
class WhisperBladeUltimate:
    """Enhanced WhisperBlade Ultimate System"""
    
    def __init__(self, config: Config = None):
        self.config = config or Config()
        self._setup_logging()
        self._init_components()
        self.session_stats = {
            'queries_processed': 0,
            'avg_response_time': 0.0,
            'success_rate': 0.0,
            'start_time': datetime.now()
        }
    
    def _setup_logging(self):
        """Setup enhanced logging"""
        logging.basicConfig(
            level=getattr(logging, self.config.LOG_LEVEL),
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler('whisperblade_enhanced.log', encoding='utf-8'),
                logging.StreamHandler()
            ]
        )
        self.logger = logging.getLogger(__name__)
    
    def _init_components(self):
        """Initialize all system components"""
        self.logger.info("Initializing WhisperBlade Ultimate Enhanced...")
        
        # Core components
        self.knowledge_engine = AdvancedKnowledgeEngine(self.config)
        self.hardware_monitor = EnhancedHardwareMonitor(self.config)
        self.voice_interface = EnhancedVoiceInterface(self.config)
        
        # Plugins
        self.web_search = EnhancedWebSearchPlugin(self.config)
        self.document_processor = DocumentProcessor(self.config)
        
        self.logger.info("All components initialized successfully")
    
    async def process_async(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """Asynchronous request processing"""
        start_time = time.time()
        
        try:
            # Extract request parameters
            query = request.get('query', '')
            lang = request.get('lang', 'en')
            user_id = request.get('user_id')
            input_type = request.get('type', 'text')  # text, voice, hardware
            
            # Process different input types
            if input_type == 'voice':
                # Voice input
                spoken_query = await self.voice_interface.listen_async(lang)
                if not spoken_query:
                    return {'error': 'Voice recognition failed', 'success': False}
                query = spoken_query
            
            elif input_type == 'hardware':
                # Hardware diagnostic request
                health_report = self.hardware_monitor.generate_health_report(lang)
                return {
                    'answer': health_report,
                    'source': 'hardware_monitor',
                    'confidence': 1.0,
                    'response_time': time.time() - start_time,
                    'lang': lang,
                    'success': True
                }
            
            if not query:
                return {'error': 'No query provided', 'success': False}
            
            # Process through knowledge engine
            result = self.knowledge_engine.search(query, lang, user_id)
            
            # If no good match, try web search
            if result.confidence < 0.5:
                web_result = await self.web_search.search_async(query, lang)
                if web_result:
                    result = QueryResult(
                        answer=web_result,
                        source='web_search',
                        confidence=0.7,
                        response_time=time.time() - start_time,
                        lang=lang
                    )
            
            # Update session statistics
            self._update_session_stats(result)
            
            # Prepare response
            response = {
                'answer': result.answer,
                'source': result.source,
                'confidence': result.confidence,
                'response_time': result.response_time,
                'lang': lang,
                'suggestions': result.suggestions,
                'support_info': self.config.SUPPORT_CONTACT,
                'success': True
            }
            
            # Voice output if requested
            if request.get('voice_output', False):
                await self.voice_interface.speak_async(result.answer, lang)
            
            return response
            
        except Exception as e:
            self.logger.error(f"Processing error: {e}")
            return {
                'error': str(e),
                'success': False,
                'response_time': time.time() - start_time
            }
    
    def process_sync(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """Synchronous request processing for compatibility"""
        return asyncio.run(self.process_async(request))
    
    def _update_session_stats(self, result: QueryResult):
        """Update session statistics"""
        self.session_stats['queries_processed'] += 1
        
        # Update average response time
        current_avg = self.session_stats['avg_response_time']
        count = self.session_stats['queries_processed']
        self.session_stats['avg_response_time'] = (
            (current_avg * (count - 1) + result.response_time) / count
        )
        
        # Update success rate
        success = result.confidence > 0.5
        current_success_rate = self.session_stats['success_rate']
        self.session_stats['success_rate'] = (
            (current_success_rate * (count - 1) + (1 if success else 0)) / count
        )
    
    def get_session_stats(self) -> Dict[str, Any]:
        """Get current session statistics"""
        uptime = datetime.now() - self.session_stats['start_time']
        return {
            **self.session_stats,
            'uptime_seconds': uptime.total_seconds(),
            'system_health': self.hardware_monitor.get_system_health(),
            'health_alerts': self.hardware_monitor.get_health_alerts()
        }
    
    def add_knowledge_entry(self, entry: KnowledgeEntry) -> bool:
        """Add new knowledge entry"""
        try:
            success = self.knowledge_engine.db.save_entry(entry)
            if success:
                # Rebuild indices and embeddings
                self.knowledge_engine._build_indices()
                if self.knowledge_engine.semantic_model:
                    self.knowledge_engine._build_semantic_embeddings()
                self.logger.info(f"Added knowledge entry: {entry.id}")
            return success
        except Exception as e:
            self.logger.error(f"Error adding knowledge entry: {e}")
            return False
    
    def backup_knowledge_base(self, backup_path: str) -> bool:
        """Backup knowledge base to file"""
        try:
            import shutil
            shutil.copy2(self.config.DB_PATH, backup_path)
            self.logger.info(f"Knowledge base backed up to: {backup_path}")
            return True
        except Exception as e:
            self.logger.error(f"Backup failed: {e}")
            return False

# ==================== MAIN ENTRY POINT ====================
async def main():
    """Main entry point for testing"""
    print("🚀 WhisperBlade Ultimate Enhanced - Starting...")
    
    # Initialize system
    config = Config()
    system = WhisperBladeUltimate(config)
    
    # Test queries
    test_queries = [
        {'query': 'startup problem', 'lang': 'en', 'type': 'text'},
        {'query': 'इन्टरनेट छैन', 'lang': 'np', 'type': 'text'},
        {'query': 'slow computer performance', 'lang': 'en', 'type': 'text'},
        {'type': 'hardware'},
        {'query': 'error code 0x800F0922', 'lang': 'en', 'type': 'text'}
    ]
    
    print("\n" + "="*60)
    print("🧠 WHISPERBLADE ULTIMATE ENHANCED - TEST SUITE")
    print("="*60)
    
    for i, query in enumerate(test_queries, 1):
        print(f"\n🔍 Test {i}: {query}")
        print("-" * 50)
        
        try:
            response = await system.process_async(query)
            
            if response.get('success'):
                print(f"✅ Answer: {response['answer'][:200]}...")
                print(f"📊 Source: {response['source']}")
                print(f"🎯 Confidence: {response['confidence']:.2f}")
                print(f"⏱️ Response Time: {response['response_time']:.3f}s")
                
                if response.get('suggestions'):
                    print(f"💡 Suggestions: {', '.join(response['suggestions'])}")
            else:
                print(f"❌ Error: {response.get('error', 'Unknown error')}")
                
        except Exception as e:
            print(f"💥 Exception: {e}")
    
    # Display session statistics
    print("\n" + "="*60)
    print("📈 SESSION STATISTICS")
    print("="*60)
    
    stats = system.get_session_stats()
    print(f"Queries Processed: {stats['queries_processed']}")
    print(f"Average Response Time: {stats['avg_response_time']:.3f}s")
    print(f"Success Rate: {stats['success_rate']:.2%}")
    print(f"Uptime: {stats['uptime_seconds']:.1f} seconds")
    
    if stats['health_alerts']:
        print(f"\n⚠️ Health Alerts: {len(stats['health_alerts'])}")
        for alert in stats['health_alerts']:
            print(f"  • {alert}")
    else:
        print("\n✅ No health alerts")

def handle_app_request(request: Dict[str, Any]) -> Dict[str, Any]:
    """Legacy compatibility function"""
    config = Config()
    system = WhisperBladeUltimate(config)
    return system.process_sync(request)

if __name__ == '__main__':
    # Set UTF-8 encoding for Windows
    import sys
    if sys.platform == 'win32':
        import os
        os.system('chcp 65001 > nul')
    
    # Run main function
    asyncio.run(main())
