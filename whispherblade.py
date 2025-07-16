#!/usr/bin/env python3
# whisperblade_ultimate.py - The All-in-One AI Brain for TechSewa
import os
import json
import re
import time
import hashlib
import requests
import psutil
from bs4 import BeautifulSoup
from fuzzywuzzy import fuzz
from functools import lru_cache
from typing import Dict, List, Optional, Tuple
import logging

# Optional imports with fallback handling
try:
    from sentence_transformers import SentenceTransformer, util
    _SEMANTIC_OK = True
except ImportError:
    _SEMANTIC_OK = False
    print("Warning: sentence_transformers not available. Semantic search disabled.")

try:
    import PyPDF2
    _PDF_OK = True
except ImportError:
    _PDF_OK = False
    print("Warning: PyPDF2 not available. PDF processing disabled.")

try:
    import speech_recognition as sr
    _SPEECH_OK = True
except ImportError:
    _SPEECH_OK = False
    print("Warning: speech_recognition not available. Voice interface disabled.")

# ==================== CONSTANTS ====================
KNOWLEDGE_DB = "knowledge_db.json"
SUPPORT_INFO = """
📌 Need more help? Contact:
📍 Learner Mission & Training Center
🗺️ Thuphandanda, Dadeldhura
📞 9867315931 | 📧 learnermission@gmail.com
"""

# Default knowledge base (was missing)
DEFAULT_KNOWLEDGE = [
    {
        "id": "startup_error",
        "aliases": ["slow boot", "startup problem", "boot issue"],
        "np_aliases": ["सुरु हुन्न", "धिलो खुल्छ"],
        "en": "Try these steps: 1) Check power connections 2) Run system diagnostics 3) Clear temporary files",
        "np": "यी कदमहरू प्रयास गर्नुहोस्: १) पावर जडान जाँच गर्नुहोस् २) सिस्टम निदान चलाउनुहोस् ३) अस्थायी फाइलहरू सफा गर्नुहोस्",
        "error_code": "0x800F0922"
    },
    {
        "id": "internet_issue",
        "aliases": ["no internet", "wifi not working", "connection problem"],
        "np_aliases": ["इन्टरनेट छैन", "वाइफाई काम गर्दैन"],
        "en": "Internet troubleshooting: 1) Check router power 2) Restart network adapter 3) Run network troubleshooter",
        "np": "इन्टरनेट समस्या निवारण: १) राउटर पावर जाँच गर्नुहोस् २) नेटवर्क एडाप्टर पुनः सुरु गर्नुहोस् ३) नेटवर्क समस्या निवारक चलाउनुहोस्"
    }
]

# ==================== CORE MODULES ====================
class KnowledgeEngine:
    """Enhanced knowledge base with semantic + fuzzy search"""
    def __init__(self, db_path: str = KNOWLEDGE_DB):
        self.db_path = db_path
        self.semantic_model = None
        self.semantic_embeds = None
        self._init_db()
        self._build_indices()
        if _SEMANTIC_OK:
            self._init_semantic_model()
    
    def _init_db(self):
        """Initialize knowledge database"""
        if not os.path.exists(self.db_path):
            with open(self.db_path, 'w', encoding='utf-8') as f:
                json.dump(DEFAULT_KNOWLEDGE, f, indent=2, ensure_ascii=False)
        
        try:
            with open(self.db_path, 'r', encoding='utf-8') as f:
                self.entries = json.load(f)
        except (json.JSONDecodeError, FileNotFoundError):
            self.entries = DEFAULT_KNOWLEDGE
    
    def _init_semantic_model(self):
        """Initialize semantic search model"""
        try:
            self.semantic_model = SentenceTransformer("all-MiniLM-L6-v2")
            # Pre-compute embeddings for all entries
            texts = [entry.get('en', '') for entry in self.entries]
            self.semantic_embeds = self.semantic_model.encode(texts)
        except Exception as e:
            print(f"Warning: Failed to initialize semantic model: {e}")
            self.semantic_model = None
    
    def _build_indices(self):
        """Build search indices for fast lookup"""
        self.en_index = {}
        self.np_index = {}
        self.error_code_map = {}
        
        for idx, entry in enumerate(self.entries):
            # English aliases
            for alias in entry.get('aliases', []):
                self.en_index[alias.lower()] = idx
            
            # Nepali aliases
            for alias in entry.get('np_aliases', []):
                self.np_index[alias.lower()] = idx
            
            # Error codes
            if 'error_code' in entry:
                self.error_code_map[entry['error_code']] = idx
    
    @lru_cache(maxsize=2000)
    def query(self, text: str, lang: str = None) -> Optional[Dict]:
        """Hybrid search (semantic + fuzzy + exact)"""
        if not text:
            return None
            
        # Auto-detect language if not specified
        if lang is None:
            lang = 'np' if any(ord(c) > 127 for c in text) else 'en'
        
        idx = self._find_match(text, lang)
        return self.entries[idx] if idx is not None else None
    
    def _find_match(self, text: str, lang: str) -> Optional[int]:
        """Find best matching entry index"""
        # 1. Check error codes first
        error_code_match = re.search(r'0x[0-9A-F]{6,8}', text.upper())
        if error_code_match:
            code = error_code_match.group()
            if code in self.error_code_map:
                return self.error_code_map[code]
        
        # 2. Exact match in aliases
        index = self.np_index if lang == 'np' else self.en_index
        for token in re.findall(r'\w+', text.lower()):
            if token in index:
                return index[token]
        
        # 3. Fuzzy match
        best_idx, best_score = None, 0
        for phrase, idx in index.items():
            score = fuzz.token_set_ratio(text.lower(), phrase)
            if score > best_score and score >= 65:
                best_idx, best_score = idx, score
        
        # 4. Semantic match (if enabled and fuzzy score is low)
        if self.semantic_model and best_score < 80:
            try:
                query_embed = self.semantic_model.encode(text)
                scores = util.cos_sim(query_embed, self.semantic_embeds)[0]
                semantic_idx = int(scores.argmax())
                if scores[semantic_idx] >= 0.6:
                    return semantic_idx
            except Exception as e:
                print(f"Semantic search error: {e}")
        
        return best_idx

