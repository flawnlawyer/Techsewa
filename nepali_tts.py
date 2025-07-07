# nepali_tts.py - enhanced version with additional features
from gtts import gTTS
from playsound import playsound
import hashlib, os, threading
import logging
from typing import Optional

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger('NepaliTTS')

CACHE_DIR = "tts_cache"
os.makedirs(CACHE_DIR, exist_ok=True)

def speak(text: str, slow: bool = False) -> Optional[threading.Thread]:
    """
    Speak Nepali text asynchronously with cached mp3 files.
    
    Args:
        text: Nepali text to speak
        slow: Whether to speak slowly (for difficult words)
        
    Returns:
        Thread object if playback started, None if failed
    """
    if not text.strip():
        return None

    try:
        # Create consistent filename (handle Unicode properly)
        filename = os.path.join(
            CACHE_DIR, 
            hashlib.md5(text.encode('utf-8')).hexdigest() + ".mp3"
        )
        
        # Generate & cache if not present
        if not os.path.exists(filename):
            gTTS(text=text, lang="ne", slow=slow).save(filename)
            logger.debug(f"Generated TTS for: {text[:50]}...")
        
        # Start playback thread
        def _play():
            try:
                playsound(filename)
            except Exception as e:
                logger.error(f"Playback failed for '{text[:30]}...': {str(e)}")
        
        thread = threading.Thread(target=_play, daemon=True)
        thread.start()
        return thread
        
    except Exception as e:
        logger.error(f"TTS generation failed for '{text[:30]}...': {str(e)}")
        return None