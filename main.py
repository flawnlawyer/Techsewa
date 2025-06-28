import os
import json
import queue
import re
import time
import threading
from functools import lru_cache
import sounddevice as sd
import pyttsx3
from vosk import Model, KaldiRecognizer
from fuzzywuzzy import fuzz
import subprocess
import psutil  # For advanced diagnostics with fallbacks

# ========== CONFIGURATION ==========
class Config:
    """Centralized configuration with intelligent defaults"""
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    MODEL_DIR = os.path.join(BASE_DIR, "Model")
    PROBLEM_DB = os.path.join(BASE_DIR, "problems.json")
    UNMATCHED_LOG = os.path.join(BASE_DIR, "unmatched_queries.log")
    SETTINGS_FILE = os.path.join(BASE_DIR, "config.json")
    
    # Default settings
    MAX_LISTEN_SECONDS = 10
    MIN_CONFIDENCE = 75
    ENABLE_EASTER_EGGS = True
    ENABLE_VOICE = True
    ENABLE_DIAGNOSTICS = True
    ENABLE_ADVANCED_DIAGNOSTICS = True  # New setting for advanced metrics
    
    @classmethod
    def load(cls):
        """Load settings from config file or use defaults"""
        try:
            if os.path.exists(cls.SETTINGS_FILE):
                with open(cls.SETTINGS_FILE, 'r') as f:
                    settings = json.load(f)
                    cls.MAX_LISTEN_SECONDS = settings.get('max_listen_seconds', 10)
                    cls.MIN_CONFIDENCE = settings.get('min_confidence', 75)
                    cls.ENABLE_EASTER_EGGS = settings.get('enable_easter_eggs', True)
                    cls.ENABLE_VOICE = settings.get('enable_voice', True)
                    cls.ENABLE_DIAGNOSTICS = settings.get('enable_diagnostics', True)
                    cls.ENABLE_ADVANCED_DIAGNOSTICS = settings.get('enable_advanced_diagnostics', True)
            else:
                cls.create_default_config()
        except Exception as e:
            print(f"⚠️ Config error: {e}")
            cls.create_default_config()

    @classmethod
    def create_default_config(cls):
        """Generate robust default configuration"""
        default_config = {
            "max_listen_seconds": 10,
            "min_confidence": 75,
            "enable_easter_eggs": True,
            "enable_voice": True,
            "enable_diagnostics": True,
            "enable_advanced_diagnostics": True
        }
        try:
            with open(cls.SETTINGS_FILE, 'w') as f:
                json.dump(default_config, f, indent=2)
            print("ℹ️ Created default config file")
        except Exception as e:
            print(f"⚠️ Couldn't create config: {e}")

Config.load()

# Model paths with validation
EN_MODEL_PATH = os.path.join(Config.MODEL_DIR, "vosk-model-small-en-us-0.15")
HI_MODEL_PATH = os.path.join(Config.MODEL_DIR, "vosk-model-small-hi-0.22")

# Contact information (centralized)
CONTACT_INFO = {
    'en': "\n📍 Visit: Learning Mission and Training Center, Thuphandanda, Dadeldhura\n"
          "📞 Phone: 9867315931\n📧 Email: learnermission@gmail.com",
    'np': "\n📍 कृपया सम्पर्क गर्नुहोस्: Learning Mission, थुपनडाँडा, डडेलधुरा\n"
          "📞 फोन: ९८६७३१५९३१\n📧 इमेल: learnermission@gmail.com"
}

# Nepali keywords for enhanced detection
NEPALI_KEYPHRASES = [
    'इन्टरनेट', 'चल्दैन', 'कम्प्युटर', 'फोन', 'समस्या', 'छ',
    'भएको', 'मर्मत', 'कृपया', 'सहयोग', 'गर्नुहोस्', 'हुन्छ'
]