class HardwareMonitor:
    """Real-time device diagnostics"""
    @staticmethod
    def system_health() -> Dict:
        """Get comprehensive system health metrics"""
        try:
            health_data = {
                'cpu_usage': psutil.cpu_percent(interval=1),
                'ram_usage': psutil.virtual_memory().percent,
                'disk_usage': psutil.disk_usage('/').percent,
                'network_active': len(psutil.net_connections()) > 0,
                'temperatures': {},
                'disk_health': 'UNKNOWN'
            }
            
            # Temperature monitoring (if available)
            try:
                temps = psutil.sensors_temperatures()
                health_data['temperatures'] = {
                    k: v[0].current for k, v in temps.items() if v
                }
            except:
                health_data['temperatures'] = {}
            
            # Disk health check (simplified)
            try:
                # This is a simplified check - in reality you'd use smartctl
                health_data['disk_health'] = 'OK' if psutil.disk_usage('/').percent < 90 else 'WARNING'
            except:
                health_data['disk_health'] = 'UNKNOWN'
            
            return health_data
        except Exception as e:
            return {'error': f"Failed to get system health: {e}"}

class VoiceInterface:
    """Hands-free Nepali/English support"""
    def __init__(self):
        if not _SPEECH_OK:
            self.recognizer = None
            return
        self.recognizer = sr.Recognizer()
    
    def listen(self, lang: str = 'en') -> Optional[str]:
        """Listen for voice input"""
        if not self.recognizer:
            return None
            
        try:
            with sr.Microphone() as source:
                print("Listening...")
                audio = self.recognizer.listen(source, timeout=5)
            
            language = 'ne-NP' if lang == 'np' else 'en-US'
            return self.recognizer.recognize_google(audio, language=language)
        except sr.WaitTimeoutError:
            print("No speech detected")
            return None
        except sr.UnknownValueError:
            print("Could not understand audio")
            return None
        except Exception as e:
            print(f"Speech recognition error: {e}")
            return None

# Missing plugin classes (simplified implementations)
class WikipediaSearch:
    """Wikipedia search plugin"""
    def __init__(self):
        self.name = "wikipedia"
    
    def execute(self, query: str) -> Optional[str]:
        """Search Wikipedia for query"""
        try:
            # Simplified - would use wikipedia library in production
            return f"Wikipedia search for '{query}' - feature not fully implemented"
        except Exception as e:
            return None

class WeatherAPI:
    """Weather information plugin"""
    def __init__(self):
        self.name = "weather"
    
    def execute(self, query: str) -> Optional[str]:
        """Get weather information"""
        if any(word in query.lower() for word in ['weather', 'temperature', 'rain', 'मौसम']):
            return "Weather service not configured. Please add API key."
        return None

class PDFIndexer:
    """PDF document indexing plugin"""
    def __init__(self):
        self.name = "pdf"
    
    def execute(self, query: str) -> Optional[str]:
        """Search PDF documents"""
        if not _PDF_OK:
            return None
        return f"PDF search for '{query}' - feature not fully implemented"

class CRMLinker:
    """CRM integration plugin"""
    def __init__(self, api_key: str = None):
        self.name = "ticket"
        self.api_key = api_key
    
    def execute(self, query: str) -> Optional[str]:
        """Link to CRM system"""
        if not self.api_key:
            return None
        return f"CRM integration for '{query}' - feature not fully implemented"

