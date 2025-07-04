import os
import json
import queue
import re
import time
import threading
import subprocess
import platform
import traceback
from functools import lru_cache
from datetime import datetime
from typing import Optional, Dict, List

import sounddevice as sd
import pyttsx3
from vosk import Model, KaldiRecognizer
from fuzzywuzzy import fuzz
import psutil

# Local imports
from Brain import SmartBrain

# ============================ CONFIG ==============================
class Config:
    """Centralized runtime configuration with validation."""
    
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    MODEL_DIR = os.path.join(BASE_DIR, "Model")
    PROBLEM_DB = os.path.join(BASE_DIR, "problems.json")
    SETTINGS_FILE = os.path.join(BASE_DIR, "config.json")
    LOG_FILE = os.path.join(BASE_DIR, "techsewa.log")

    # Default settings
    MAX_LISTEN_SECONDS = 10
    MIN_CONFIDENCE = 75
    ENABLE_VOICE = True
    ENABLE_DIAGNOSTICS = True
    ENABLE_INTERNET_LOOKUP = True
    ENABLE_LEARNING = True
    LANGUAGE = "en"  # Default language

    @classmethod
    def load(cls):
        """Load settings with validation."""
        if not os.path.exists(cls.SETTINGS_FILE):
            cls._create_default_config()
            return
            
        try:
            with open(cls.SETTINGS_FILE, "r", encoding="utf-8") as fp:
                cfg = json.load(fp)
                
            cls.MAX_LISTEN_SECONDS = max(1, min(cfg.get("max_listen_seconds", cls.MAX_LISTEN_SECONDS), 30))
            cls.MIN_CONFIDENCE = max(10, min(cfg.get("min_confidence", cls.MIN_CONFIDENCE), 100))
            cls.ENABLE_VOICE = bool(cfg.get("enable_voice", cls.ENABLE_VOICE))
            cls.ENABLE_DIAGNOSTICS = bool(cfg.get("enable_diagnostics", cls.ENABLE_DIAGNOSTICS)) 
            cls.ENABLE_INTERNET_LOOKUP = bool(cfg.get("enable_internet_lookup", cls.ENABLE_INTERNET_LOOKUP))
            cls.ENABLE_LEARNING = bool(cfg.get("enable_learning", cls.ENABLE_LEARNING))
            cls.LANGUAGE = cfg.get("language", cls.LANGUAGE)
            
        except Exception as e:
            cls._log_error(f"Config load error: {str(e)}")
            cls._create_default_config()

    @classmethod
    def _create_default_config(cls):
        """Generate default config file."""
        default_config = {
            "max_listen_seconds": cls.MAX_LISTEN_SECONDS,
            "min_confidence": cls.MIN_CONFIDENCE,
            "enable_voice": cls.ENABLE_VOICE,
            "enable_diagnostics": cls.ENABLE_DIAGNOSTICS,
            "enable_internet_lookup": cls.ENABLE_INTERNET_LOOKUP,
            "enable_learning": cls.ENABLE_LEARNING,
            "language": cls.LANGUAGE
        }
        
        try:
            with open(cls.SETTINGS_FILE, "w", encoding="utf-8") as f:
                json.dump(default_config, f, indent=2)
        except Exception as e:
            cls._log_error(f"Failed to create config: {str(e)}")

    @classmethod
    def _log_error(cls, message: str):
        """Log errors to file."""
        with open(cls.LOG_FILE, "a", encoding="utf-8") as f:
            f.write(f"[{datetime.now().isoformat()}] {message}\n")

Config.load()

# ====================== LOCALIZATION =========================
class Localization:
    """Multilingual support with dynamic loading."""
    
    _strings = {
        "en": {
            "welcome": "Welcome to Techsewa Assistant",
            "listening": "Listening...",
            "not_heard": "Didn't hear anything",
            "no_input": "No input detected",
            "fix_prompt": "Run auto-fix? (y/n) ",
            "diagnostics": "System Diagnostics",
            "goodbye": "Thank you for using Techsewa"
        },
        "np": {
            "welcome": "टेकसेवा सहयोगीमा स्वागत छ",
            "listening": "सुन्दै...", 
            "not_heard": "केही सुनिएन",
            "no_input": "कुनै इनपुट भेटिएन",
            "fix_prompt": "स्वत: मर्मत गर्ने? (हो/छैन) ",
            "diagnostics": "प्रणाली निदान",
            "goodbye": "टेकसेवा प्रयोग गर्नुभएकोमा धन्यवाद"
        }
    }

    @classmethod
    def get(cls, key: str, lang: str = None) -> str:
        """Get localized string."""
        lang = lang or Config.LANGUAGE
        return cls._strings.get(lang, {}).get(key, cls._strings["en"].get(key, key))