# ========== CORE COMPONENTS ==========
class AudioProcessor:
    """Advanced audio handling with thread safety"""
    def __init__(self, sample_rate=16000):
        self.sample_rate = sample_rate
        self.queue = queue.Queue()
        self.stream = None
        self.listening = False
        self.lock = threading.Lock()

    def callback(self, indata, frames, time, status):
        """Thread-safe audio callback"""
        with self.lock:
            if self.listening:
                self.queue.put(bytes(indata))

    def start_stream(self):
        """Initialize audio stream with error handling"""
        try:
            self.stream = sd.RawInputStream(
                samplerate=self.sample_rate,
                blocksize=8000,
                dtype='int16',
                channels=1,
                callback=self.callback
            )
            self.stream.start()
        except Exception as e:
            print(f"⚠️ Audio stream error: {e}")

    def stop_stream(self):
        """Graceful stream shutdown"""
        if self.stream:
            try:
                self.stream.stop()
                self.stream.close()
            except:
                pass

    def get_audio(self, timeout):
        """Get audio data with timeout protection"""
        self.listening = True
        audio_data = b""
        start_time = time.time()
        
        while time.time() - start_time < timeout:
            try:
                with self.lock:
                    audio_data += self.queue.get_nowait()
            except queue.Empty:
                time.sleep(0.05)
        
        self.listening = False
        return audio_data

class LanguageProcessor:
    """Enhanced language detection with mixed input support"""
    def __init__(self):
        self.nepali_script_range = range(0x0900, 0x097F + 1)
        
    def detect(self, text):
        """Advanced detection with threshold tuning"""
        if not text.strip():
            return 'en'
            
        devanagari_count = sum(1 for ch in text if ord(ch) in self.nepali_script_range)
        ratio = devanagari_count / max(len(text), 1)
        
        # Strong Nepali indicators
        if ratio > 0.3:
            return 'np'
        if any(kw in text.lower() for kw in NEPALI_KEYPHRASES):
            return 'np'
        
        # Mixed language handling
        if 0.1 < ratio <= 0.3 and len(text.split()) > 3:
            return 'np'
            
        return 'en'

class ProblemSolver:
    """Optimized problem matching with new JSON structure"""
    def __init__(self, problem_db):
        self.problems = problem_db
        self.alias_map = self._build_alias_map()
        
    def _build_alias_map(self):
        """Create efficient alias lookup structure"""
        alias_map = {}
        for idx, problem in enumerate(self.problems):
            for alias in problem['aliases']:
                alias_map[alias.lower()] = idx
        return alias_map
    
    @lru_cache(maxsize=100)
    def match(self, text, lang='en'):
        """Hybrid matching with exact and fuzzy search"""
        text = text.lower().strip()
        
        # Exact match first
        for word in text.split():
            if word in self.alias_map:
                return self.problems[self.alias_map[word]][lang]
        
        # Fuzzy matching with threshold
        best_match, best_score = None, 0
        for problem in self.problems:
            for alias in problem['aliases']:
                score = fuzz.token_set_ratio(text, alias.lower())
                if score > best_score and score >= Config.MIN_CONFIDENCE:
                    best_match = problem[lang]
                    best_score = score
        
        return best_match

class TTSService:
    """Enhanced TTS with voice management"""
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            try:
                cls._instance.engine = pyttsx3.init()
                cls._instance.engine.setProperty('rate', 145)
                
                # Configure voice
                voices = cls._instance.engine.getProperty('voices')
                nepali_voices = [v for v in voices 
                               if 'hindi' in v.name.lower() or 'nepali' in v.name.lower()]
                if nepali_voices:
                    cls._instance.engine.setProperty('voice', nepali_voices[0].id)
            except Exception as e:
                print(f"⚠️ TTS initialization failed: {e}")
                cls._instance.engine = None
                
        return cls._instance
    
    def speak(self, text):
        """Safe speech output with error handling"""
        if not Config.ENABLE_VOICE or not self.engine:
            return
            
        try:
            clean_text = re.sub(r'[^\w\s\u0900-\u097F]', '', text)
            self.engine.say(clean_text)
            self.engine.runAndWait()
        except Exception as e:
            print(f"⚠️ TTS Error: {e}")

