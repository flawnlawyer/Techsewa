# nepali_tts.py - Enhanced Nepali Text-to-Speech Module
import asyncio
import hashlib
import os
import threading
import time
import logging
from pathlib import Path
from typing import Optional, Union, Callable, Dict, Any
from dataclasses import dataclass, field
from enum import Enum
import json

try:
    from gtts import gTTS
    from playsound import playsound
    import pygame
    HAS_PYGAME = True
except ImportError as e:
    HAS_PYGAME = False
    logging.warning(f"Optional dependency missing: {e}")

class PlaybackEngine(Enum):
    """Available audio playback engines."""
    PLAYSOUND = "playsound"
    PYGAME = "pygame"
    SYSTEM = "system"

class TTSLanguage(Enum):
    """Supported TTS languages."""
    NEPALI = "ne"
    ENGLISH = "en"
    HINDI = "hi"

@dataclass
class TTSConfig:
    """Configuration for TTS operations."""
    cache_dir: str = "tts_cache"
    playback_engine: PlaybackEngine = PlaybackEngine.PLAYSOUND
    default_language: TTSLanguage = TTSLanguage.NEPALI
    cache_size_limit_mb: int = 100
    max_text_length: int = 1000
    timeout_seconds: int = 10
    volume: float = 0.8
    speed_multiplier: float = 1.0
    auto_cleanup: bool = True
    log_level: str = "INFO"

@dataclass
class TTSResult:
    """Result of TTS operation."""
    success: bool
    message: str
    file_path: Optional[str] = None
    thread: Optional[threading.Thread] = None
    duration: float = 0.0