# ============================ TTS ================================
class TTS:
    """Enhanced Text-to-Speech with voice selection."""
    
    _engine = None

    @classmethod
    def initialize(cls):
        """Initialize TTS engine with voice selection."""
        if cls._engine is None:
            try:
                cls._engine = pyttsx3.init()
                cls._engine.setProperty("rate", 150)
                
                # Try to set Nepali voice if available
                voices = cls._engine.getProperty('voices')
                nepali_voices = [v for v in voices if 'hindi' in v.id.lower() or 'nepali' in v.id.lower()]
                if nepali_voices and Config.LANGUAGE == "np":
                    cls._engine.setProperty('voice', nepali_voices[0].id)
                    
            except Exception as e:
                Config._log_error(f"TTS init failed: {str(e)}")
                cls._engine = None

    @classmethod
    def speak(cls, text: str, lang: str = None):
        """Speak text with language awareness."""
        if not Config.ENABLE_VOICE or not text.strip():
            return
            
        if cls._engine is None:
            cls.initialize()
            if cls._engine is None:
                return
                
        try:
            # Simple language filtering
            clean_text = re.sub(r'[^\w\s\u0900-\u097F]', '', text) if lang == "np" else text
            cls._engine.say(clean_text)
            cls._engine.runAndWait()
        except Exception as e:
            Config._log_error(f"TTS error: {str(e)}")

# ========================= MICROPHONE ============================
class MicStream:
    """Non-blocking audio recorder with improved error handling."""
    
    def __init__(self):
        self.q = queue.Queue()
        self._stream = None
        self._initialize_stream()

    def _initialize_stream(self):
        """Initialize audio stream with retry logic."""
        max_attempts = 3
        for attempt in range(max_attempts):
            try:
                self._stream = sd.RawInputStream(
                    samplerate=16000,
                    blocksize=8000,
                    dtype='int16',
                    channels=1,
                    callback=self._audio_callback
                )
                self._stream.start()
                return
            except Exception as e:
                if attempt == max_attempts - 1:
                    Config._log_error(f"Mic init failed after {max_attempts} attempts: {str(e)}")
                    raise RuntimeError("Could not initialize microphone")
                time.sleep(1)

    def _audio_callback(self, indata, frames, time, status):
        """Callback for audio data."""
        if status:
            Config._log_error(f"Audio stream status: {status}")
        self.q.put(bytes(indata))

    def record(self, seconds: float) -> bytes:
        """Record audio with timeout handling."""
        data, start = b"", time.time()
        while time.time() - start < seconds:
            try:
                data += self.q.get_nowait()
            except queue.Empty:
                time.sleep(0.05)
            except KeyboardInterrupt:
                break
        return data

    def close(self):
        """Graceful shutdown."""
        if self._stream is not None:
            try:
                self._stream.stop()
                self._stream.close()
            except Exception as e:
                Config._log_error(f"Mic close error: {str(e)}")

# ========================= AUTO FIXER ============================
class AutoFixer:
    """Enhanced auto-repair with logging and safety checks."""
    
    _FIX_MAP = {
        "slow_performance": "_fix_slow_performance",
        "wifi_not_connecting": "_fix_wifi",
        "audio_problem": "_fix_audio"
    }

    @classmethod
    def try_fix(cls, problem_id: str) -> bool:
        """Execute fix with proper error handling."""
        if not problem_id or problem_id not in cls._FIX_MAP:
            return False
            
        fix_method = getattr(cls, cls._FIX_MAP[problem_id], None)
        if not fix_method:
            return False
            
        try:
            fix_method()
            Config._log_error(f"Successfully executed fix for {problem_id}")
            return True
        except Exception as e:
            Config._log_error(f"Fix failed for {problem_id}: {str(e)}")
            return False

    @staticmethod
    def _fix_slow_performance():
        """Clean system temp files."""
        print("🛠 Clearing temp files...")
        temp_dirs = [
            os.getenv("TEMP"),
            os.getenv("TMP"),
            "/tmp"
        ]
        
        for temp_dir in filter(None, temp_dirs):
            if not os.path.exists(temp_dir):
                continue
                
            for fname in os.listdir(temp_dir):
                fpath = os.path.join(temp_dir, fname)
                try:
                    if os.path.isfile(fpath):
                        os.remove(fpath)
                except Exception:
                    continue
        print("✅ Temp files cleaned")

    @staticmethod
    def _fix_wifi():
        """Reset WiFi adapter."""
        if platform.system() != "Windows":
            print("⚠️ WiFi fix only works on Windows")
            return
            
        print("🛠 Restarting WiFi adapter...")
        commands = [
            "netsh interface set interface \"Wi-Fi\" disable",
            "netsh interface set interface \"Wi-Fi\" enable",
            "ipconfig /renew"
        ]
        
        for cmd in commands:
            try:
                subprocess.run(cmd, shell=True, check=True, timeout=10)
            except subprocess.SubprocessError as e:
                print(f"⚠️ Command failed: {cmd} - {str(e)}")
                continue
                
        print("✅ WiFi adapter reset")

    @staticmethod
    def _fix_audio():
        """Restart audio services."""
        print("🛠 Restarting audio services...")
        if platform.system() == "Windows":
            os.system("net stop Audiosrv")
            os.system("net start Audiosrv")
        print("✅ Audio services restarted")

