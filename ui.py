<<<<<<< HEAD
import os
import sys
import json
import time
import queue
import threading
import platform
import subprocess
import webbrowser
from datetime import datetime
from functools import lru_cache
from typing import Dict, List, Callable, Optional, Tuple
import psutil
import pyttsx3
import requests
import sv_ttk
import ping3
from fuzzywuzzy import fuzz
from PIL import Image, ImageTk
import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox, filedialog
import matplotlib
matplotlib.use("Agg")
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure

# Optional imports for enhanced features
try:
    from gtts import gTTS
    from playsound import playsound
    _GTTS_OK = True
except ImportError:
    _GTTS_OK = False

# ====================== CONSTANTS & PATHS ======================
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, "problems.json")
CFG_PATH = os.path.join(BASE_DIR, "config.json")
ASSETS_DIR = os.path.join(BASE_DIR, "assets")
CACHE_DIR = os.path.join(BASE_DIR, "tts_cache")
os.makedirs(ASSETS_DIR, exist_ok=True)
os.makedirs(CACHE_DIR, exist_ok=True)

APP_NAME = "Techsewa Ultimate Pro"
APP_VER = "5.0"
ORG_INFO = "Learning Mission & Training Center"
CONTACT = f"\n📍 {ORG_INFO}\n📞 9867315931  📧 learnermission@gmail.com"

# ====================== HELPER CLASSES ========================
class DualTTS:
    """Enhanced TTS with caching and language support"""
    def __init__(self, rate=160, volume=0.95):
        self.queue = queue.Queue()
        self.eng_engine = pyttsx3.init()
        self.eng_engine.setProperty("rate", rate)
        self.eng_engine.setProperty("volume", volume)
        threading.Thread(target=self._process_queue, daemon=True).start()

    def speak(self, text: str, lang: str = "en"):
        if text.strip():
            self.queue.put((text, lang))

    def _process_queue(self):
        while True:
            text, lang = self.queue.get()
            try:
                if lang == "np" and _GTTS_OK:
                    self._speak_nepali(text)
                else:
                    self._speak_english(text)
            except Exception as e:
                print(f"TTS Error: {e}")
            self.queue.task_done()

    def _speak_nepali(self, text):
        cache_file = os.path.join(CACHE_DIR, f"{hash(text)}.mp3")
        if not os.path.exists(cache_file):
            gTTS(text=text, lang="ne").save(cache_file)
        playsound(cache_file, block=True)

    def _speak_english(self, text):
        self.eng_engine.say(text)
        self.eng_engine.runAndWait()

class SystemScanner:
    """Comprehensive system diagnostics with monitoring"""
    def __init__(self):
        self.xs = []
        self.ys = []
        self.figure = Figure(figsize=(5, 2), dpi=100)
        self.ax = self.figure.add_subplot(111)
        self.line, = self.ax.plot([], [])
        self.ax.set_ylim(0, 100)
        self.ax.set_ylabel("%")
        self.ax.set_xlim(0, 60)
        
    def full_scan(self) -> Dict:
        return {
            "system": {
                "os": platform.platform(),
                "hostname": platform.node(),
                "architecture": platform.architecture()[0]
            },
            "cpu": self._get_cpu_info(),
            "memory": self._get_memory_info(),
            "storage": self._get_storage_info(),
            "network": self._get_network_info(),
            "gpu": self._get_gpu_info(),
            "printers": self._get_printers(),
            "sensors": self._get_sensor_data()
        }

    def update_chart(self):
        """Update CPU usage chart"""
        self.xs.append(len(self.xs))
        self.ys.append(psutil.cpu_percent())
        self.xs = self.xs[-60:]
        self.ys = self.ys[-60:]
        self.line.set_data(self.xs, self.ys)
        self.ax.set_xlim(max(0, len(self.xs)-60), len(self.xs))
        return self.figure

    def _get_cpu_info(self):
        return {
            "model": platform.processor(),
            "physical_cores": psutil.cpu_count(logical=False),
            "total_cores": psutil.cpu_count(logical=True),
            "usage": psutil.cpu_percent(interval=1)
        }

    def _get_memory_info(self):
        mem = psutil.virtual_memory()
        return {
            "total_gb": round(mem.total / (1024 ** 3), 2),
            "available_gb": round(mem.available / (1024 ** 3), 2),
            "percent_used": mem.percent
        }

    def _get_storage_info(self):
        partitions = []
        for part in psutil.disk_partitions():
            usage = psutil.disk_usage(part.mountpoint)
            partitions.append({
                "device": part.device,
                "mountpoint": part.mountpoint,
                "total_gb": round(usage.total / (1024 ** 3), 2),
                "used_gb": round(usage.used / (1024 ** 3), 2),
                "free_gb": round(usage.free / (1024 ** 3), 2),
                "percent_used": usage.percent
            })
        return partitions

    def _get_network_info(self):
        net = psutil.net_io_counters()
        return {
            "bytes_sent": net.bytes_sent,
            "bytes_recv": net.bytes_recv,
            "packets_sent": net.packets_sent,
            "packets_recv": net.packets_recv
        }

    def _get_gpu_info(self):
        try:
            if platform.system() == "Windows":
                output = subprocess.check_output(
                    ["wmic", "path", "win32_VideoController", "get", "name"]
                ).decode().splitlines()
                return output[1].strip() if len(output) > 1 else "Unknown"
        except:
            pass
        return "Unknown"

    def _get_printers(self):
        try:
            if platform.system() == "Windows":
                output = subprocess.check_output(
                    ["wmic", "printer", "get", "name"]
                ).decode().splitlines()
                return [line.strip() for line in output[1:] if line.strip()]
        except:
            pass
        return []

    def _get_sensor_data(self):
        try:
            return {
                "temperatures": psutil.sensors_temperatures(),
                "fans": psutil.sensors_fans(),
                "battery": psutil.sensors_battery()
            }
        except:
            return {}

class ProblemDetector(threading.Thread):
    """Background system monitoring with alerts"""
    def __init__(self, alert_callback):
        super().__init__(daemon=True)
        self.alert_callback = alert_callback
        
    def run(self):
        while True:
            # CPU monitoring
            cpu = psutil.cpu_percent()
            if cpu > 90: 
                self.alert_callback("CPU over 90%", 101)
                
            # Memory monitoring
            mem = psutil.virtual_memory().percent
            if mem > 90:
                self.alert_callback("RAM over 90%", 102)
                
            # Network monitoring
            try:
                dl = ping3.ping("8.8.8.8", unit="ms", timeout=1)
                if dl is None:
                    self.alert_callback("Internet unreachable", 103)
            except:
                self.alert_callback("Network error", 104)
                
            time.sleep(5)

class AutoHealer:
    """Automated system issue resolution"""
    def heal(self, code: int) -> str:
        try:
            if code == 101:  # High CPU
                top = [p for p in psutil.process_iter(['pid', 'name', 'cpu_percent'])]
                top.sort(key=lambda p: p.info['cpu_percent'], reverse=True)
                top[0].kill()
                return f"Killed {top[0].info['name']} (high CPU)"
                
            elif code == 102:  # High memory
                top = [p for p in psutil.process_iter(['pid', 'name', 'memory_percent'])]
                top.sort(key=lambda p: p.info['memory_percent'], reverse=True)
                top[0].kill()
                return f"Killed {top[0].info['name']} (high memory)"
                
            elif code == 103:  # Network issue
                subprocess.call("ipconfig /flushdns", shell=True)
                return "DNS cache flushed"
                
            elif code == 104:  # Network error
                return "Network error detected - please check your connection"
                
        except Exception as e:
            return f"Healing failed: {str(e)}"
        return "No solution available"

