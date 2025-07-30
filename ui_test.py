# techsewa_gui.py  (Python 3.9+)
import threading, queue, time, os, psutil, darkdetect
import ttkbootstrap as tb
from ttkbootstrap.constants import *
from tkchart import LineChart, Line
from problem_detector import ProblemDetector, ProblemAlert, ProblemType
from auto_healer import EnhancedAutoHealer
import whispherblade as wb
import nepali_tts as ntts

THEME = "superhero" if darkdetect.isDark() else "flatly"

class App(tb.Window):
    def __init__(self):
        super().__init__(themename=THEME, title="TechSewa Ultimate", size=(1280, 800))
        self.style.configure("Sidebar.TButton", anchor="w", padding=10, width=18)
        # --- controller & queues ---
        self.controller = AppController(self)
        # --- layout skeleton ---
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)
        Sidebar(self).grid(row=0, column=0, sticky="ns")
        self.stack = tb.Frame(self); self.stack.grid(row=0, column=1, sticky="nsew")
        # attach pages
        self.pages = {name: cls(self.stack, self.controller) for name, cls in {
            "dashboard": DashboardPage,
            "alerts":    AlertPage,
            "healer":    HealerPage,
            "assistant": AssistantPage,
            "settings":  SettingsPage,
        }.items()}
        for i, page in self.pages.items():
            page.grid(row=0, column=0, sticky="nsew")
        self.show("dashboard")

    def show(self, page_key:str):                 # stack-like page switch
        self.pages[page_key].tkraise()

class Sidebar(tb.Frame):
    def __init__(self, parent):
        super().__init__(parent, padding=(4,4), bootstyle=PRIMARY)
        items = [
            ("🏠 Dashboard",   "dashboard"),
            ("⚠️ Health",      "alerts"),
            ("🛠 Auto Healer", "healer"),
            ("🤖 Assistant",   "assistant"),
            ("⚙️ Settings",    "settings")
        ]
        for text, key in items:
            tb.Button(self, text=text, style="Sidebar.TButton",
                      command=lambda k=key: parent.show(k)).pack(fill=X, pady=2)

# ------------------------------------------------------------------ Pages
class DashboardPage(tb.Frame):
    def __init__(self, parent, ctl):
        super().__init__(parent, padding=10)
        self.ctl = ctl
        self.meter_cpu  = tb.Meter(self, subtext="CPU", bootstyle=INFO, metertype="semi")
        self.meter_ram  = tb.Meter(self, subtext="RAM", bootstyle=WARNING, metertype="semi")
        self.meter_disk = tb.Meter(self, subtext="Disk", bootstyle=DANGER, metertype="semi")
        self.meter_cpu.grid(row=0, column=0, padx=30, pady=15)
        self.meter_ram.grid(row=0, column=1, padx=30, pady=15)
        self.meter_disk.grid(row=0, column=2, padx=30, pady=15)
        # live line chart
        self.chart = LineChart(self, x_axis_values=[str(i) for i in range(60)], y_axis_values=(0,100))
        self.line_cpu = Line(master=self.chart, color="cyan")
        self.chart.grid(row=1, column=0, columnspan=3, pady=10, sticky="ew")
        self.after(1000, self.refresh)

    def refresh(self):
        data = self.ctl.get_stats()
        self.meter_cpu.configure(amountused=data["cpu"])
        self.meter_ram.configure(amountused=data["ram"])
        self.meter_disk.configure(amountused=data["disk"])
        # shift chart left
        self.chart.show_data(line=self.line_cpu, data=[data["cpu"]])
        self.after(1000, self.refresh)

class AlertPage(tb.Frame):
    def __init__(self, parent, ctl):
        super().__init__(parent, padding=10)
        cols=("Time","Type","Severity","Message")
        self.tree = tb.Treeview(self, columns=cols, show="headings", height=18)
        for c in cols: self.tree.heading(c, text=c)
        self.tree.pack(fill=BOTH, expand=True)
        ctl.subscribe_alerts(self.add_row)

    def add_row(self, alert:ProblemAlert):
        self.tree.insert("", 0, values=(time.strftime('%H:%M:%S',time.localtime(alert.timestamp)),
                                        alert.problem_type.name, alert.severity, alert.message))