# ======================= DIAGNOSTICS ============================
class Diagnostics:
    """Comprehensive system diagnostics with caching."""
    
    _last_diag_time = 0
    _last_diag_results = None
    _CACHE_TIME = 60  # Cache results for 60 seconds

    @classmethod
    def quick(cls) -> Dict[str, float]:
        """Quick system check with caching."""
        now = time.time()
        if now - cls._last_diag_time < cls._CACHE_TIME and cls._last_diag_results:
            return cls._last_diag_results
            
        try:
            results = {
                "cpu": psutil.cpu_percent(interval=1),
                "ram": psutil.virtual_memory().percent,
                "disk": psutil.disk_usage("/").percent,
                "timestamp": now
            }
            
            # Try to get temperature if available
            if hasattr(psutil, "sensors_temperatures"):
                temps = psutil.sensors_temperatures()
                if temps:
                    for name, entries in temps.items():
                        if entries:
                            results["temp"] = entries[0].current
                            break
                            
            cls._last_diag_time = now
            cls._last_diag_results = results
            return results
            
        except Exception as e:
            Config._log_error(f"Diagnostics failed: {str(e)}")
            return {}

    @classmethod
    def full_report(cls) -> str:
        """Generate complete diagnostic report."""
        diag = cls.quick()
        if not diag:
            return "⚠️ Diagnostics unavailable"
            
        report = [
            f"🩺 System Diagnostics [{datetime.fromtimestamp(diag['timestamp'])}]",
            f"🧠 CPU: {diag['cpu']}%",
            f"💾 RAM: {diag['ram']}%",
            f"💽 Disk: {diag['disk']}%"
        ]
        
        if "temp" in diag:
            report.append(f"🌡 Temp: {diag['temp']}°C")
            
        return "\n".join(report)