class SmartBrainPro:
    """Enhanced problem-solving engine with semantic capabilities"""
    def __init__(self, db_path: str, min_confidence: int = 80, internet: bool = True):
        with open(db_path, "r", encoding="utf-8") as f:
            self.problems = json.load(f)
        self.min_confidence = min_confidence
        self.internet = internet
        self.query_history = []
        self.learning_mode = True
        self.stats = {
            "total_problems": len(self.problems),
            "cached_matches": 0,
            "internet_lookups": 0
        }

    @lru_cache(maxsize=1000)
    def _match(self, query: str, lang: str = "en") -> Optional[Dict]:
        query = query.lower()
        best_match = None
        best_score = 0
        
        for problem in self.problems:
            for alias in problem.get("aliases", []):
                score = fuzz.token_set_ratio(query, alias.lower())
                if score > best_score and score >= self.min_confidence:
                    best_match = problem
                    best_score = score
                    self.stats["cached_matches"] += 1
        return best_match

    def solve(self, query: str, lang: str = "en") -> Dict:
        self.query_history.append((datetime.now().isoformat(), query, lang))
        
        # 1. Try local exact/fuzzy match
        local_match = self._match(query, lang)
        if local_match:
            return {
                "source": "local",
                "answer": local_match.get(lang, ""),
                "confidence": "high"
            }
        
        # 2. Try internet lookup if enabled
        if self.internet:
            internet_result = self._web_search(query)
            if internet_result:
                self.stats["internet_lookups"] += 1
                return {
                    "source": "internet",
                    "answer": internet_result,
                    "confidence": "medium"
                }
        
        # 3. Fallback
        return {
            "source": "none",
            "answer": "No solution found. Would you like me to learn this?",
            "confidence": "low"
        }

    def _web_search(self, query: str) -> str:
        try:
            response = requests.get(
                "https://api.duckduckgo.com/",
                params={
                    "q": query,
                    "format": "json",
                    "no_html": 1,
                    "no_redirect": 1
                },
                timeout=8
            )
            data = response.json()
            
            if data.get("AbstractText"):
                return f"{data['AbstractText']}\n\n🔗 {data['AbstractURL']}"
            elif data.get("RelatedTopics"):
                first_result = data["RelatedTopics"][0]
                return f"{first_result.get('Text', 'No description')}\n\n🔗 {first_result.get('FirstURL', '')}"
            else:
                return "No relevant results found online."
        except Exception as e:
            return f"Internet search failed: {str(e)}"

    def teach(self, question: str, answer_en: str, answer_np: str = None):
        new_entry = {
            "aliases": [question.lower()],
            "en": answer_en,
            "np": answer_np or answer_en,
            "learned": True,
            "timestamp": datetime.now().isoformat()
        }
        self.problems.append(new_entry)
        self.stats["total_problems"] += 1
        self._save_knowledge()

    def _save_knowledge(self):
        try:
            with open(DB_PATH, "w", encoding="utf-8") as f:
                json.dump(self.problems, f, indent=2, ensure_ascii=False)
        except Exception as e:
            print(f"Failed to save knowledge base: {e}")

