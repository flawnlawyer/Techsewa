"""
cli.py  –  Techsewa Assistant (Console / Microphone Edition)
============================================================
Run with:  python cli.py
"""

import os, json, queue, re, time, threading, subprocess, sys
from functools import lru_cache
from typing import Optional

import sounddevice as sd
import psutil
from vosk import Model, KaldiRecognizer

# ─── Local imports ─────────────────────────────────────────────────────────────
from Brain import SmartBrain
from problem_detector import ProblemDetector, ProblemType
from auto_healer import AutoHealer
from nepali_tts import speak as nepali_speak
import pyttsx3
# ───────────────────────────────────────────────────────────────────────────────

# ══════════════════ CONFIG ════════════════════════════════════════════════════
BASE_DIR   = os.path.dirname(os.path.abspath(__file__))
MODEL_DIR  = os.path.join(BASE_DIR, "Model")
PROBLEM_DB = os.path.join(BASE_DIR, "problems.json")
CONFIG     = os.path.join(BASE_DIR, "config.json")

DEFAULTS = {
    "max_listen_seconds": 8,
    "min_confidence": 75,
    "enable_voice": True,
    "enable_internet": True,
    "language": "en"          # "en" or "np"
}

def load_cfg():
    if not os.path.exists(CONFIG):
        with open(CONFIG, "w", encoding="utf-8") as f:
            json.dump(DEFAULTS, f, indent=2)
    try:
        with open(CONFIG, "r", encoding="utf-8") as f:
            cfg = {**DEFAULTS, **json.load(f)}
    except Exception:
        cfg = DEFAULTS
    return cfg

CFG = load_cfg()

CONTACT_INFO = {
    "en": "\n📍 Learning Mission & Training Center, Dadeldhura  |  📞 9867315931",
    "np": "\n📍 Learning Mission, डडेलधुरा  |  📞 ९८६७३१५९३१"
}

# ══════════════════ AUDIO DEVICES ═════════════════════════════════════════════
class Microphone:
    def __init__(self):
        self.q = queue.Queue()
        self.stream = sd.RawInputStream(
            samplerate=16_000, blocksize=8_000, dtype='int16',
            channels=1, callback=lambda d, *_: self.q.put(bytes(d))
        ).start()

    def listen(self, secs=CFG["max_listen_seconds"]) -> bytes:
        audio, t0 = b"", time.time()
        while time.time() - t0 < secs:
            try:  audio += self.q.get_nowait()
            except queue.Empty: time.sleep(0.05)
        return audio

    def close(self): self.stream.close()

class Speaker:
    def __init__(self):
        self.eng = pyttsx3.init()
        self.eng.setProperty('rate', 150)

    def speak(self, txt: str, lang: str):
        if not CFG["enable_voice"]: return
        if lang == "np":
            nepali_speak(txt)
        else:
            self.eng.say(txt); self.eng.runAndWait()

# ══════════════════ CORE ASSISTANT ════════════════════════════════════════════
class TechsewaCLI:
    def __init__(self):
        self.spk  = Speaker()
        self.mic  = Microphone()
        self.brain = SmartBrain(PROBLEM_DB, CFG["enable_internet"],
                                min_confidence=CFG["min_confidence"])
        self.rec  = KaldiRecognizer(
            Model(os.path.join(
                MODEL_DIR,
                "vosk-model-small-hi-0.22" if CFG["language"]=="np"
                else "vosk-model-small-en-us-0.15")),
            16_000)

        # Health monitor
        self.healer   = AutoHealer()
        self.detector = ProblemDetector(self._on_problem, )
        self.detector.start()

    # ── ProblemDetector callback ────────────────────────────────────────────
    def _on_problem(self, msg: str, code: int):
        print(f"\n⚠  System Alert ({code}): {msg}")
        problem_map = {
            201: ProblemType.CPU_HIGH,
            202: ProblemType.RAM_HIGH,
            203: ProblemType.DISK_LOW,
            204: ProblemType.BATTERY_LOW,
            205: ProblemType.TEMP_HIGH,
            206: ProblemType.NET_SPIKE
        }
        healed = self.healer.heal(problem_map.get(code, ProblemType.CPU_HIGH))
        if healed: print("🛠  Auto‑Healer attempted a fix.")
        self.spk.speak(msg, "np")

    # ── Main loop ───────────────────────────────────────────────────────────
    def run(self):
        hello = {"en": "Welcome to Techsewa CLI", "np": "टेकसेवा CLI मा स्वागत छ"}
        self.spk.speak(hello[CFG["language"]], CFG["language"])
        print(hello[CFG["language"]])
        try:
            while True:
                user_text = self._get_input()
                if not user_text: continue
                self._answer(user_text)
        except KeyboardInterrupt:
            print("\nExiting…")
        finally:
            self.detector.stop()
            self.mic.close()

    # ── Helpers ─────────────────────────────────────────────────────────────
    def _get_input(self) -> Optional[str]:
        choice = input("\n[Enter]=Speak | k=keyboard | q=quit > ").lower()
        if choice == 'q': raise KeyboardInterrupt
        if choice == 'k':
            return input("Type your problem: ").strip()

        print("🎙  Listening…")
        audio = self.mic.listen()
        if self.rec.AcceptWaveform(audio):
            txt = json.loads(self.rec.Result())["text"]
        else:
            txt = json.loads(self.rec.PartialResult())["partial"]
        return txt.strip()

    def _answer(self, query: str):
        print(f"\n👤 You: {query}")
        res = self.brain.solve(query, CFG["language"])
        full = f"{res['answer']}{CONTACT_INFO[CFG['language']]}"
        print(f"\n🤖 Techsewa:\n{full}\n")
        self.spk.speak(full, CFG["language"])

# ══════════════════ RUN ══════════════════════════════════════════════════════
if __name__ == "__main__":
    TechsewaCLI().run()