class SystemDiagnostics:
    """Comprehensive system diagnostics with fallbacks"""
    
    @staticmethod
    def check_internet():
        """Robust internet connectivity check"""
        try:
            subprocess.check_call(["ping", "-n", "1", "8.8.8.8"], 
                                stdout=subprocess.DEVNULL, 
                                stderr=subprocess.DEVNULL)
            return "✅ Internet connection working"
        except:
            return "❌ No internet connection"

    @staticmethod
    def check_wifi():
        """Windows-specific WiFi status check"""
        try:
            output = subprocess.check_output(
                "netsh wlan show interfaces", 
                shell=True, 
                stderr=subprocess.DEVNULL
            ).decode()
            return "✅ WiFi connected" if re.search(r"State\s+:\s+connected", output) else "❌ WiFi disconnected"
        except:
            return "⚠️ Could not determine WiFi status"

    @staticmethod
    def check_cpu_memory():
        """CPU and memory usage with fallback"""
        try:
            cpu = psutil.cpu_percent(interval=1)
            mem = psutil.virtual_memory()
            return f"🧠 CPU: {cpu}% | RAM: {mem.percent}% used"
        except:
            return "⚠️ Could not check CPU/memory"

    @staticmethod
    def check_disk():
        """Disk usage with fallback"""
        try:
            disk = psutil.disk_usage('/')
            total_gb = disk.total // (1024 ** 3)
            return f"💽 Disk: {disk.percent}% used of {total_gb}GB"
        except:
            return "⚠️ Could not check disk usage"

    @staticmethod
    def check_temperature():
        """Temperature monitoring with fallback"""
        try:
            temps = psutil.sensors_temperatures()
            if temps:
                for name, entries in temps.items():
                    if entries:
                        return f"🌡️ {name}: {entries[0].current}°C"
            return "🌡️ Temperature info not available"
        except:
            return "⚠️ Could not check temperature"

    @staticmethod
    def run_all():
        """Run all diagnostics with timing and fallbacks"""
        start_time = time.time()
        basic_results = [
            SystemDiagnostics.check_internet(),
            SystemDiagnostics.check_wifi()
        ]
        
        advanced_results = []
        if Config.ENABLE_ADVANCED_DIAGNOSTICS:
            advanced_results = [
                SystemDiagnostics.check_cpu_memory(),
                SystemDiagnostics.check_disk(),
                SystemDiagnostics.check_temperature()
            ]
        
        results = basic_results + advanced_results + [
            f"⏱️ Diagnostics completed in {time.time() - start_time:.2f} seconds"
        ]
        return results