class NepaliTTS:
    """Enhanced Nepali Text-to-Speech class with caching and multiple playback options."""
    
    def __init__(self, config: Optional[TTSConfig] = None):
        self.config = config or TTSConfig()
        self.cache_dir = Path(self.config.cache_dir)
        self.cache_dir.mkdir(exist_ok=True)
        
        # Setup logging
        logging.basicConfig(
            level=getattr(logging, self.config.log_level),
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        self.logger = logging.getLogger('NepaliTTS')
        
        # Initialize pygame if available and selected
        if self.config.playback_engine == PlaybackEngine.PYGAME and HAS_PYGAME:
            try:
                pygame.mixer.init()
                self.logger.info("Pygame mixer initialized")
            except Exception as e:
                self.logger.warning(f"Pygame init failed: {e}, falling back to playsound")
                self.config.playback_engine = PlaybackEngine.PLAYSOUND
        
        # Cache management
        self._cache_info = self._load_cache_info()
        self._active_threads: Dict[str, threading.Thread] = {}
        
        # Cleanup old cache if enabled
        if self.config.auto_cleanup:
            self._cleanup_cache()
    
    def _load_cache_info(self) -> Dict[str, Any]:
        """Load cache information from disk."""
        cache_info_file = self.cache_dir / "cache_info.json"
        if cache_info_file.exists():
            try:
                with open(cache_info_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception as e:
                self.logger.warning(f"Failed to load cache info: {e}")
        return {"files": {}, "total_size": 0}
    
    def _save_cache_info(self):
        """Save cache information to disk."""
        cache_info_file = self.cache_dir / "cache_info.json"
        try:
            with open(cache_info_file, 'w', encoding='utf-8') as f:
                json.dump(self._cache_info, f, ensure_ascii=False, indent=2)
        except Exception as e:
            self.logger.warning(f"Failed to save cache info: {e}")
    
    def _cleanup_cache(self):
        """Clean up old cache files if size limit exceeded."""
        current_size = sum(
            os.path.getsize(self.cache_dir / f) 
            for f in os.listdir(self.cache_dir) 
            if f.endswith('.mp3')
        ) / (1024 * 1024)  # Convert to MB
        
        if current_size > self.config.cache_size_limit_mb:
            self.logger.info(f"Cache size ({current_size:.1f}MB) exceeds limit, cleaning up...")
            
            # Sort files by last access time
            files_with_time = []
            for filename in os.listdir(self.cache_dir):
                if filename.endswith('.mp3'):
                    file_path = self.cache_dir / filename
                    files_with_time.append((file_path, os.path.getmtime(file_path)))
            
            files_with_time.sort(key=lambda x: x[1])  # Sort by modification time
            
            # Remove oldest files until under limit
            for file_path, _ in files_with_time:
                if current_size <= self.config.cache_size_limit_mb * 0.8:  # 80% of limit
                    break
                try:
                    file_size = os.path.getsize(file_path) / (1024 * 1024)
                    os.remove(file_path)
                    current_size -= file_size
                    self.logger.debug(f"Removed cached file: {file_path.name}")
                except Exception as e:
                    self.logger.warning(f"Failed to remove {file_path}: {e}")
    
    def _get_cache_filename(self, text: str, language: TTSLanguage, slow: bool) -> str:
        """Generate consistent cache filename."""
        cache_key = f"{text}_{language.value}_{slow}_{self.config.speed_multiplier}"
        return hashlib.md5(cache_key.encode('utf-8')).hexdigest() + ".mp3"
    
    def _validate_text(self, text: str) -> bool:
        """Validate input text."""
        if not text or not text.strip():
            return False
        if len(text) > self.config.max_text_length:
            self.logger.warning(f"Text too long ({len(text)} chars), truncating")
            return False
        return True
    
    def _generate_audio(self, text: str, language: TTSLanguage, slow: bool, filename: Path) -> bool:
        """Generate audio file using gTTS."""
        try:
            tts = gTTS(
                text=text.strip(),
                lang=language.value,
                slow=slow
            )
            tts.save(str(filename))
            
            # Update cache info
            file_size = os.path.getsize(filename)
            self._cache_info["files"][filename.name] = {
                "size": file_size,
                "created": time.time(),
                "text_preview": text[:50] + "..." if len(text) > 50 else text
            }
            self._cache_info["total_size"] += file_size
            self._save_cache_info()
            
            self.logger.debug(f"Generated TTS audio: {filename.name}")
            return True
            
        except Exception as e:
            self.logger.error(f"TTS generation failed: {e}")
            return False
    
    def _play_with_playsound(self, filename: Path) -> bool:
        """Play audio using playsound."""
        try:
            playsound(str(filename))
            return True
        except Exception as e:
            self.logger.error(f"Playsound playback failed: {e}")
            return False
    
    def _play_with_pygame(self, filename: Path) -> bool:
        """Play audio using pygame."""
        if not HAS_PYGAME:
            return False
        
        try:
            pygame.mixer.music.load(str(filename))
            pygame.mixer.music.set_volume(self.config.volume)
            pygame.mixer.music.play()
            
            # Wait for playback to finish
            while pygame.mixer.music.get_busy():
                time.sleep(0.1)
            
            return True
        except Exception as e:
            self.logger.error(f"Pygame playback failed: {e}")
            return False
    
    def _play_with_system(self, filename: Path) -> bool:
        """Play audio using system command."""
        try:
            import subprocess
            if os.name == 'nt':  # Windows
                os.system(f'start "" "{filename}"')
            elif os.name == 'posix':  # macOS and Linux
                subprocess.run(['afplay' if os.uname().sysname == 'Darwin' else 'mpg123', str(filename)], 
                             check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            return True
        except Exception as e:
            self.logger.error(f"System playback failed: {e}")
            return False
    
    def speak(self, 
              text: str, 
              slow: bool = False,
              language: Optional[TTSLanguage] = None,
              blocking: bool = False,
              callback: Optional[Callable] = None) -> TTSResult:
        """
        Speak text with enhanced options.
        
        Args:
            text: Text to speak
            slow: Whether to speak slowly
            language: Language to use (defaults to config default)
            blocking: Whether to wait for playback to finish
            callback: Function to call when playback completes
            
        Returns:
            TTSResult object with operation details
        """
        start_time = time.time()
        
        if not self._validate_text(text):
            return TTSResult(False, "Invalid text input")
        
        language = language or self.config.default_language
        text = text.strip()
        
        # Generate cache filename
        cache_filename = self._get_cache_filename(text, language, slow)
        file_path = self.cache_dir / cache_filename
        
        # Generate audio if not cached
        if not file_path.exists():
            if not self._generate_audio(text, language, slow, file_path):
                return TTSResult(False, "Audio generation failed")
        
        # Select playback method
        playback_methods = {
            PlaybackEngine.PLAYSOUND: self._play_with_playsound,
            PlaybackEngine.PYGAME: self._play_with_pygame,
            PlaybackEngine.SYSTEM: self._play_with_system
        }
        
        play_method = playback_methods.get(self.config.playback_engine, self._play_with_playsound)
        
        # Play audio
        def _play_audio():
            try:
                success = play_method(file_path)
                if callback:
                    callback(success)
                return success
            except Exception as e:
                self.logger.error(f"Playback failed: {e}")
                if callback:
                    callback(False)
                return False
        
        if blocking:
            success = _play_audio()
            duration = time.time() - start_time
            return TTSResult(success, "Playback completed" if success else "Playback failed", 
                           str(file_path), None, duration)
        else:
            thread = threading.Thread(target=_play_audio, daemon=True)
            thread.start()
            
            # Store thread reference
            thread_id = hashlib.md5(text.encode()).hexdigest()[:8]
            self._active_threads[thread_id] = thread
            
            return TTSResult(True, "Playback started", str(file_path), thread, 0.0)
    
    def speak_async(self, text: str, **kwargs) -> TTSResult:
        """Async version of speak method."""
        return self.speak(text, blocking=False, **kwargs)
    
    def speak_sync(self, text: str, **kwargs) -> TTSResult:
        """Synchronous version of speak method."""
        return self.speak(text, blocking=True, **kwargs)
    
    def stop_all(self):
        """Stop all active playback threads."""
        if self.config.playback_engine == PlaybackEngine.PYGAME and HAS_PYGAME:
            pygame.mixer.music.stop()
        
        for thread in self._active_threads.values():
            if thread.is_alive():
                # Note: Can't forcefully stop threads, they need to finish naturally
                pass
        
        self._active_threads.clear()
        self.logger.info("Stopped all playback")
    
    def clear_cache(self):
        """Clear all cached audio files."""
        try:
            for file in self.cache_dir.glob("*.mp3"):
                file.unlink()
            self._cache_info = {"files": {}, "total_size": 0}
            self._save_cache_info()
            self.logger.info("Cache cleared")
        except Exception as e:
            self.logger.error(f"Failed to clear cache: {e}")
    
    def get_cache_info(self) -> Dict[str, Any]:
        """Get information about cached files."""
        return {
            "total_files": len(self._cache_info["files"]),
            "total_size_mb": self._cache_info["total_size"] / (1024 * 1024),
            "cache_dir": str(self.cache_dir),
            "files": self._cache_info["files"]
        }

# Convenience functions for backward compatibility
def speak(text: str, slow: bool = False, **kwargs) -> Optional[threading.Thread]:
    """Simple speak function for backward compatibility."""
    tts = NepaliTTS()
    result = tts.speak(text, slow=slow, **kwargs)
    return result.thread if result.success else None

# Example usage and testing
if __name__ == "__main__":
    # Example usage
    config = TTSConfig(
        playback_engine=PlaybackEngine.PLAYSOUND,
        cache_size_limit_mb=50,
        volume=0.8
    )
    
    tts = NepaliTTS(config)
    
    # Test basic functionality
    print("Testing Nepali TTS...")
    
    # Synchronous speech
    result = tts.speak_sync("नमस्ते, म एक नेपाली TTS प्रणाली हुँ।")
    print(f"Sync result: {result.success}, {result.message}")
    
    # Asynchronous speech
    result = tts.speak_async("यो असिंक्रोनस परीक्षण हो।")
    print(f"Async result: {result.success}, {result.message}")
    
    # Wait a bit for async to complete
    time.sleep(3)
    
    # Show cache info
    cache_info = tts.get_cache_info()
    print(f"Cache info: {cache_info['total_files']} files, {cache_info['total_size_mb']:.2f} MB")
    
    print("Testing complete!")