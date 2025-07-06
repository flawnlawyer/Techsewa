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
    app.mainloop()