import os
import json
import queue
import re
import time
import threading
import subprocess
from functools import lru_cache
from typing import Optional, Dict

import sounddevice as sd
import pyttsx3
from vosk import Model, KaldiRecognizer
import psutil

# Local imports
from Brain import SmartBrain

# ====================== CONFIGURATION ========================
class Config:
    """Centralized configuration with validation"""
    
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    MODEL_DIR = os.path.join(BASE_DIR, "Model")
    PROBLEM_DB = os.path.join(BASE_DIR, "problems.json")
    CONFIG_FILE = os.path.join(BASE_DIR, "config.json")
    
    # Default settings
    MAX_LISTEN_SECONDS = 10
    MIN_CONFIDENCE = 75
    ENABLE_VOICE = True
    ENABLE_DIAGNOSTICS = True
    ENABLE_INTERNET = True
    LANGUAGE = "en"  # 'en' or 'np'

    @classmethod
    def load(cls):
        """Load settings from config file"""
        if not os.path.exists(cls.CONFIG_FILE):
            cls._create_default_config()
        try:
            with open(cls.CONFIG_FILE, "r", encoding="utf-8") as f:
                settings = json.load(f)
                cls.MAX_LISTEN_SECONDS = settings.get("max_listen_seconds", cls.MAX_LISTEN_SECONDS)
                cls.MIN_CONFIDENCE = settings.get("min_confidence", cls.MIN_CONFIDENCE)
                cls.ENABLE_VOICE = settings.get("enable_voice", cls.ENABLE_VOICE)
                cls.ENABLE_DIAGNOSTICS = settings.get("enable_diagnostics", cls.ENABLE_DIAGNOSTICS)
                cls.ENABLE_INTERNET = settings.get("enable_internet", cls.ENABLE_INTERNET)
                cls.LANGUAGE = settings.get("language", cls.LANGUAGE)
        except Exception as e:
            print(f"⚠️ Config error: {e}")
            cls._create_default_config()

    @classmethod
    def _create_default_config(cls):
        """Create default config file"""
        default = {
            "max_listen_seconds": cls.MAX_LISTEN_SECONDS,
            "min_confidence": cls.MIN_CONFIDENCE,
            "enable_voice": cls.ENABLE_VOICE,
            "enable_diagnostics": cls.ENABLE_DIAGNOSTICS,
            "enable_internet": cls.ENABLE_INTERNET,
            "language": cls.LANGUAGE
        }
        with open(cls.CONFIG_FILE, "w", encoding="utf-8") as f:
            json.dump(default, f, indent=2)

Config.load()

# ====================== CONTACT INFORMATION ==================
CONTACT_INFO = {
    "en": (
        "\n📍 Visit: Learning Mission & Training Center, Thuphandanda, Dadeldhura\n"
        "📞 Phone: 9867315931\n"
        "📧 Email: learnermission@gmail.com"
    ),
    "np": (
        "\n📍 कृपया सम्पर्क गर्नुहोस्: Learning Mission, थुपनडाँडा, डडेलधुरा\n"
        "📞 फोन: ९८६७३१५९३१\n"
        "📧 इमेल: learnermission@gmail.com"
    )
}

# ====================== AUDIO HANDLING =======================
class Microphone:
    """Non-blocking microphone input"""
    
    def __init__(self):
        self.queue = queue.Queue()
        self.stream = sd.RawInputStream(
            samplerate=16000,
            blocksize=8000,
            dtype='int16',
            channels=1,
            callback=self._callback
        )
        self.stream.start()

    def _callback(self, indata, frames, time, status):
        """Audio callback function"""
        self.queue.put(bytes(indata))

    def listen(self, seconds: float) -> bytes:
        """Record audio for specified duration"""
        audio = b""
        start = time.time()
        while time.time() - start < seconds:
            try:
                audio += self.queue.get_nowait()
            except queue.Empty:
                time.sleep(0.05)
        return audio

    def close(self):
        """Release audio resources"""
        self.stream.close()

