#!/usr/bin/env python3
# mad_antivirus.py – TechSewa’s FREE Offline Guard … now with 200 % more sass
import os, psutil, hashlib, json, time, platform, shutil, random
from datetime import datetime
from pathlib import Path

# -------- SASS ENGINE --------
SASS_LINES = [
    "Your PC is so infected it needs a priest, not an antivirus.",
    "Found more threats than relatives at a Nepali wedding.",
    "This machine has more bugs than a Kathmandu street dog.",
    "If malware had loyalty cards, you’d have platinum status.",
    "Your CPU is working harder than a micro-bus conductor on a festival day.",
    "Congratulations, you’ve collected every virus like Pokémon cards.",
    "I’ve seen cleaner temp folders in cyber-cafés that still run Windows XP.",
    "Your startup list is longer than the queue for momos at Basantapur.",
    "Is this a computer or a malware Airbnb?",
    "Even the viruses are asking for Wi-Fi to call home."
]

# -------- CONSTANTS --------
HOME       = Path.home()
QUAR_DIR   = HOME / ".techsewa" / "quarantine"
CACHE_DIR  = HOME / ".techsewa" / "cache"
LOG_DIR    = HOME / ".techsewa" / "logs"

WHITELIST = {
    "explorer.exe", "svchost.exe", "lsass.exe", "winlogon.exe",
    "hamropatro.exe", "nepali_keyboard.exe", "techsewa_helper.exe"
}

YARA_RULES = [
    ("WannaCry-KillSwitch", b"\x00\x00\x00\x00ifeopen", 95, "Ransomware that asks for momo instead of bitcoin."),
    ("Emotet-2023", b"\x8B\xFF\x55\x8B\xEC\x83\xEC", 90, "Banking trojan – steals more than pickpockets in Ratna Park."),
    ("AutoIt-Backdoor", b"\x41\x55\x74\x6F\x49\x74\x21", 85, "Script kiddie’s favorite, now with extra naan."),
    ("Generic-Downloader", b"\x68\x74\x74\x70\x3A\x2F\x2F", 70, "Downloads payloads faster than your 4G at Tinkune."),
    ("NepaliKeylogger", b"\x6E\x70\x6B\x6C\x67\x5F\x76", 80, "Logs keystrokes – probably trying to steal your Wi-Fi password."),
    ("FakeAV-Scam", b"\x59\x6F\x75\x72\x20\x50\x43\x20\x69\x73\x20\x69\x6E\x66\x65\x63\x74\x65\x64", 60, "Ironically, the fake antivirus is itself malware."),
]

MAX_FILE_SCAN = 50 * 1024 * 1024
INTEGRITY_HASH = "a1b2c3d4e5f6..."   # fill after deployment

# -------- UTILITIES --------
def sha256(path: Path) -> str:
    h = hashlib.sha256()
    try:
        with open(path, "rb") as f:
            for chunk in iter(lambda: f.read(1 << 20), b""):
                h.update(chunk)
        return h.hexdigest()
    except Exception:
        return "ERROR_CANT_READ"

def ensure_dirs():
    for d in (QUAR_DIR, CACHE_DIR, LOG_DIR):
        d.mkdir(parents=True, exist_ok=True)
        d.chmod(0o700)

def log_sass(msg, lvl="ROAST"):
    log_file = LOG_DIR / f"roast_{datetime.now():%Y%m%d}.log"
    log_file.write_text(log_file.read_text() + f"[{datetime.now():%H:%M:%S}] {lvl}: {msg}\n" if log_file.exists() else "")

# -------- QUARANTINE (WITH ATTITUDE) --------
class QuarantineManager:
    @staticmethod
    def quarantine(path: Path) -> bool:
        try:
            q_name = f"{path.name}.{int(time.time())}.exiled"
            q_path = QUAR_DIR / q_name
            shutil.move(str(path), str(q_path))
            meta = q_path.with_suffix(".meta")
            meta.write_text(json.dumps({"original": str(path), "sha256": sha256(q_path)}, indent=2))
            roast = random.choice(SASS_LINES)
            log_sass(f"Sent {path.name} to digital jail. {roast}")
            return True
        except Exception as e:
            log_sass(f"Failed to exile {path.name}: {e}")
            return False