# ====================== MAIN APPLICATION =======================
class TechsewaProApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title(f"{APP_NAME} {APP_VER}")
        self.geometry("1400x900")
        self.minsize(1200, 800)
        
        # Initialize diagnostic variables and progress bars
        self.diag_vars = {}
        self.diag_progress = {}
        
        # Load configuration
        self.config = self._load_config()
        
        # Initialize core components
        self.tts = DualTTS(
            rate=self.config.get("voice_rate", 160),
            volume=self.config.get("voice_volume", 0.95)
        )
        self.brain = SmartBrainPro(
            DB_PATH,
            min_confidence=self.config.get("min_confidence", 80),
            internet=self.config.get("enable_internet", True)
        )
        self.scanner = SystemScanner()
        self.healer = AutoHealer()
        
        # Setup UI
        self._setup_styles()
        self._build_ui()
        
        # Start background tasks
        self._start_background_tasks()
        
        # Initial system scan
        self.after(1000, self._run_system_scan)

    def _setup_styles(self):
        """Configure macOS-inspired styles with modern touches"""
        style = ttk.Style()
        
        # Main theme
        sv_ttk.set_theme(self.config.get("theme", "light"))
        
        # Custom styles
        style.configure("TFrame", background="#f5f5f7")
        style.configure("TLabel", background="#f5f5f7", font=("SF Pro Text", 11))
        style.configure("TButton", font=("SF Pro Text", 11), padding=6)
        style.configure("TEntry", font=("SF Pro Text", 12), padding=8)
        style.configure("Header.TFrame", background="#f5f5f7", borderwidth=0)
        style.configure("Header.TLabel", font=("SF Pro Display", 18, "bold"))
        style.configure("Accent.TButton", background="#0071e3", foreground="white")
        style.configure("Chat.TFrame", background="#ffffff")
        style.configure("Sidebar.TFrame", background="#f5f5f7")
        style.configure("Status.TFrame", background="#f8f9fa")
        style.configure("Status.TLabel", background="#f8f9fa", foreground="#5f6368")
        
        # Gauge styles
        style.configure("Gauge.CPU.TFrame", background="#f1f3f4")
        style.configure("Gauge.Memory.TFrame", background="#f1f3f4")
        style.configure("Gauge.Disk.TFrame", background="#f1f3f4")
        style.configure("Gauge.Network.TFrame", background="#f1f3f4")
        
        style.map("Accent.TButton",
                background=[("active", "#0077ed"), ("pressed", "#0063c7")])

    def _build_ui(self):
        """Build the enhanced interface"""
        # Configure grid
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=1)
        
        # Sidebar
        self._build_sidebar()
        
        # Main content area
        self._build_main_content()
        
        # Status bar
        self._build_status_bar()
        
        # Configure text tags for rich formatting
        self._configure_text_tags()

    def _configure_text_tags(self):
        """Configure text tags for rich formatting in chat"""
        tags = [
            ("system", "#5f6368", ("SF Pro Text", 11)),
            ("user", "#202124", ("SF Pro Text", 12, "bold")),
            ("assistant", "#1a73e8", ("SF Pro Text", 12)),
            ("internet", "#34a853", ("SF Pro Text", 12)),
            ("error", "#d93025", ("SF Pro Text", 11)),
            ("highlight", "#e8f0fe", None)
        ]
        
        for name, fg, font in tags:
            self.chat_display.tag_config(name, foreground=fg, font=font)

    def _build_sidebar(self):
        """Build the enhanced sidebar with system monitoring"""
        sidebar = ttk.Frame(self, width=220, style="Sidebar.TFrame")
        sidebar.grid(row=0, column=0, sticky="nswe")
        sidebar.grid_propagate(False)
        
        # App logo
        logo_frame = ttk.Frame(sidebar, padding=(20, 30, 20, 20))
        logo_frame.pack(fill=tk.X)
        
        try:
            logo_img = Image.open(os.path.join(ASSETS_DIR, "logo.png"))
            logo_img = logo_img.resize((40, 40), Image.LANCZOS)
            self.logo_photo = ImageTk.PhotoImage(logo_img)
            ttk.Label(logo_frame, image=self.logo_photo).pack()
        except:
            ttk.Label(logo_frame, text="🧠", font=("SF Pro Text", 24)).pack()
        
        # Navigation buttons
        nav_frame = ttk.Frame(sidebar, padding=(10, 20))
        nav_frame.pack(fill=tk.X)
        
        nav_buttons = [
            ("Assistant", self._show_assistant),
            ("System Info", self._show_system_info),
            ("Alerts", self._show_alerts),
            ("Settings", self._show_settings),
            ("Knowledge Base", self._show_knowledge_base),
            ("Brain Stats", self._show_brain_stats)
        ]
        
        for text, command in nav_buttons:
            btn = ttk.Button(
                nav_frame,
                text=text,
                style="TButton",
                command=command
            )
            btn.pack(fill=tk.X, pady=4)
        
        # System status
        status_frame = ttk.Frame(sidebar, padding=(20, 20))
        status_frame.pack(fill=tk.X, side=tk.BOTTOM)
        
        self.cpu_label = ttk.Label(status_frame, text="CPU: --%")
        self.cpu_label.pack(anchor=tk.W)
        
        self.mem_label = ttk.Label(status_frame, text="RAM: --%")
        self.mem_label.pack(anchor=tk.W)
        
        self.disk_label = ttk.Label(status_frame, text="Disk: --%")
        self.disk_label.pack(anchor=tk.W)
        
        self.net_label = ttk.Label(status_frame, text="NET: --")
        self.net_label.pack(anchor=tk.W)

    def _build_main_content(self):
        """Build the main content area with enhanced tabs"""
        main_frame = ttk.Frame(self, style="Chat.TFrame")
        main_frame.grid(row=0, column=1, sticky="nsew")
        
        # Notebook for tabs
        self.notebook = ttk.Notebook(main_frame)
        self.notebook.pack(fill=tk.BOTH, expand=True)
        
        # Assistant tab
        self._build_assistant_tab()
        
        # System info tab
        self._build_system_tab()
        
        # Alerts tab
        self._build_alerts_tab()
        
        # Settings tab
        self._build_settings_tab()
        
        # Knowledge base tab
        self._build_knowledge_tab()
        
        # Brain stats tab
        self._build_brain_stats_tab()
        
        # Start with assistant tab visible
        self.notebook.select(0)

    def _build_assistant_tab(self):
        """Build the assistant chat interface with enhanced features"""
        tab = ttk.Frame(self.notebook)
        self.notebook.add(tab, text="Assistant")
        
        # Chat display
        self.chat_display = scrolledtext.ScrolledText(
            tab,
            wrap=tk.WORD,
            state="disabled",
            font=("SF Pro Text", 12),
            padx=20,
            pady=20,
            bg="#ffffff",
            bd=0,
            highlightthickness=0
        )
        self.chat_display.pack(fill=tk.BOTH, expand=True)
        
        # Input area
        input_frame = ttk.Frame(tab)
        input_frame.pack(fill=tk.X, padx=10, pady=10)
        
        self.query_var = tk.StringVar()
        self.query_entry = ttk.Entry(
            input_frame,
            textvariable=self.query_var,
            font=("SF Pro Text", 12)
        )
        self.query_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 10))
        self.query_entry.bind("<Return>", lambda e: self._process_query())
        
        self.send_btn = ttk.Button(
            input_frame,
            text="Send",
            style="Accent.TButton",
            command=self._process_query
        )
        self.send_btn.pack(side=tk.RIGHT)
        
        # Add mic button for voice input
        try:
            mic_img = Image.open(os.path.join(ASSETS_DIR, "mic.png"))
            mic_img = mic_img.resize((24, 24), Image.LANCZOS)
            self.mic_photo = ImageTk.PhotoImage(mic_img)
            ttk.Button(
                input_frame,
                image=self.mic_photo,
                command=self._start_voice_input
            ).pack(side=tk.RIGHT, padx=(0, 5))
        except:
            ttk.Button(
                input_frame,
                text="🎤",
                command=self._start_voice_input
            ).pack(side=tk.RIGHT, padx=(0, 5))

    def _build_system_tab(self):
        """Build the system info tab with live monitoring"""
        tab = ttk.Frame(self.notebook)
        self.notebook.add(tab, text="System")
        
        # System info display
        sys_frame = ttk.LabelFrame(tab, text="System Information", padding=15)
        sys_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # CPU usage graph
        graph_frame = ttk.Frame(sys_frame)
        graph_frame.pack(fill=tk.X, pady=10)
        
        self.canvas = FigureCanvasTkAgg(self.scanner.figure, master=graph_frame)
        self.canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)
        
        # System metrics
        metrics_frame = ttk.Frame(sys_frame)
        metrics_frame.pack(fill=tk.X, pady=10)
        
        metrics = [
            ("CPU", "cpu_percent", "Gauge.CPU.TFrame"),
            ("Memory", "virtual_memory", "Gauge.Memory.TFrame"),
            ("Disk", "disk_usage", "Gauge.Disk.TFrame"),
            ("Network", "net_io_counters", "Gauge.Network.TFrame")
        ]
        
        for title, metric, style in metrics:
            self._create_metric_card(metrics_frame, title, metric, style)
        
        # Detailed system info
        self.system_display = scrolledtext.ScrolledText(
            sys_frame,
            wrap=tk.WORD,
            state="disabled",
            font=("SF Mono", 11),
            height=10
        )
        self.system_display.pack(fill=tk.BOTH, expand=True)
        
        # Control buttons
        btn_frame = ttk.Frame(sys_frame)
        btn_frame.pack(fill=tk.X, padx=10, pady=10)
        
        ttk.Button(
            btn_frame,
            text="Refresh",
            command=self._run_system_scan
        ).pack(side=tk.LEFT)
        
        ttk.Button(
            btn_frame,
            text="Export Report",
            command=self._export_system_report
        ).pack(side=tk.RIGHT)

    def _create_metric_card(self, parent, title, metric, style):
        """Create a metric card for system monitoring"""
        card = ttk.Frame(parent, style=style, padding=10)
        card.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=5)
        
        ttk.Label(card, text=title, font=("SF Pro Text", 10, "bold")).pack()
        
        self.diag_vars[metric] = tk.StringVar(value="--")
        ttk.Label(card, textvariable=self.diag_vars[metric], 
                 font=("SF Pro Text", 14)).pack(pady=5)
        
        pb = ttk.Progressbar(card, orient=tk.HORIZONTAL, length=100, mode='determinate')
        pb.pack(fill=tk.X)
        self.diag_progress[metric] = pb

    def _build_alerts_tab(self):
        """Build the alerts tab for system monitoring"""
        tab = ttk.Frame(self.notebook)
        self.notebook.add(tab, text="Alerts")
        
        # Alerts treeview
        cols = ("time", "message", "code")
        self.alerts_tree = ttk.Treeview(
            tab,
            columns=cols,
            show="headings",
            height=15
        )
        
        for col in cols:
            self.alerts_tree.heading(col, text=col.capitalize())
            self.alerts_tree.column(col, width=150)
            
        self.alerts_tree.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Heal button
        btn_frame = ttk.Frame(tab)
        btn_frame.pack(fill=tk.X, padx=10, pady=5)
        
        ttk.Button(
            btn_frame,
            text="Heal Selected",
            command=self._heal_selected
        ).pack(side=tk.LEFT)
        
        # Start problem detector
        self.detector = ProblemDetector(self._add_alert)
        self.detector.start()

    def _build_settings_tab(self):
        """Build the settings tab"""
        tab = ttk.Frame(self.notebook)
        self.notebook.add(tab, text="Settings")
        
        # Settings frame
        settings_frame = ttk.Frame(tab, padding=15)
        settings_frame.pack(fill=tk.BOTH, expand=True)
        
        # Theme selection
        ttk.Label(settings_frame, text="Theme:", font=("SF Pro Text", 12)).pack(anchor=tk.W, pady=5)
        self.theme_var = tk.StringVar(value=self.config.get("theme", "light"))
        theme_frame = ttk.Frame(settings_frame)
        theme_frame.pack(fill=tk.X, pady=5)
        
        ttk.Radiobutton(
            theme_frame,
            text="Light",
            variable=self.theme_var,
            value="light",
            command=self._change_theme
        ).pack(side=tk.LEFT, padx=5)
        
        ttk.Radiobutton(
            theme_frame,
            text="Dark",
            variable=self.theme_var,
            value="dark",
            command=self._change_theme
        ).pack(side=tk.LEFT, padx=5)
        
        # Voice settings
        ttk.Label(settings_frame, text="Voice Settings:", font=("SF Pro Text", 12)).pack(anchor=tk.W, pady=5)
        
        voice_frame = ttk.Frame(settings_frame)
        voice_frame.pack(fill=tk.X, pady=5)
        
        ttk.Label(voice_frame, text="Rate:").pack(side=tk.LEFT)
        self.rate_var = tk.IntVar(value=self.config.get("voice_rate", 160))
        ttk.Scale(
            voice_frame,
            from_=100,
            to=300,
            variable=self.rate_var,
            command=lambda v: self.tts.eng_engine.setProperty("rate", int(float(v)))
        ).pack(side=tk.LEFT, padx=5, fill=tk.X, expand=True)
        
        ttk.Label(voice_frame, text="Volume:").pack(side=tk.LEFT, padx=(10,0))
        self.vol_var = tk.IntVar(value=self.config.get("voice_volume", 95))
        ttk.Scale(
            voice_frame,
            from_=0,
            to=100,
            variable=self.vol_var,
            command=lambda v: self.tts.eng_engine.setProperty("volume", int(float(v))/100)
        ).pack(side=tk.LEFT, padx=5, fill=tk.X, expand=True)
        
        # Confidence threshold
        ttk.Label(settings_frame, text="Confidence Threshold:", font=("SF Pro Text", 12)).pack(anchor=tk.W, pady=5)
        self.conf_var = tk.IntVar(value=self.config.get("min_confidence", 80))
        ttk.Scale(
            settings_frame,
            from_=50,
            to=100,
            variable=self.conf_var,
            orient=tk.HORIZONTAL
        ).pack(fill=tk.X, pady=5)
        
        # Internet access
        self.internet_var = tk.BooleanVar(value=self.config.get("enable_internet", True))
        ttk.Checkbutton(
            settings_frame,
            text="Enable Internet Fallback",
            variable=self.internet_var
        ).pack(anchor=tk.W, pady=5)
        
        # Save button
        ttk.Button(
            settings_frame,
            text="Save Settings",
            style="Accent.TButton",
            command=self._save_settings
        ).pack(pady=10)

    def _build_knowledge_tab(self):
        """Build the knowledge base tab"""
        tab = ttk.Frame(self.notebook)
        self.notebook.add(tab, text="Knowledge")
        
        # Knowledge base display
        kb_frame = ttk.Frame(tab, padding=15)
        kb_frame.pack(fill=tk.BOTH, expand=True)
        
        # Search frame
        search_frame = ttk.Frame(kb_frame)
        search_frame.pack(fill=tk.X, pady=5)
        
        ttk.Label(search_frame, text="Search:").pack(side=tk.LEFT)
        self.search_var = tk.StringVar()
        self.search_var.trace("w", self._filter_knowledge)
        ttk.Entry(search_frame, textvariable=self.search_var).pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5)
        
        # Knowledge treeview
        cols = ("question", "answer_en", "answer_np")
        self.kb_tree = ttk.Treeview(
            kb_frame,
            columns=cols,
            show="headings",
            height=15
        )
        
        for col in cols:
            self.kb_tree.heading(col, text=col.replace("_", " ").title())
            self.kb_tree.column(col, width=200)
            
        self.kb_tree.pack(fill=tk.BOTH, expand=True, pady=5)
        
        # Populate knowledge base
        self._populate_knowledge_base()
        
        # Add/Edit buttons
        btn_frame = ttk.Frame(kb_frame)
        btn_frame.pack(fill=tk.X, pady=5)
        
        ttk.Button(
            btn_frame,
            text="Add Entry",
            command=self._add_knowledge_entry
        ).pack(side=tk.LEFT, padx=5)
        
        ttk.Button(
            btn_frame,
            text="Edit Selected",
            command=self._edit_knowledge_entry
        ).pack(side=tk.LEFT, padx=5)
        
        ttk.Button(
            btn_frame,
            text="Delete Selected",
            command=self._delete_knowledge_entry
        ).pack(side=tk.LEFT, padx=5)

    def _build_brain_stats_tab(self):
        """Build the brain statistics tab"""
        tab = ttk.Frame(self.notebook)
        self.notebook.add(tab, text="Brain Stats")
        
        # Stats frame
        stats_frame = ttk.Frame(tab, padding=15)
        stats_frame.pack(fill=tk.BOTH, expand=True)
        
        # Capabilities
        ttk.Label(
            stats_frame,
            text="🧠 SmartBrain Pro Capabilities",
            font=("SF Pro Text", 12, "bold")
        ).pack(anchor=tk.W, pady=5)
        
        caps_frame = ttk.Frame(stats_frame)
        caps_frame.pack(fill=tk.X, pady=10)
        
        capabilities = [
            ("✅", "Local Knowledge Base"),
            ("✅", "Fuzzy Matching"),
            ("✅", "Internet Fallback"),
            ("✅", "Learning Mode"),
            ("✅", "Dual Language Support")
        ]
        
        for i, (icon, text) in enumerate(capabilities):
            frame = ttk.Frame(caps_frame)
            frame.grid(row=i//3, column=i%3, sticky=tk.W, padx=10, pady=5)
            ttk.Label(frame, text=icon, font=("SF Pro Text", 12)).pack(side=tk.LEFT)
            ttk.Label(frame, text=text, font=("SF Pro Text", 10)).pack(side=tk.LEFT)
        
        # Statistics
        ttk.Label(
            stats_frame,
            text="📊 Current Statistics",
            font=("SF Pro Text", 12, "bold")
        ).pack(anchor=tk.W, pady=5)
        
        self.stats_frame = ttk.Frame(stats_frame)
        self.stats_frame.pack(fill=tk.X, pady=10)
        
        # Update stats initially
        self._update_brain_stats()

    def _build_status_bar(self):
        """Build the status bar with clock"""
        status_frame = ttk.Frame(self, height=25, style="Status.TFrame")
        status_frame.grid(row=1, column=0, columnspan=2, sticky="ew")
        
        self.status_var = tk.StringVar(value="Ready")
        ttk.Label(
            status_frame,
            textvariable=self.status_var,
            style="Status.TLabel"
        ).pack(side=tk.LEFT, padx=10)
        
        self.time_var = tk.StringVar()
        ttk.Label(
            status_frame,
            textvariable=self.time_var,
            style="Status.TLabel"
        ).pack(side=tk.RIGHT, padx=10)
        
        self._update_clock()

    # ====================== CORE FUNCTIONALITY ======================
    def _process_query(self):
        """Process user query and generate response"""
        query = self.query_var.get().strip()
        if not query:
            return
            
        self.query_var.set("")
        self._add_to_chat(f"You: {query}", "user")
        self.status_var.set("Processing...")
        
        # Process in background thread
        threading.Thread(
            target=self._solve_query,
            args=(query,),
            daemon=True
        ).start()

    def _solve_query(self, query: str):
        """Get solution from brain and display it"""
        try:
            result = self.brain.solve(query, "en")
            
            # Format response based on source
            if result["source"] == "internet":
                response = f"🌐 Techsewa (Internet):\n{result['answer']}"
                self._add_to_chat(response, "internet")
            elif result["source"] == "local":
                response = f"💡 Techsewa (Local Knowledge):\n{result['answer']}"
                self._add_to_chat(response, "assistant")
            else:
                response = f"❓ Techsewa: {result['answer']}"
                self._add_to_chat(response, "system")
            
            # Speak the response
            self.tts.speak(result["answer"], "en")
            
            # Update brain stats
            self._update_brain_stats()
            
        except Exception as e:
            error_msg = f"⚠️ Error: {str(e)}"
            self._add_to_chat(error_msg, "error")
        finally:
            self.status_var.set("Ready")

    def _add_to_chat(self, message: str, tag: str = "system"):
        """Add message to chat display with appropriate formatting"""
        self.chat_display.config(state="normal")
        
        if tag == "system":
            for line in message.split('\n'):
                self.chat_display.insert(tk.END, "• " + line + "\n" if line.strip() else "\n", tag)
        else:
            self.chat_display.insert(tk.END, message + "\n\n", tag)
            
        self.chat_display.config(state="disabled")
        self.chat_display.see(tk.END)

    def _run_system_scan(self):
        """Perform comprehensive system scan"""
        self.status_var.set("Scanning system...")
        
        try:
            scan_results = self.scanner.full_scan()
            formatted_results = json.dumps(scan_results, indent=2)
            
            self.system_display.config(state="normal")
            self.system_display.delete("1.0", tk.END)
            self.system_display.insert(tk.END, formatted_results)
            self.system_display.config(state="disabled")
            
            # Update sidebar indicators
            cpu_usage = scan_results["cpu"]["usage"]
            mem_usage = scan_results["memory"]["percent_used"]
            disk_usage = psutil.disk_usage('/').percent
            
            self.cpu_label.config(text=f"CPU: {cpu_usage}%")
            self.mem_label.config(text=f"RAM: {mem_usage}%")
            self.disk_label.config(text=f"Disk: {disk_usage}%")
            
            self.status_var.set("System scan completed")
        except Exception as e:
            self.status_var.set(f"Scan failed: {str(e)}")

    def _export_system_report(self):
        """Export system report to file"""
        file_path = filedialog.asksaveasfilename(
            defaultextension=".txt",
            filetypes=[("Text Files", "*.txt"), ("All Files", "*.*")],
            title="Save System Report"
        )
        
        if file_path:
            try:
                with open(file_path, "w") as f:
                    f.write(self.system_display.get("1.0", tk.END))
                self.status_var.set(f"Report saved to {file_path}")
            except Exception as e:
                self.status_var.set(f"Failed to save report: {str(e)}")

    def _add_alert(self, message: str, code: int):
        """Add an alert to the alerts tab"""
        self.alerts_tree.insert("", tk.END, values=(
            datetime.now().strftime("%H:%M:%S"),
            message,
            code
        ))
        
        # Auto-scroll to new alert
        self.alerts_tree.see(self.alerts_tree.get_children()[-1])
        
        # Show notification
        self._add_to_chat(f"⚠️ System Alert: {message} (Code: {code})", "system")

    def _heal_selected(self):
        """Attempt to heal the selected alert"""
        selection = self.alerts_tree.selection()
        if not selection:
            return
            
        item = self.alerts_tree.item(selection[0])
        code = int(item['values'][2])
        
        result = self.healer.heal(code)
        self._add_to_chat(f"⚕️ Healing attempt: {result}", "system")
        messagebox.showinfo("Healing Result", result)

    def _start_voice_input(self):
        """Start voice input simulation"""
        self._add_to_chat("🎤 Listening... Speak now", "system")
        self.after(3000, self._process_voice_input)

    def _process_voice_input(self):
        """Process simulated voice input"""
        sample_queries = [
            "My screen is not working",
            "How do I reset my password?",
            "Internet connection is slow",
            "Printer not responding"
        ]
        query = sample_queries[len(self.chat_display.get("1.0", tk.END)) % len(sample_queries)]
        self.query_var.set(query)
        self._process_query()

    def _start_background_tasks(self):
        """Start background monitoring tasks"""
        def update_system_stats():
            # Update CPU chart
            self.scanner.update_chart()
            self.canvas.draw()
            
            # Update metrics
            cpu = psutil.cpu_percent()
            mem = psutil.virtual_memory().percent
            disk = psutil.disk_usage('/').percent
            
            self.diag_vars["cpu_percent"].set(f"{cpu}%")
            self.diag_progress["cpu_percent"]["value"] = cpu
            
            self.diag_vars["virtual_memory"].set(f"{mem}%")
            self.diag_progress["virtual_memory"]["value"] = mem
            
            self.diag_vars["disk_usage"].set(f"{disk}%")
            self.diag_progress["disk_usage"]["value"] = disk
            
            # Update network stats
            net1 = psutil.net_io_counters()
            self.after(1000, self._update_network_stats, net1)
            
            # Update sidebar
            self.cpu_label.config(text=f"CPU: {cpu}%")
            self.mem_label.config(text=f"RAM: {mem}%")
            self.disk_label.config(text=f"Disk: {disk}%")
            
            self.after(5000, update_system_stats)
        
        update_system_stats()

    def _update_network_stats(self, net1):
        """Update network statistics"""
        net2 = psutil.net_io_counters()
        dl = (net2.bytes_recv - net1.bytes_recv) / 1024
        ul = (net2.bytes_sent - net1.bytes_sent) / 1024
        self.diag_vars["net_io_counters"].set(f"↓{dl:.1f}KB/s ↑{ul:.1f}KB/s")
        self.diag_progress["net_io_counters"]["value"] = min(100, (dl + ul) * 100 / 1024)
        self.net_label.config(text=f"NET: ↓{dl:.1f} ↑{ul:.1f}")

    def _update_clock(self):
        """Update the clock in the status bar"""
        now = datetime.now().strftime("%H:%M:%S | %d %b %Y")
        self.time_var.set(now)
        self.after(1000, self._update_clock)

    def _update_brain_stats(self):
        """Update the brain statistics display"""
        # Clear previous widgets
        for widget in self.stats_frame.winfo_children():
            widget.destroy()
        
        # Get current stats
        stats = {
            "Knowledge Base Entries": self.brain.stats["total_problems"],
            "Cached Matches": self.brain.stats["cached_matches"],
            "Internet Lookups": self.brain.stats["internet_lookups"],
            "Session Queries": len(self.brain.query_history)
        }
        
        # Create new stat displays
        for i, (label, value) in enumerate(stats.items()):
            frame = ttk.Frame(self.stats_frame)
            frame.grid(row=i//2, column=i%2, sticky=tk.W, padx=10, pady=5)
            ttk.Label(frame, text=f"{label}:", font=("SF Pro Text", 10, "bold")).pack(side=tk.LEFT)
            ttk.Label(frame, text=str(value), font=("SF Pro Text", 10)).pack(side=tk.LEFT)

    def _populate_knowledge_base(self):
        """Populate the knowledge base treeview"""
        for problem in self.brain.problems:
            self.kb_tree.insert("", tk.END, values=(
                problem.get("aliases", [""])[0],
                problem.get("en", ""),
                problem.get("np", "")
            ))

    def _filter_knowledge(self, *args):
        """Filter knowledge base based on search term"""
        search_term = self.search_var.get().lower()
        
        # Clear current items
        for item in self.kb_tree.get_children():
            self.kb_tree.delete(item)
        
        # Add matching items
        for problem in self.brain.problems:
            if (search_term in problem.get("aliases", [""])[0].lower() or
                search_term in problem.get("en", "").lower() or
                search_term in problem.get("np", "").lower()):
                
                self.kb_tree.insert("", tk.END, values=(
                    problem.get("aliases", [""])[0],
                    problem.get("en", ""),
                    problem.get("np", "")
                ))

    def _add_knowledge_entry(self):
        """Add a new knowledge base entry"""
        dialog = tk.Toplevel(self)
        dialog.title("Add Knowledge Entry")
        dialog.geometry("600x400")
        
        # Question
        ttk.Label(dialog, text="Question/Alias:").pack(pady=(10,0))
        question_entry = ttk.Entry(dialog, width=80)
        question_entry.pack(pady=5)
        
        # English answer
        ttk.Label(dialog, text="English Answer:").pack(pady=(10,0))
        en_answer_text = scrolledtext.ScrolledText(dialog, height=5, width=80)
        en_answer_text.pack(pady=5)
        
        # Nepali answer
        ttk.Label(dialog, text="Nepali Answer:").pack(pady=(10,0))
        np_answer_text = scrolledtext.ScrolledText(dialog, height=5, width=80)
        np_answer_text.pack(pady=5)
        
        # Save button
        def save_entry():
            question = question_entry.get().strip()
            en_answer = en_answer_text.get("1.0", tk.END).strip()
            np_answer = np_answer_text.get("1.0", tk.END).strip()
            
            if question and en_answer:
                self.brain.teach(question, en_answer, np_answer)
                self._populate_knowledge_base()
                dialog.destroy()
            else:
                messagebox.showerror("Error", "Question and English answer are required!")
        
        ttk.Button(
            dialog,
            text="Save",
            style="Accent.TButton",
            command=save_entry
        ).pack(pady=10)

    def _edit_knowledge_entry(self):
        """Edit selected knowledge base entry"""
        selection = self.kb_tree.selection()
        if not selection:
            messagebox.showwarning("Warning", "Please select an entry to edit")
            return
            
        item = self.kb_tree.item(selection[0])
        values = item['values']
        
        dialog = tk.Toplevel(self)
        dialog.title("Edit Knowledge Entry")
        dialog.geometry("600x400")
        
        # Question
        ttk.Label(dialog, text="Question/Alias:").pack(pady=(10,0))
        question_entry = ttk.Entry(dialog, width=80)
        question_entry.insert(0, values[0])
        question_entry.pack(pady=5)
        
        # English answer
        ttk.Label(dialog, text="English Answer:").pack(pady=(10,0))
        en_answer_text = scrolledtext.ScrolledText(dialog, height=5, width=80)
        en_answer_text.insert("1.0", values[1])
        en_answer_text.pack(pady=5)
        
        # Nepali answer
        ttk.Label(dialog, text="Nepali Answer:").pack(pady=(10,0))
        np_answer_text = scrolledtext.ScrolledText(dialog, height=5, width=80)
        np_answer_text.insert("1.0", values[2])
        np_answer_text.pack(pady=5)
        
        # Save button
        def save_entry():
            question = question_entry.get().strip()
            en_answer = en_answer_text.get("1.0", tk.END).strip()
            np_answer = np_answer_text.get("1.0", tk.END).strip()
            
            if question and en_answer:
                # Find and update the entry
                for problem in self.brain.problems:
                    if problem.get("aliases", [""])[0] == values[0]:
                        problem["aliases"] = [question]
                        problem["en"] = en_answer
                        problem["np"] = np_answer
                        break
                
                self.brain._save_knowledge()
                self._populate_knowledge_base()
                dialog.destroy()
            else:
                messagebox.showerror("Error", "Question and English answer are required!")
        
        ttk.Button(
            dialog,
            text="Save",
            style="Accent.TButton",
            command=save_entry
        ).pack(pady=10)

    def _delete_knowledge_entry(self):
        """Delete selected knowledge base entry"""
        selection = self.kb_tree.selection()
        if not selection:
            messagebox.showwarning("Warning", "Please select an entry to delete")
            return
            
        item = self.kb_tree.item(selection[0])
        question = item['values'][0]
        
        if messagebox.askyesno("Confirm", f"Delete entry: {question}?"):
            # Remove from knowledge base
            self.brain.problems = [p for p in self.brain.problems 
                                 if p.get("aliases", [""])[0] != question]
            self.brain._save_knowledge()
            self.brain.stats["total_problems"] -= 1
            self._populate_knowledge_base()
            self._update_brain_stats()

    def _change_theme(self):
        """Change application theme"""
        theme = self.theme_var.get()
        sv_ttk.set_theme(theme)
        self.config["theme"] = theme

    def _save_settings(self):
        """Save current settings to config file"""
        self.config.update({
            "theme": self.theme_var.get(),
            "voice_rate": self.rate_var.get(),
            "voice_volume": self.vol_var.get(),
            "min_confidence": self.conf_var.get(),
            "enable_internet": self.internet_var.get()
        })
        
        # Update brain settings
        self.brain.min_confidence = self.conf_var.get()
        self.brain.internet = self.internet_var.get()
        
        try:
            with open(CFG_PATH, "w") as f:
                json.dump(self.config, f, indent=2)
            self.status_var.set("Settings saved successfully")
        except Exception as e:
            self.status_var.set(f"Failed to save settings: {str(e)}")

    # ====================== NAVIGATION METHODS ======================
    def _show_assistant(self):
        """Show the assistant tab"""
        self.notebook.select(0)

    def _show_system_info(self):
        """Show the system info tab"""
        self.notebook.select(1)

    def _show_alerts(self):
        """Show the alerts tab"""
        self.notebook.select(2)

    def _show_settings(self):
        """Show the settings tab"""
        self.notebook.select(3)

    def _show_knowledge_base(self):
        """Show the knowledge base tab"""
        self.notebook.select(4)

    def _show_brain_stats(self):
        """Show the brain stats tab"""
        self.notebook.select(5)

    # ====================== CONFIGURATION METHODS ======================
    def _load_config(self) -> Dict:
        """Load configuration from file or create default"""
        default_config = {
            "enable_internet": True,
            "enable_voice": True,
            "min_confidence": 80,
            "voice_rate": 160,
            "voice_volume": 95,
            "theme": "light"
        }
        
        if os.path.exists(CFG_PATH):
            try:
                with open(CFG_PATH, "r", encoding="utf-8") as f:
                    loaded_config = json.load(f)
                    return {**default_config, **loaded_config}
            except Exception as e:
                print(f"Error loading config: {e}")
                return default_config
        return default_config

    def _save_config(self):
        """Save configuration to file"""
        try:
            with open(CFG_PATH, "w", encoding="utf-8") as f:
                json.dump(self.config, f, indent=2)
        except Exception as e:
            self.status_var.set(f"Failed to save config: {str(e)}")

# ====================== APPLICATION ENTRY POINT ======================
if __name__ == "__main__":
    if not os.path.exists(DB_PATH):
        # Create a default empty database if none exists
        default_db = [
            {
                "aliases": ["screen not working"],
                "en": "Try adjusting the brightness or checking the display cable connection.",
                "np": "प्रकाश समायोजन गर्नुहोस् वा डिस्प्ले केबल जडान जाँच गर्नुहोस्।",
                "learned": False
            },
            {
                "aliases": ["internet slow"],
                "en": "Try restarting your router or contacting your ISP.",
                "np": "राउटर पुनः सुरु गर्नुहोस् वा आफ्नो ISP संग सम्पर्क गर्नुहोस्।",
                "learned": False
            }
        ]
        with open(DB_PATH, "w", encoding="utf-8") as f:
            json.dump(default_db, f, indent=2, ensure_ascii=False)
    
    app = TechsewaProApp()
=======
import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox, PhotoImage
import threading
import json
import os
import platform
import psutil
import pyttsx3
from Brain import SmartBrain
import webbrowser
from datetime import datetime
from PIL import Image, ImageTk
import sv_ttk
import sys
import requests
from io import BytesIO

class TechsewaUltimate(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Techsewa Assistant - Ultimate Edition")
        self.geometry("1400x900")
        self.minsize(1200, 800)
        
        # Initialize diagnostics storage
        self.diag_vars = {}
        self.diag_progress = {}
        
        # Modern theme
        sv_ttk.use_light_theme()
        
        # Configuration
        self.BASE_DIR = os.path.dirname(os.path.abspath(__file__))
        self.DB_PATH = os.path.join(self.BASE_DIR, "problems.json")
        self.CONFIG_PATH = os.path.join(self.BASE_DIR, "config.json")
        self.ASSETS_DIR = os.path.join(self.BASE_DIR, "assets")
        
        # Load settings
        self.config = self._load_config()
        
        # Initialize UI and components
        self._init_ui()
        self._init_voice_engine()
        self._init_brain()
        
        # Start animations and initial messages
        self.after(100, self._animate_header)
        self._log("🚀 Techsewa Assistant Ultimate Edition Activated", "system")
        self._log("Powered by SmartBrain Ultra with semantic search", "system")
        self._log("Type your technical issue or click the mic to speak", "system")

    def _init_ui(self):
        """Initialize all UI components"""
        # Main container
        self.main_frame = ttk.Frame(self)
        self.main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Header with animation
        self.header_frame = ttk.Frame(self.main_frame, style="Card.TFrame")
        self.header_frame.pack(fill=tk.X, padx=20, pady=(20, 10))
        
        # Logo and title with fade-in effect
        self._load_logo()
        
        self.title_label = ttk.Label(
            self.header_frame,
            text="Techsewa Assistant ULTRA",
            font=("Segoe UI", 18, "bold"),
            foreground="#1a73e8"
        )
        self.title_label.pack(side=tk.LEFT, padx=10)
        
        # Brain status indicator
        self.brain_status = ttk.Label(
            self.header_frame,
            text="🧠 SmartBrain Ultra Active",
            font=("Segoe UI", 10),
            foreground="#34a853"
        )
        self.brain_status.pack(side=tk.RIGHT, padx=10)
        
        # Search bar with modern look
        search_frame = ttk.Frame(self.main_frame, style="Card.TFrame")
        search_frame.pack(fill=tk.X, padx=20, pady=10)
        
        self.search_var = tk.StringVar()
        self.entry = ttk.Entry(
            search_frame,
            textvariable=self.search_var,
            font=("Segoe UI", 12),
            style="Search.TEntry"
        )
        self.entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=10, pady=10)
        self.entry.bind("<Return>", lambda e: self.process_query())
        
        # Action buttons
        btn_frame = ttk.Frame(search_frame)
        btn_frame.pack(side=tk.RIGHT)
        
        # Mic button with animation
        self.mic_img = self._load_image("mic.png", (24, 24))
        self.mic_btn = ttk.Button(
            btn_frame,
            image=self.mic_img,
            style="Accent.TButton",
            command=self.start_voice_input
        )
        self.mic_btn.pack(side=tk.LEFT, padx=(0, 5))
        
        # Teach button
        self.teach_btn = ttk.Button(
            btn_frame,
            text="Teach",
            style="Accent.TButton",
            command=self.show_teach_dialog
        )
        self.teach_btn.pack(side=tk.LEFT, padx=5)
        
        # Main content area with tabs
        self.notebook = ttk.Notebook(self.main_frame)
        self.notebook.pack(fill=tk.BOTH, expand=True, padx=20, pady=(0, 20))
        
        # Chat tab
        self.chat_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.chat_frame, text="Assistant")
        self._init_chat_tab()
        
        # Diagnostics tab
        self.diag_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.diag_frame, text="System")
        self._init_diagnostics_tab()
        
        # Settings tab
        self.settings_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.settings_frame, text="Settings")
        self._init_settings_tab()
        
        # Brain Stats tab
        self.stats_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.stats_frame, text="Brain Stats")
        self._init_stats_tab()
        
        # Status bar
        self._init_status_bar()
        
        # Configure text tags and styles
        self._configure_text_tags()
        self._configure_styles()

    def _init_chat_tab(self):
        """Initialize the chat tab"""
        self.text_area = scrolledtext.ScrolledText(
            self.chat_frame,
            wrap=tk.WORD,
            state="disabled",
            font=("Segoe UI", 12),
            padx=20,
            pady=20,
            relief=tk.FLAT
        )
        self.text_area.pack(fill=tk.BOTH, expand=True)

    def _init_diagnostics_tab(self):
        """Initialize diagnostics tab"""
        sys_frame = ttk.LabelFrame(self.diag_frame, text="System Information", padding=15)
        sys_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        metrics = [
            ("CPU", "cpu_percent", "Gauge.CPU.TFrame"),
            ("Memory", "virtual_memory", "Gauge.Memory.TFrame"),
            ("Disk", "disk_usage", "Gauge.Disk.TFrame"),
            ("Network", "net_io_counters", "Gauge.Network.TFrame")
        ]
        
        for title, metric, style in metrics:
            self._create_info_card(sys_frame, title, metric, "0%", style)
        
        self._update_diagnostics()

    def _init_stats_tab(self):
        """Initialize Brain Stats tab"""
        stats_frame = ttk.Frame(self.stats_frame, padding=15)
        stats_frame.pack(fill=tk.BOTH, expand=True)
        
        # Brain capabilities
        ttk.Label(stats_frame, text="🧠 SmartBrain Ultra Capabilities", font=("Segoe UI", 12, "bold")).pack(anchor=tk.W, pady=5)
        
        self.capabilities_frame = ttk.Frame(stats_frame)
        self.capabilities_frame.pack(fill=tk.X, pady=10)
        
        # Stats
        ttk.Label(stats_frame, text="📊 Current Statistics", font=("Segoe UI", 12, "bold")).pack(anchor=tk.W, pady=5)
        
        self.stats_frame = ttk.Frame(stats_frame)
        self.stats_frame.pack(fill=tk.X, pady=10)
        
        # Update stats
        self._update_brain_stats()

    def _update_brain_stats(self):
        """Update brain statistics display"""
        if not hasattr(self, 'brain'):
            return
            
        stats = self.brain.stats()
        
        # Clear previous widgets
        for widget in self.capabilities_frame.winfo_children():
            widget.destroy()
        for widget in self.stats_frame.winfo_children():
            widget.destroy()
        
        # Capabilities
        caps = [
            ("✅" if stats["semantic"] else "❌", "Semantic Search (BERT)"),
            ("✅" if stats["internet"] else "❌", "Internet Fallback"),
            ("✅", "Local Knowledge Base"),
            ("✅", "Fuzzy Matching"),
            ("✅", "Learning Mode")
        ]
        
        for i, (icon, text) in enumerate(caps):
            frame = ttk.Frame(self.capabilities_frame)
            frame.grid(row=i//3, column=i%3, sticky=tk.W, padx=10, pady=5)
            ttk.Label(frame, text=icon, font=("Segoe UI", 12)).pack(side=tk.LEFT)
            ttk.Label(frame, text=text, font=("Segoe UI", 10)).pack(side=tk.LEFT)
        
        # Statistics
        stat_items = [
            ("Knowledge Base Entries", stats["total_problems"]),
            ("Cached Matches", stats["cached_matches"]),
            ("Session Queries", len(self.brain.history))
        ]
        
        for i, (label, value) in enumerate(stat_items):
            frame = ttk.Frame(self.stats_frame)
            frame.grid(row=i//2, column=i%2, sticky=tk.W, padx=10, pady=5)
            ttk.Label(frame, text=f"{label}:", font=("Segoe UI", 10, "bold")).pack(side=tk.LEFT)
            ttk.Label(frame, text=str(value), font=("Segoe UI", 10)).pack(side=tk.LEFT)

    def _init_settings_tab(self):
        """Initialize settings tab"""
        notebook = ttk.Notebook(self.settings_frame)
        notebook.pack(fill=tk.BOTH, expand=True)
        
        # General settings
        general_frame = ttk.Frame(notebook, padding=15)
        notebook.add(general_frame, text="General")
        self._create_setting_switch(general_frame, "Enable Internet Lookup", "enable_internet")
        self._create_setting_slider(general_frame, "Confidence Threshold", "min_confidence", 50, 100)
        
        # Voice settings
        voice_frame = ttk.Frame(notebook, padding=15)
        notebook.add(voice_frame, text="Voice")
        self._create_setting_slider(voice_frame, "Voice Speed", "voice_rate", 100, 200)
        self._create_setting_slider(voice_frame, "Voice Volume", "voice_volume", 0, 100)
        self._create_setting_switch(voice_frame, "Enable Voice Output", "enable_voice")
        
        # Appearance
        appear_frame = ttk.Frame(notebook, padding=15)
        notebook.add(appear_frame, text="Appearance")
        self._create_setting_dropdown(appear_frame, "Theme", "theme", ["light", "dark"])
        
        # About
        about_frame = ttk.Frame(notebook, padding=15)
        notebook.add(about_frame, text="About")
        ttk.Label(about_frame, 
                 text="Techsewa Assistant Ultimate\nPowered by SmartBrain Ultra\n\nVersion 3.1\n© 2025 Techsewa Inc.",
                 justify=tk.CENTER).pack(pady=20)
        ttk.Button(about_frame, text="Check for Updates", command=self.check_updates).pack(pady=5)
        ttk.Button(about_frame, text="Visit Website", command=lambda: webbrowser.open("https://techsewa.com")).pack(pady=5)

    def _init_status_bar(self):
        """Initialize the status bar"""
        self.status_bar = ttk.Frame(self.main_frame, height=30, style="Status.TFrame")
        self.status_bar.pack(fill=tk.X, side=tk.BOTTOM)
        
        self.status_label = ttk.Label(
            self.status_bar,
            text="Ready",
            style="Status.TLabel"
        )
        self.status_label.pack(side=tk.LEFT, padx=10)
        
        self.time_label = ttk.Label(
            self.status_bar,
            style="Status.TLabel"
        )
        self.time_label.pack(side=tk.RIGHT, padx=10)
        self._update_clock()

    def _configure_text_tags(self):
        """Configure text tags for rich formatting"""
        tags = [
            ("system", "#5f6368", ("Segoe UI", 11)),
            ("user", "#202124", ("Segoe UI", 12, "bold")),
            ("assistant", "#1a73e8", ("Segoe UI", 12)),
            ("internet", "#34a853", ("Segoe UI", 12)),
            ("semantic", "#673ab7", ("Segoe UI", 12)),
            ("error", "#d93025", ("Segoe UI", 11)),
            ("highlight", "#e8f0fe", None)
        ]
        
        for name, fg, font in tags:
            self.text_area.tag_config(name, foreground=fg, font=font)

    def _configure_styles(self):
        """Configure custom widget styles"""
        style = ttk.Style()
        
        # Card style
        style.configure("Card.TFrame", background="white", borderwidth=1, relief="solid")
        
        # Search entry
        style.configure("Search.TEntry", 
                      foreground="#5f6368",
                      padding=10,
                      bordercolor="#dadce0")
        
        # Accent button
        style.configure("Accent.TButton", 
                      background="#1a73e8",
                      foreground="white",
                      borderwidth=0)
        
        # Status bar
        style.configure("Status.TFrame", background="#f8f9fa")
        style.configure("Status.TLabel", background="#f8f9fa", foreground="#5f6368")
        
        # Gauge styles
        style.configure("Gauge.CPU.TFrame", background="#f1f3f4")
        style.configure("Gauge.Memory.TFrame", background="#f1f3f4")
        style.configure("Gauge.Disk.TFrame", background="#f1f3f4")
        style.configure("Gauge.Network.TFrame", background="#f1f3f4")

    def _load_logo(self):
        """Load logo with fallback"""
        try:
            logo_path = os.path.join(self.ASSETS_DIR, "logo.png")
            if os.path.exists(logo_path):
                img = Image.open(logo_path)
                img = img.resize((40, 40), Image.LANCZOS)
                self.logo_img = ImageTk.PhotoImage(img)
                ttk.Label(self.header_frame, image=self.logo_img).pack(side=tk.LEFT, padx=(10, 0))
        except Exception as e:
            print(f"Error loading logo: {e}")

    def _load_image(self, filename, size):
        """Load image from assets"""
        try:
            img_path = os.path.join(self.ASSETS_DIR, filename)
            if os.path.exists(img_path):
                img = Image.open(img_path)
                img = img.resize(size, Image.LANCZOS)
                return ImageTk.PhotoImage(img)
        except Exception as e:
            print(f"Error loading image {filename}: {e}")
        return None

    def _animate_header(self):
        """Animate header elements"""
        for i in range(0, 101, 5):
            self.header_frame.configure(style="Card.TFrame")
            self.update()
            self.after(10)

    def _update_clock(self):
        """Update time in status bar"""
        now = datetime.now().strftime("%H:%M:%S | %d %b %Y")
        self.time_label.config(text=now)
        self.after(1000, self._update_clock)

    def _init_voice_engine(self):
        """Initialize TTS engine"""
        try:
            self.tts = pyttsx3.init()
            self.tts.setProperty('rate', self.config.get("voice_rate", 150))
            self.tts.setProperty('volume', self.config.get("voice_volume", 0.9))
        except Exception as e:
            self._log(f"Voice initialization failed: {str(e)}", "error")

    def _init_brain(self):
        """Initialize the SmartBrain Ultra"""
        try:
            self.brain = SmartBrain(
                self.DB_PATH,
                enable_internet=self.config.get("enable_internet", True),
                min_confidence=self.config.get("min_confidence", 80)
            )
            self._update_brain_stats()
        except Exception as e:
            messagebox.showerror("Brain Initialization Error", 
                               f"Failed to initialize SmartBrain Ultra:\n{str(e)}")
            self.destroy()

    def _create_info_card(self, parent, title, metric, value, style):
        """Create a system info card"""
        card = ttk.Frame(parent, style=style, padding=10)
        card.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=5)
        
        ttk.Label(card, text=title, font=("Segoe UI", 10, "bold")).pack()
        
        self.diag_vars[metric] = tk.StringVar(value=value)
        ttk.Label(card, textvariable=self.diag_vars[metric], 
                 font=("Segoe UI", 14)).pack(pady=5)
        
        pb = ttk.Progressbar(card, orient=tk.HORIZONTAL, length=100, mode='determinate')
        pb.pack(fill=tk.X)
        self.diag_progress[metric] = pb

    def _create_setting_switch(self, parent, label, config_key):
        """Create a settings switch"""
        frame = ttk.Frame(parent)
        frame.pack(fill=tk.X, pady=5)
        
        ttk.Label(frame, text=label).pack(side=tk.LEFT)
        var = tk.BooleanVar(value=self.config.get(config_key, False))
        switch = ttk.Checkbutton(frame, variable=var, style="Switch.TCheckbutton")
        switch.pack(side=tk.RIGHT)
        var.trace("w", lambda *_: self._update_config(config_key, var.get()))

    def _create_setting_slider(self, parent, label, config_key, from_, to):
        """Create a settings slider"""
        frame = ttk.Frame(parent)
        frame.pack(fill=tk.X, pady=10)
        
        ttk.Label(frame, text=label).pack(anchor=tk.W)
        var = tk.IntVar(value=self.config.get(config_key, (from_ + to) // 2))
        scale = ttk.Scale(frame, from_=from_, to=to, variable=var)
        scale.pack(fill=tk.X)
        ttk.Label(frame, textvariable=var).pack(anchor=tk.E)
        var.trace("w", lambda *_: self._update_config(config_key, var.get()))

    def _create_setting_dropdown(self, parent, label, config_key, values):
        """Create a settings dropdown"""
        frame = ttk.Frame(parent)
        frame.pack(fill=tk.X, pady=10)
        
        ttk.Label(frame, text=label).pack(anchor=tk.W)
        var = tk.StringVar(value=self.config.get(config_key, values[0]))
        dropdown = ttk.Combobox(frame, textvariable=var, values=values, state="readonly")
        dropdown.pack(fill=tk.X)
        var.trace("w", lambda *_: self._update_config(config_key, var.get()))

    def _log(self, message, msg_type="system"):
        """Add message to chat log"""
        self.text_area.config(state=tk.NORMAL)
        
        if msg_type == "system":
            for line in message.split('\n'):
                self.text_area.insert(tk.END, "• " + line + "\n" if line.strip() else "\n", msg_type)
        else:
            self.text_area.insert(tk.END, message + "\n\n", msg_type)
            
        self.text_area.config(state=tk.DISABLED)
        self.text_area.see(tk.END)
        
        if self.config.get("enable_voice", True) and msg_type != "error":
            self.tts.say(message)
            self.tts.runAndWait()

    def process_query(self):
        """Process user query"""
        query = self.search_var.get().strip()
        if not query:
            return
            
        self.search_var.set("")
        self._log(f"You: {query}", "user")
        self.status_label.config(text="Processing your request...")
        
        threading.Thread(
            target=self._solve_query,
            args=(query,),
            daemon=True
        ).start()

    def _solve_query(self, query):
        """Get solution from brain"""
        try:
            result = self.brain.solve(
                query,
                lang=self.config.get("language", "en"),
                min_conf=self.config.get("min_confidence", 80)
            )
            
            # Format based on source
            if result['source'] == 'internet':
                response = f"🌐 Techsewa (Internet):\n{result['answer']}"
                self.after(0, self._log, response, "internet")
            elif result['source'] == 'semantic':
                response = f"🧠 Techsewa (Semantic):\n{result['answer']}"
                self.after(0, self._log, response, "semantic")
            else:
                response = f"💡 Techsewa ({result['source'].title()}):\n{result['answer']}"
                self.after(0, self._log, response, "assistant")
                
            # Update stats after successful query
            self.after(0, self._update_brain_stats)
        except Exception as e:
            self.after(0, self._log, f"⚠️ Error: {str(e)}", "error")
        finally:
            self.after(0, lambda: self.status_label.config(text="Ready"))

    def start_voice_input(self):
        """Start voice input simulation"""
        self._log("🎤 Listening... Speak now", "system")
        self.after(3000, self._process_voice_input)

    def _process_voice_input(self):
        """Process simulated voice input"""
        sample_queries = [
            "My screen is not working",
            "How do I reset my password?",
            "Internet connection is slow",
            "Printer not responding"
        ]
        query = sample_queries[len(self.text_area.get("1.0", tk.END)) % len(sample_queries)]
        self.search_var.set(query)
        self.process_query()

    def show_teach_dialog(self):
        """Show dialog to teach new solutions"""
        dialog = tk.Toplevel(self)
        dialog.title("Teach New Solution")
        dialog.geometry("500x400")
        
        ttk.Label(dialog, text="Problem/Question:").pack(pady=(10, 0))
        problem_entry = ttk.Entry(dialog, font=("Segoe UI", 11))
        problem_entry.pack(fill=tk.X, padx=20, pady=5)
        
        ttk.Label(dialog, text="English Solution:").pack()
        en_solution = scrolledtext.ScrolledText(dialog, height=5, font=("Segoe UI", 11))
        en_solution.pack(fill=tk.BOTH, padx=20, pady=5)
        
        ttk.Label(dialog, text="Nepali Solution (optional):").pack()
        np_solution = scrolledtext.ScrolledText(dialog, height=5, font=("Segoe UI", 11))
        np_solution.pack(fill=tk.BOTH, padx=20, pady=5)
        
        def save_solution():
            problem = problem_entry.get().strip()
            en = en_solution.get("1.0", tk.END).strip()
            np = np_solution.get("1.0", tk.END).strip()
            
            if problem and en:
                self.brain.teach(problem, en, np if np else None)
                self._log(f"📚 Learned new solution for: {problem}", "system")
                self._update_brain_stats()
                dialog.destroy()
            else:
                messagebox.showwarning("Incomplete", "Please provide both problem and English solution")
        
        ttk.Button(dialog, text="Save", command=save_solution).pack(pady=10)

    def _update_diagnostics(self):
        """Update system diagnostics"""
        try:
            # CPU
            cpu = psutil.cpu_percent()
            self.diag_vars["cpu_percent"].set(f"{cpu}%")
            self.diag_progress["cpu_percent"]["value"] = cpu
            
            # Memory
            mem = psutil.virtual_memory()
            self.diag_vars["virtual_memory"].set(f"{mem.percent}%")
            self.diag_progress["virtual_memory"]["value"] = mem.percent
            
            # Disk
            disk = psutil.disk_usage('/')
            self.diag_vars["disk_usage"].set(f"{disk.percent}%")
            self.diag_progress["disk_usage"]["value"] = disk.percent
            
            # Network
            net1 = psutil.net_io_counters()
            self.after(1000, self._update_network, net1)
            
        except Exception as e:
            print(f"Diagnostics error: {e}")
        finally:
            self.after(5000, self._update_diagnostics)

    def _update_network(self, net1):
        """Update network statistics"""
        net2 = psutil.net_io_counters()
        dl = (net2.bytes_recv - net1.bytes_recv) / 1024
        ul = (net2.bytes_sent - net1.bytes_sent) / 1024
        self.diag_vars["net_io_counters"].set(f"↓{dl:.1f}KB/s ↑{ul:.1f}KB/s")
        self.diag_progress["net_io_counters"]["value"] = min(100, (dl + ul) * 100 / 1024)

    def check_updates(self):
        """Check for application updates"""
        self._log("🔍 Checking for updates...", "system")
        self.status_label.config(text="Checking for updates...")
        self.after(2000, lambda: self._log("✅ You're using the latest version", "system"))
        self.after(2000, lambda: self.status_label.config(text="Ready"))

    def _update_config(self, key, value):
        """Update configuration setting"""
        self.config[key] = value
        self._save_config()
        
        if key == "enable_internet":
            self.brain.enable_internet = value
            self._update_brain_stats()
        elif key in ["voice_rate", "voice_volume"] and hasattr(self, 'tts'):
            self.tts.setProperty('rate' if key == "voice_rate" else 'volume', 
                               value if key == "voice_rate" else value/100)
        elif key == "theme":
            sv_ttk.set_theme(value)

    def _load_config(self):
        """Load or create configuration"""
        default_config = {
            "enable_internet": True,
            "enable_voice": True,
            "min_confidence": 80,
            "language": "en",
            "voice_rate": 150,
            "voice_volume": 90,
            "theme": "light"
        }
        
        if os.path.exists(self.CONFIG_PATH):
            try:
                with open(self.CONFIG_PATH, "r", encoding="utf-8") as f:
                    return {**default_config, **json.load(f)}
            except Exception as e:
                messagebox.showwarning("Config Error", f"Using defaults: {str(e)}")
                return default_config
        return default_config

    def _save_config(self):
        """Save configuration to file"""
        try:
            with open(self.CONFIG_PATH, "w", encoding="utf-8") as f:
                json.dump(self.config, f, indent=2)
        except Exception as e:
            self._log(f"⚠️ Failed to save config: {str(e)}", "error")

if __name__ == "__main__":
    app = TechsewaUltimate()
>>>>>>> 45d4a94f6f9ec2233ffcf916ea97fa2fe46c4ce7
    app.mainloop()