# ==================== TECHSEWA ASSISTANT ========================
class Techsewa:
    """Main assistant class with enhanced capabilities."""
    
    def __init__(self):
        self.mic = MicStream()
        self.brain = SmartBrain(
            Config.PROBLEM_DB,
            Config.ENABLE_INTERNET_LOOKUP,
            min_confidence=Config.MIN_CONFIDENCE
        )
        self.recognizer = self._init_recognizer()
        self.conversation_history = []
        self._init_resources()

    def _init_resources(self):
        """Initialize required resources."""
        if not os.path.exists(Config.MODEL_DIR):
            raise FileNotFoundError(f"Model directory not found: {Config.MODEL_DIR}")
            
        if not os.path.exists(Config.PROBLEM_DB):
            raise FileNotFoundError(f"Problem database not found: {Config.PROBLEM_DB}")

    def _init_recognizer(self) -> KaldiRecognizer:
        """Initialize speech recognizer based on language."""
        model_path = os.path.join(
            Config.MODEL_DIR,
            "vosk-model-small-hi-0.22" if Config.LANGUAGE == "np" 
            else "vosk-model-small-en-us-0.15"
        )
        
        if not os.path.exists(model_path):
            raise FileNotFoundError(f"Language model not found: {model_path}")
            
        return KaldiRecognizer(Model(model_path), 16000)

    def run(self):
        """Main interaction loop."""
        self._welcome()
        
        while True:
            try:
                user_input = self._get_user_input()
                if user_input is None:
                    continue
                    
                self._process_input(user_input)
                
            except KeyboardInterrupt:
                print("\n🛑 Shutdown requested...")
                break
            except Exception as e:
                Config._log_error(f"Runtime error: {str(e)}\n{traceback.format_exc()}")
                print(f"⚠️ An error occurred: {str(e)}")
                time.sleep(1)  # Prevent tight error loop

        self._goodbye()

    def _welcome(self):
        """Show welcome message."""
        welcome_msg = Localization.get("welcome", Config.LANGUAGE)
        print(f"\n🙏 {welcome_msg}")
        TTS.speak(welcome_msg, Config.LANGUAGE)

    def _goodbye(self):
        """Show goodbye message."""
        goodbye_msg = Localization.get("goodbye", Config.LANGUAGE)
        print(f"\n🌟 {goodbye_msg}")
        TTS.speak(goodbye_msg, Config.LANGUAGE)

    def _get_user_input(self) -> Optional[str]:
        """Get input from user via voice or text."""
        cmd = input("\n🎤 [Enter=speak | k=keyboard | d=diag | q=quit]> ").lower()
        
        if cmd == 'q':
            raise KeyboardInterrupt()
        if cmd == 'd' and Config.ENABLE_DIAGNOSTICS:
            self._run_diagnostics()
            return None
        if cmd == 'k':
            return input("⌨️ ").strip()
            
        return self._get_voice_input()

    def _get_voice_input(self) -> Optional[str]:
        """Get voice input from microphone."""
        print(Localization.get("listening", Config.LANGUAGE))
        
        # Warm-up and noise flush
        self.mic.record(0.5)
        
        # Main recording
        audio_data = self.mic.record(Config.MAX_LISTEN_SECONDS)
        if not audio_data:
            print(Localization.get("not_heard", Config.LANGUAGE))
            return None
            
        if self.recognizer.AcceptWaveform(audio_data):
            result = json.loads(self.recognizer.Result()).get("text", "")
        else:
            result = json.loads(self.recognizer.PartialResult()).get("partial", "")
            
        if not result.strip():
            print(Localization.get("no_input", Config.LANGUAGE))
            return None
            
        print(f"👤 You: {result}")
        return result

    def _process_input(self, user_input: str):
        """Process and respond to user input."""
        # Detect language if not set in config
        lang = self._detect_language(user_input) if Config.LANGUAGE == "auto" else Config.LANGUAGE
        
        # Get solution from brain
        result = self.brain.solve(user_input, lang)
        response = f"{result['answer']}\n{CONTACT_INFO}"
        
        # Log conversation
        self._log_conversation(user_input, response, result['source'], lang)
        
        # Present results
        print(f"\n🤖 [{result['source'].upper()}]\n{response}\n")
        TTS.speak(response, lang)
        
        # Handle auto-fix if applicable
        if result['source'] == 'local':
            self._handle_auto_fix(user_input)

    def _detect_language(self, text: str) -> str:
        """Simple language detection."""
        nepali_chars = sum(1 for c in text if '\u0900' <= c <= '\u097F')
        return "np" if nepali_chars / max(len(text), 1) > 0.3 else "en"

    def _log_conversation(self, query: str, response: str, source: str, lang: str):
        """Log conversation to history."""
        self.conversation_history.append({
            "timestamp": datetime.now().isoformat(),
            "query": query,
            "response": response,
            "source": source,
            "language": lang
        })

    def _handle_auto_fix(self, query: str):
        """Handle auto-fix workflow."""
        problem_id = self._infer_problem_id(query)
        if not problem_id or not self._auto_fix_enabled(problem_id):
            return
            
        prompt = Localization.get("fix_prompt", Config.LANGUAGE)
        if input(prompt).lower() in ('y', 'हो'):
            AutoFixer.try_fix(problem_id)

    def _infer_problem_id(self, query: str) -> Optional[str]:
        """Find problem ID from query."""
        query = query.lower()
        for prob in self.brain.local.problems:
            if any(query == alias.lower() for alias in prob.get("aliases", [])):
                return prob.get("id")
        return None

    def _auto_fix_enabled(self, problem_id: str) -> bool:
        """Check if auto-fix is enabled for problem."""
        for prob in self.brain.local.problems:
            if prob.get("id") == problem_id:
                return prob.get("auto_fix", False)
        return False

    def _run_diagnostics(self):
        """Run and display diagnostics."""
        diag_report = Diagnostics.full_report()
        print(f"\n{diag_report}")
        TTS.speak(diag_report.replace("🩺", "").replace("🧠", "CPU").replace("💾", "RAM"), Config.LANGUAGE)

    def close(self):
        """Cleanup resources."""
        self.mic.close()
        # Save conversation history
        with open("conversation_history.json", "w", encoding="utf-8") as f:
            json.dump(self.conversation_history, f, indent=2)

# ============================ MAIN ==============================
if __name__ == "__main__":
    assistant = None
    try:
        print("\n" + "="*50)
        print("🚀 Techsewa Assistant - Professional Edition")
        print("="*50)
        
        assistant = Techsewa()
        assistant.run()
        
    except Exception as e:
        error_msg = f"⛔ Critical error: {str(e)}"
        print(error_msg)
        Config._log_error(error_msg + "\n" + traceback.format_exc())
        
    finally:
        if assistant:
            assistant.close()
        print("\n" + "="*50)
        print("Session ended")