# -------- SASSY SCAN ENGINE --------
class SassyScanner:
    def __init__(self):
        self.hits = []
        self.stats = {"files": 0, "procs": 0, "start": time.time()}

    def scan_processes(self):
        for p in psutil.process_iter(['pid', 'name', 'exe', 'memory_info']):
            try:
                self.stats["procs"] += 1
                name = p.info['name'].lower()
                if name in WHITELIST:
                    continue
                score = 0
                flags = []

                if p.info['memory_info'] and p.info['memory_info'].rss > 600 * 1024 * 1024:
                    score += 25
                    flags.append("memory_hog")
                exe = Path(p.info['exe'] or "")
                if exe.exists():
                    score += self._scan_file(exe)
                if score >= 50:
                    self.hits.append({"type": "process", "pid": p.pid, "name": name, "score": score, "flags": flags})
            except Exception:
                pass

    def scan_files(self, root: Path):
        for path in root.rglob("*"):
            if not path.is_file() or path.suffix.lower() not in {'.exe', '.dll', '.scr', '.vbs', '.ps1', '.js'}:
                continue
            if path.stat().st_size > MAX_FILE_SCAN:
                log_sass(f"{path.name} is chunkier than a Yeti, skipping.")
                continue
            self.stats["files"] += 1
            score = self._scan_file(path)
            if score:
                self.hits.append({"type": "file", "path": str(path), "score": score})

    def _scan_file(self, path: Path) -> int:
        try:
            head = path.open("rb").read(4096)
            for name, sig, score, roast in YARA_RULES:
                if sig in head:
                    log_sass(f"{path.name}: {roast}")
                    return score
            if head[0:2] != b"MZ" and path.suffix == ".exe":
                return 40  # Fake PE
        except Exception:
            pass
        return 0

# -------- MAIN CLASS (EXTRA SASS) --------
class MadAntivirus:
    def __init__(self):
        ensure_dirs()
        self.report = {
            "meta": {
                "version": "3.0-roast",
                "scan_id": hashlib.md5(str(time.time()).encode()).hexdigest()[:6],
                "integrity_ok": sha256(Path(__file__)) == INTEGRITY_HASH
            },
            "system": self._snapshot(),
            "findings": [],
            "quarantined": [],
            "sass_line": random.choice(SASS_LINES)
        }

    def scan(self, root: Path = None):
        sassy = SassyScanner()
        sassy.scan_processes()
        sassy.scan_files(root or Path.home())
        self.report["findings"] = sassy.hits
        self.report["stats"] = {"files": sassy.stats["files"], "procs": sassy.stats["procs"],
                                "duration": round(time.time() - sassy.stats["start"], 2)}
        for hit in [h for h in sassy.hits if h["score"] >= 75]:
            if hit["type"] == "file":
                QuarantineManager.quarantine(Path(hit["path"]))
                self.report["quarantined"].append(hit["path"])
        return self.report

    def _snapshot(self):
        return {
            "cpu": f"{psutil.cpu_percent()}%",
            "ram": f"{psutil.virtual_memory().percent}%",
            "disks": {d.device: f"{psutil.disk_usage(d.mountpoint).percent}%" for d in psutil.disk_partitions()}
        }

    def roast_report(self) -> str:
        r = self.report
        lines = [
            f"🔥 TechSewa Roast Report [ID: {r['meta']['scan_id']}]",
            "=" * 60,
            f"CPU: {r['system']['cpu']} | RAM: {r['system']['ram']}",
            f"Scanned {r['stats']['files']} files & {r['stats']['procs']} processes in {r['stats']['duration']}s",
            "\n💣 Findings:",
        ]
        for f in r["findings"]:
            lines.append(f"  • {f['type']} {f.get('path', '')} (score {f['score']})")
        if r["quarantined"]:
            lines.append("\n🧹 Quarantined:")
            lines.extend(f"  - {Path(p).name}" for p in r["quarantined"])
        lines.append(f"\n💬 Parting wisdom: {r['sass_line']}")
        return "\n".join(lines)

# -------- CLI --------
if __name__ == "__main__":
    print("🧨 TechSewa Mad Antivirus – Roasting your PC since 2024")
    av = MadAntivirus()
    rep = av.scan()
    print(av.roast_report())
    (LOG_DIR / f"report_{rep['meta']['scan_id']}.txt").write_text(av.roast_report())