class HealerPage(tb.Frame):
    def __init__(self, parent, ctl):
        super().__init__(parent, padding=10)
        self.ctl = ctl
        tb.Button(self, text="Run Auto-Healer Now", bootstyle=SUCCESS,
                  command=self.run_healer).pack(pady=10)
        self.log = tb.ScrolledText(self, height=25, width=100, wrap="word")
        self.log.pack(fill=BOTH, expand=True)

    def run_healer(self):
        self.log.insert(END, "Running auto-healer …\n"); self.log.see(END)
        res = self.ctl.heal_now()
        for act in res.actions_taken:
            self.log.insert(END, f"✓ {act}\n")
        self.log.insert(END, f"-- {res.message}\n\n"); self.log.see(END)

class AssistantPage(tb.Frame):
    def __init__(self, parent, ctl):
        super().__init__(parent, padding=10)
        self.ctl=ctl
        self.chat = tb.ScrolledText(self, height=20, width=120, state="disabled")
        self.chat.pack(fill=BOTH, expand=True, pady=5)
        bottom = tb.Frame(self); bottom.pack(fill=X)
        self.query = tb.Entry(bottom); self.query.pack(side=LEFT, fill=X, expand=True, padx=5)
        tb.Button(bottom, text="Ask", bootstyle=PRIMARY, command=self.ask).pack(side=LEFT)

    def ask(self):
        q = self.query.get().strip(); self.query.delete(0, END)
        if not q: return
        self._write("you", q)
        self._write("assistant", "…thinking…")
        self.after_idle(lambda: self._answer(q))

    def _answer(self, q):
        ans = self.ctl.ask_ai(q)
        self.chat.delete("end-3l", "end-1l")
        self._write("assistant", ans)

    def _write(self, who, txt):
        self.chat.configure(state="normal")
        self.chat.insert(END, f"{who}: {txt}\n"); self.chat.configure(state="disabled")
        self.chat.see(END)

class SettingsPage(tb.Frame):
    def __init__(self, parent, ctl):
        super().__init__(parent, padding=10)
        tb.Label(self, text="TechSewa Ultimate v2", font=("Segoe UI", 20)).pack(pady=15)
        tb.Button(self, text="Toggle Theme", command=self.toggle).pack(pady=10)
        tb.Label(self, text="Developer: Ayush Ojha  • github.com/flawnlawyer").pack()
        self.ctrl=ctl
    def toggle(self):
        cur = self.master.master.style.theme.name
        self.master.master.style.theme_use("flatly" if cur=="superhero" else "superhero")

# ------------------------------------------------------------------ Controller & background threads
class AppController:
    def __init__(self, guiroot):
        self.guiroot = guiroot
        self.alert_handlers=[]              # callbacks
        # whisperblade + system services
        self.wb = wb.WhisperBladeUltimate()
        self.detector = ProblemDetector(self._alert_cb, check_interval=5); self.detector.start()
        self.healer = EnhancedAutoHealer(); self.healer.start_monitoring()
    # data feeders --------------------------------------------------
    def get_stats(self):
        return {"cpu":psutil.cpu_percent(),
                "ram":psutil.virtual_memory().percent,
                "disk":psutil.disk_usage("/").percent}
    def subscribe_alerts(self, fn): self.alert_handlers.append(fn)
    def _alert_cb(self, alert):      # called from ProblemDetector thread
        self.guiroot.after(0, lambda: [h(alert) for h in self.alert_handlers])
    def heal_now(self): return self.healer.heal(problem_type=wb.ProblemType.CPU)  # sample healer call
    def ask_ai(self, q:str):
        res = self.wb.process_sync({"query":q, "lang":"en"})
        threading.Thread(target=ntts.speak, args=(res["answer"],), daemon=True).start()
        return res["answer"]

# ------------------------------------------------------------------
if __name__ == "__main__":
    App().mainloop()