# ====================== SPEECH SYNTHESIS =====================
class Speaker:
    """Text-to-speech with language support"""
    
    def __init__(self):
        self.engine = pyttsx3.init()
        self.engine.setProperty('rate', 150)
        
    def speak(self, text: str, lang: str = "en"):
        """Speak text with language filtering"""
        if not Config.ENABLE_VOICE:
            return
            
        # Basic language filtering
        if lang == "np":
            text = re.sub(r'[^\w\s\u0900-\u097F]', '', text)
        self.engine.say(text)
        self.engine.runAndWait()

# ====================== CORE ASSISTANT =======================
class TechsewaAssistant:
    """Main assistant class"""
    
    def __init__(self):
        self.mic = Microphone()
        self.speaker = Speaker()
        self.brain = SmartBrain(
            Config.PROBLEM_DB,
            Config.ENABLE_INTERNET,
            min_confidence=Config.MIN_CONFIDENCE
        )
        self.recognizer = self._init_recognizer()

    def _init_recognizer(self):
        """Initialize speech recognizer based on language"""
        model_path = os.path.join(
            Config.MODEL_DIR,
            "vosk-model-small-hi-0.22" if Config.LANGUAGE == "np" 
            else "vosk-model-small-en-us-0.15"
        )
        return KaldiRecognizer(Model(model_path), 16000)

    def run(self):
        """Main interaction loop"""
        print("\n" + "="*50)
        print("🚀 Techsewa Assistant - Professional Edition")
        print("="*50)
        
        welcome_msg = {
            "en": "Welcome to Techsewa Assistant",
            "np": "टेकसेवा सहयोगीमा स्वागत छ"
        }
        self.speaker.speak(welcome_msg[Config.LANGUAGE], Config.LANGUAGE)
        
        try:
            while True:
                user_input = self._get_input()
                if not user_input:
                    continue
                    
                self._process_query(user_input)
                
        except KeyboardInterrupt:
            print("\nShutting down...")
        finally:
            self.mic.close()

    def _get_input(self) -> Optional[str]:
        """Get user input via voice or text"""
        cmd = input("\n🎤 [Enter=speak | k=keyboard | d=diag | q=quit]> ").lower()
        
        if cmd == 'q':
            raise KeyboardInterrupt()
        if cmd == 'd' and Config.ENABLE_DIAGNOSTICS:
            self._run_diagnostics()
            return None
        if cmd == 'k':
            return input("⌨️ Describe your problem: ").strip()
            
        print("🔊 Listening..." if Config.LANGUAGE == "en" else "🔊 सुन्दै...")
        audio = self.mic.listen(Config.MAX_LISTEN_SECONDS)
        if not audio:
            print("No audio detected" if Config.LANGUAGE == "en" else "ध्वनि पत्ता लागेन")
            return None
            
        if self.recognizer.AcceptWaveform(audio):
            result = json.loads(self.recognizer.Result()).get("text", "")
        else:
            result = json.loads(self.recognizer.PartialResult()).get("partial", "")
            
        return result if result.strip() else None

    def _process_query(self, query: str):
        """Process and respond to user query"""
        print(f"👤 You: {query}")
        
        # Get solution from brain
        result = self.brain.solve(query, Config.LANGUAGE)
        response = f"{result['answer']}{CONTACT_INFO[Config.LANGUAGE]}"
        
        # Present results
        print(f"\n🤖 Techsewa:\n{response}\n")
        self.speaker.speak(response, Config.LANGUAGE)

    def _run_diagnostics(self):
        """Run system diagnostics"""
        diag = {
            "cpu": psutil.cpu_percent(interval=1),
            "ram": psutil.virtual_memory().percent,
            "disk": psutil.disk_usage('/').percent
        }
        
        report = (
            f"🖥️ CPU: {diag['cpu']}%\n"
            f"🧠 RAM: {diag['ram']}%\n"
            f"💾 Disk: {diag['disk']}%"
        )
        
        print("\nSystem Diagnostics:")
        print(report)
        self.speaker.speak(report.replace("🖥️", "CPU").replace("🧠", "RAM").replace("💾", "Disk"))

# ====================== MAIN ENTRY ============================
if __name__ == "__main__":
    assistant = TechsewaAssistant()
    assistant.run()