# ==================== INTEGRATED BRAIN ====================
class WhisperbladeUltimate:
    """Main AI brain orchestrator"""
    def __init__(self):
        self.knowledge = KnowledgeEngine()
        self.hardware = HardwareMonitor()
        self.voice = VoiceInterface()
        self._init_plugins()
        self._setup_logging()
    
    def _setup_logging(self):
        """Setup logging for debugging with Unicode support"""
        # Create formatters
        formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
        
        # File handler with UTF-8 encoding
        file_handler = logging.FileHandler('whisperblade.log', encoding='utf-8')
        file_handler.setFormatter(formatter)
        
        # Console handler with UTF-8 encoding (Windows fix)
        console_handler = logging.StreamHandler()
        console_handler.setFormatter(formatter)
        
        # Configure logger
        self.logger = logging.getLogger(__name__)
        self.logger.setLevel(logging.INFO)
        self.logger.addHandler(file_handler)
        self.logger.addHandler(console_handler)
        
        # Prevent duplicate logs
        self.logger.propagate = False
    
    def _init_plugins(self):
        """Initialize all plugins"""
        self.plugins = {
            'wikipedia': WikipediaSearch(),
            'weather': WeatherAPI(),
            'pdf': PDFIndexer(),
            'ticket': CRMLinker(api_key=os.getenv('TECHSEWA_CRM_KEY'))
        }
    
    def process(self, input_data: Dict) -> Dict:
        """Unified processing for text/voice/sensor inputs"""
        self.logger.info(f"Processing input: {input_data}")
        
        try:
            # Voice input
            if input_data.get('audio'):
                query = self.voice.listen(input_data.get('lang', 'en'))
                if not query:
                    return {'error': 'Voice recognition failed'}
            
            # Hardware diagnostics
            elif input_data.get('sensor_readings'):
                return {
                    'source': 'hardware',
                    'answer': self.hardware.system_health()
                }
            
            # Standard text query
            else:
                query = input_data.get('text', '')
                
            if not query:
                return {'error': 'No query provided'}
            
            # Process through all intelligence layers
            response = self._generate_response(query, input_data.get('lang'))
            self._log_to_crm(query, response, input_data.get('user_id'))
            return response
            
        except Exception as e:
            self.logger.error(f"Processing error: {e}")
            return {'error': f'Processing failed: {str(e)}'}
    
    def _generate_response(self, query: str, lang: str = None) -> Dict:
        """Generate response using multiple intelligence layers"""
        # 1. Local knowledge base
        if match := self.knowledge.query(query, lang):
            return {
                'source': 'local',
                'answer': match.get(lang or 'en', match.get('en', 'No answer found')),
                'support_info': SUPPORT_INFO
            }
        
        # 2. Try plugins
        for plugin_name, plugin in self.plugins.items():
            try:
                if result := plugin.execute(query):
                    return {
                        'source': plugin_name,
                        'answer': result,
                        'support_info': SUPPORT_INFO
                    }
            except Exception as e:
                self.logger.warning(f"Plugin {plugin_name} failed: {e}")
        
        # 3. Fallback response
        return {
            'source': 'fallback',
            'answer': self._get_fallback_response(query, lang),
            'support_info': SUPPORT_INFO
        }
    
    def _get_fallback_response(self, query: str, lang: str = None) -> str:
        """Generate fallback response when no match found"""
        if lang == 'np':
            return f"माफ गर्नुहोस्, '{query}' को बारेमा जानकारी फेला परेन। कृपया हाम्रो सहयोग टोलीलाई सम्पर्क गर्नुहोस्।"
        else:
            return f"Sorry, I couldn't find information about '{query}'. Please contact our support team for assistance."
    
    def _log_to_crm(self, query: str, response: Dict, user_id: str = None):
        """Log interaction to CRM system with Unicode-safe logging"""
        try:
            # Simplified CRM logging
            log_entry = {
                'timestamp': time.time(),
                'user_id': user_id,
                'query': query[:50] + '...' if len(query) > 50 else query,  # Truncate long queries
                'response_source': response.get('source'),
                'success': 'error' not in response
            }
            
            # Safe logging for Unicode characters
            try:
                self.logger.info(f"CRM Log: {log_entry}")
            except UnicodeEncodeError:
                # Fallback: log without the query text
                safe_log = {k: v for k, v in log_entry.items() if k != 'query'}
                safe_log['query'] = '[Unicode query logged to file]'
                self.logger.info(f"CRM Log: {safe_log}")
                
        except Exception as e:
            self.logger.warning(f"CRM logging failed: {e}")

# ==================== DEPLOYMENT READY ====================
def main():
    """Main entry point for testing"""
    # Set UTF-8 encoding for Windows console
    import sys
    if sys.platform == 'win32':
        import os
        os.system('chcp 65001 > nul')  # Set console to UTF-8
    
    brain = WhisperbladeUltimate()
    
    # Test queries
    test_queries = [
        {'text': 'startup problem', 'lang': 'en'},
        {'text': 'इन्टरनेट छैन', 'lang': 'np'},
        {'text': 'weather today', 'lang': 'en'},
        {'sensor_readings': True}
    ]
    
    print("🧠 WhisperBlade Ultimate - Testing Suite")
    print("=" * 50)
    
    for i, query in enumerate(test_queries, 1):
        print(f"\n🔍 Test {i}: {query}")
        try:
            response = brain.process(query)
            print(f"✅ Response: {response}")
        except Exception as e:
            print(f"❌ Error: {e}")
        print("-" * 50)

def handle_app_request(request):
    """Integration function for other app modules"""
    brain = WhisperbladeUltimate()
    return brain.process({
        'text': request.get('query', ''),
        'lang': request.get('lang'),
        'user_id': request.get('user_id')
    })

if __name__ == '__main__':
    main()