# ========== MAIN APPLICATION ==========
class TechsewaAssistant:
    """Main application class with enhanced features"""
    def __init__(self):
        self.resources = self.load_resources()
        if not self.resources:
            raise RuntimeError("❌ Failed to load required resources")
            
        self.tts = TTSService()
        self.audio = AudioProcessor()
        self.lang_processor = LanguageProcessor()
        self.problem_solver = ProblemSolver(self.resources['problems'])
        self.running = False

    def load_resources(self):
        """Robust resource loading with validation"""
        try:
            # Load problem database
            with open(Config.PROBLEM_DB, "r", encoding='utf-8') as f:
                problems = json.load(f)
                if not isinstance(problems, list):
                    raise ValueError("Invalid problem database format")
            
            # Verify model directories
            if not all(os.path.isdir(p) for p in [EN_MODEL_PATH, HI_MODEL_PATH]):
                raise FileNotFoundError("Model directories not found")
            
            return {
                'problems': problems,
                'model_en': Model(EN_MODEL_PATH),
                'model_hi': Model(HI_MODEL_PATH)
            }
        except Exception as e:
            print(f"❌ Resource loading failed: {e}")
            return None
            
    def handle_input(self, mode='voice'):
        """Flexible input handling with validation"""
        if mode == 'keyboard':
            user_input = input("⌨️ Describe your problem: ").strip()
            while not user_input:
                print("⚠️ Please enter a valid description")
                user_input = input("⌨️ Describe your problem: ").strip()
            return user_input
            
        elif mode == 'voice':
            print("\n🔊 Listening... (Speak now)")
            audio_data = self.audio.get_audio(Config.MAX_LISTEN_SECONDS)
            
            if not audio_data:
                print("⏱️ Listening timeout")
                return None
                
            result = json.loads(self.recognizer.Result())
            return result.get("text", "").strip()
            
        return None
        
    def run_diagnostics(self):
        """Comprehensive diagnostic mode"""
        if not Config.ENABLE_DIAGNOSTICS:
            return "Diagnostics are disabled in config"
            
        print("\n🛠️ Running system diagnostics...")
        results = SystemDiagnostics.run_all()
        report = "\n".join(results)
        print(report)
        self.tts.speak("System diagnostics completed. " + ". ".join(r.replace("✅", "").replace("❌", "Error") for r in results[:2]))
        return report

    def run(self):
        """Main application loop with enhanced features"""
        print("\n" + "="*50)
        print("🚀 Techsewa Assistant - V3 Professional Edition")
        print("="*50 + "\n")
        
        # Initialize components
        self.recognizer = KaldiRecognizer(self.resources['model_en'], 16000)
        self.current_lang = 'en'
        self.audio.start_stream()
        self.running = True
        
        # Welcome message
        welcome_msg = {
            'visual': "🙏 नमस्ते! Techsewa मा स्वागत छ\n🙏 Welcome to Techsewa V3",
            'spoken': "नमस्ते! Techsewa मा स्वागत छ. Welcome to Techsewa V3"
        }
        print(welcome_msg['visual'])
        self.tts.speak(welcome_msg['spoken'])
        
        try:
            while self.running:
                # Enhanced input prompt
                mode = input("\n🎤 [Enter=speak, k=keyboard, d=diagnostics, q=quit]: ").strip().lower()
                
                if mode == 'q':
                    self.running = False
                    continue
                    
                if mode == 'd':
                    self.run_diagnostics()
                    continue
                    
                # Get user input
                user_input = self.handle_input('keyboard' if mode == 'k' else 'voice')
                if not user_input:
                    continue
                    
                print(f"\n👤 You: {user_input}")
                
                # Easter egg handling
                if Config.ENABLE_EASTER_EGGS and "messi" in user_input.lower():
                    msg = "MESSI MESSI MESSI 🐐 — The GOAT doesn't fix problems, he creates magic!"
                    print(f"\n🎉 {msg}")
                    self.tts.speak(msg)
                    continue
                
                # Language processing
                detected_lang = self.lang_processor.detect(user_input)
                if detected_lang != self.current_lang:
                    self.current_lang = detected_lang
                    self.recognizer = KaldiRecognizer(
                        self.resources['model_hi'] if self.current_lang == 'np' 
                        else self.resources['model_en'], 
                        16000
                    )
                    print(f"🌐 Language switched to: {'नेपाली' if self.current_lang == 'np' else 'English'}")
                
                # Problem resolution
                solution = self.problem_solver.match(user_input, self.current_lang)
                
                if solution:
                    response = f"{solution}\n{CONTACT_INFO[self.current_lang]}"
                else:
                    response = (
                        "माफ गर्नुहोस्, म तपाईंको समस्या बुझ्न सकिन।\n"
                        if self.current_lang == 'np' else
                        "Sorry, I couldn't understand your problem.\n"
                    ) + CONTACT_INFO[self.current_lang]
                    self.log_unmatched(user_input, self.current_lang)
                
                # Present response
                print(f"\n🤖 Techsewa:\n{response}")
                self.tts.speak(response)
                
        except KeyboardInterrupt:
            print("\n🛑 Shutdown requested...")
        except Exception as e:
            print(f"\n❌ Fatal error: {e}")
            self.tts.speak("A serious error occurred. Please restart the application.")
        finally:
            self.cleanup()

    def log_unmatched(self, text, lang):
        """Enhanced logging for unmatched queries"""
        try:
            timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
            with open(Config.UNMATCHED_LOG, "a", encoding='utf-8') as f:
                f.write(f"[{timestamp}] {lang.upper()}: {text}\n")
        except Exception as e:
            print(f"⚠️ Failed to log query: {e}")

    def cleanup(self):
        """Comprehensive resource cleanup"""
        self.running = False
        self.audio.stop_stream()
        print("\n🛑 Shutting down Techsewa Assistant...")
        farewell_msg = {
            'visual': "धन्यवाद! Techsewa प्रयोग गर्नुभएकोमा।\nThank you for using Techsewa!",
            'spoken': "धन्यवाद! Techsewa प्रयोग गर्नुभएकोमा। Thank you for using Techsewa."
        }
        print(farewell_msg['visual'])
        self.tts.speak(farewell_msg['spoken'])

if __name__ == "__main__":
    # Initialize default config if missing
    if not os.path.exists(Config.SETTINGS_FILE):
        Config.create_default_config()
    
    # Run application with error handling
    try:
        assistant = TechsewaAssistant()
        assistant.run()
    except Exception as e:
        print(f"❌ Failed to start Techsewa: {e}")