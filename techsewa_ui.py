import sys
import time
from typing import Dict, List

import psutil  # type: ignore
from PyQt5.QtCore import (
    QEasingCurve,
    QPropertyAnimation,
    QTimer,
    Qt,
)
from PyQt5.QtGui import QFont, QIcon, QPixmap
from PyQt5.QtWidgets import (
    QApplication,
    QCheckBox,
    QComboBox,
    QFrame,
    QGraphicsOpacityEffect,
    QGridLayout,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QListWidget,
    QListWidgetItem,
    QMainWindow,
    QMessageBox,
    QPushButton,
    QSpacerItem,
    QStackedWidget,
    QTableWidget,
    QTableWidgetItem,
    QTextEdit,
    QVBoxLayout,
    QWidget,
)
from matplotlib.backends.backend_qt5agg import (
    FigureCanvasQTAgg as FigureCanvas,
)
from matplotlib.figure import Figure

# Optional TTS – installed locally; fallback to dummy if unavailable
try:
    import pyttsx3  # type: ignore

    _TTS_AVAILABLE = True
except ImportError:
    _TTS_AVAILABLE = False

__version__ = "0.1.0"
__author__ = "Ayush Ojha (@flawnlawyer)"

# -----------------------------------------------------------------------------
# Theme helpers
# -----------------------------------------------------------------------------

LIGHT_STYLE_SHEET = """
* { font-family: 'Segoe UI', sans-serif; }
QMainWindow { background: #f5f5f5; }
QLineEdit, QTextEdit, QComboBox, QTableWidget {
    background: #ffffff;
    border: 1px solid #cccccc;
    border-radius: 6px;
    padding: 4px;
}
QPushButton {
    background: #2d89ef;
    color: white;
    border-radius: 6px;
    padding: 6px 12px;
}
QPushButton:hover { background: #1e64b7; }
QListWidget { background: #e8e8e8; border: none; }
QListWidget::item:selected { background: #2d89ef; color: white; }
"""

DARK_STYLE_SHEET = """
* { font-family: 'Segoe UI', sans-serif; }
QMainWindow { background: #121212; color: #e0e0e0; }
QLineEdit, QTextEdit, QComboBox, QTableWidget {
    background: #1e1e1e;
    color: #e0e0e0;
    border: 1px solid #333333;
    border-radius: 6px;
    padding: 4px;
}
QPushButton {
    background: #bb86fc;
    color: #000000;
    border-radius: 6px;
    padding: 6px 12px;
}
QPushButton:hover { background: #985eff; }
QListWidget { background: #1e1e1e; border: none; }
QListWidget::item:selected { background: #bb86fc; color: #000000; }
"""


def apply_theme(app: QApplication, dark: bool = False) -> None:
    """Apply the global light or dark QSS theme."""

    if dark:
        app.setStyleSheet(DARK_STYLE_SHEET)
    else:
        app.setStyleSheet(LIGHT_STYLE_SHEET)


# -----------------------------------------------------------------------------
# Utility widgets
# -----------------------------------------------------------------------------


class FadeStackedWidget(QStackedWidget):
    """A QStackedWidget with a fade transition on page change."""

    def __init__(self) -> None:
        super().__init__()
        self._fade_duration_ms = 250
        self._current_effect: QGraphicsOpacityEffect | None = None
        self._anim: QPropertyAnimation | None = None

    def setCurrentIndex(self, index: int) -> None:  # type: ignore[override]
        if index == self.currentIndex():
            return

        current_widget = self.currentWidget()
        if current_widget is not None:
            self._current_effect = QGraphicsOpacityEffect(current_widget)
            current_widget.setGraphicsEffect(self._current_effect)
            self._anim = QPropertyAnimation(self._current_effect, b"opacity")
            self._anim.setDuration(self._fade_duration_ms)
            self._anim.setStartValue(1.0)
            self._anim.setEndValue(0.0)
            self._anim.setEasingCurve(QEasingCurve.InOutQuad)
            self._anim.start()
            # When finished, actually change page and fade in new page
            self._anim.finished.connect(lambda: self._fade_in(index))
        else:
            super().setCurrentIndex(index)

    def _fade_in(self, index: int) -> None:
        super().setCurrentIndex(index)
        new_widget = self.currentWidget()
        if new_widget is None:
            return
        effect = QGraphicsOpacityEffect(new_widget)
        new_widget.setGraphicsEffect(effect)
        anim = QPropertyAnimation(effect, b"opacity")
        anim.setDuration(self._fade_duration_ms)
        anim.setStartValue(0.0)
        anim.setEndValue(1.0)
        anim.setEasingCurve(QEasingCurve.InOutQuad)
        anim.start()
        # Keep reference to prevent garbage collection
        self._current_effect = effect
        self._anim = anim


class CardWidget(QWidget):
    """A simple card displaying a metric and a matplotlib live mini-graph."""

    def __init__(self, title: str, unit: str = "%") -> None:
        super().__init__()
        self._title = title
        self._unit = unit
        self._values: List[float] = []
        self._max_points = 60
        self._init_ui()
        self._timer = QTimer(self)
        self._timer.timeout.connect(self._update)
        self._timer.start(1000)

    def _init_ui(self) -> None:
        layout = QVBoxLayout(self)
        self.title_label = QLabel(self._title)
        font = QFont()
        font.setPointSize(10)
        font.setBold(True)
        self.title_label.setFont(font)
        layout.addWidget(self.title_label, alignment=Qt.AlignHCenter)

        self.value_label = QLabel("0%")
        vfont = QFont()
        vfont.setPointSize(14)
        vfont.setBold(True)
        self.value_label.setFont(vfont)
        layout.addWidget(self.value_label, alignment=Qt.AlignHCenter)

        # matplotlib figure
        fig = Figure(figsize=(2, 1.2), dpi=100)
        self.ax = fig.add_subplot(111)
        self.ax.set_facecolor("none")
        self.ax.tick_params(labelsize=6)
        self.ax.set_ylim(0, 100)
        self.canvas = FigureCanvas(fig)
        layout.addWidget(self.canvas)

        self.setLayout(layout)
        self.setFrameStyle(QFrame.Panel | QFrame.Raised)
        self.setLineWidth(1)

    def _fetch_value(self) -> float:  # noqa: D401 – simple fetch
        match self._title.lower():
            case "cpu":
                return psutil.cpu_percent()
            case "ram":
                return psutil.virtual_memory().percent
            case "disk":
                return psutil.disk_usage("/").percent
            case "gpu":
                # Dummy GPU util (not cross-platform). Could integrate GPUtil.
                return 0.0
            case "battery":
                bat = psutil.sensors_battery()
                return bat.percent if bat else 0.0
            case _:
                return 0.0

    def _update(self) -> None:
        value = self._fetch_value()
        self._values.append(value)
        self._values = self._values[-self._max_points :]
        self.value_label.setText(f"{value:.0f}{self._unit}")
        self._draw_graph()

    def _draw_graph(self) -> None:
        self.ax.clear()
        self.ax.plot(self._values, color="#2d89ef")
        self.ax.set_ylim(0, 100)
        self.canvas.draw_idle()


# -----------------------------------------------------------------------------
# Pages implementation
# -----------------------------------------------------------------------------


class DashboardPage(QWidget):
    def __init__(self) -> None:
        super().__init__()
        layout = QGridLayout(self)
        metrics = ["CPU", "RAM", "Disk", "GPU", "Battery"]
        for idx, m in enumerate(metrics):
            card = CardWidget(m)
            row, col = divmod(idx, 3)
            layout.addWidget(card, row, col)
        layout.setSpacing(12)
        self.setLayout(layout)


class AntivirusPage(QWidget):
    def __init__(self) -> None:
        super().__init__()
        vbox = QVBoxLayout(self)
        title = QLabel("Antivirus Scanner")
        title.setFont(QFont("", 14, QFont.Bold))
        vbox.addWidget(title)

        btn_quick = QPushButton("Quick Scan")
        btn_full = QPushButton("Full Scan")
        vbox.addWidget(btn_quick)
        vbox.addWidget(btn_full)

        self.last_scan_label = QLabel("Last scan: Never")
        vbox.addWidget(self.last_scan_label)

        btn_quick.clicked.connect(lambda: self._start_scan("quick"))
        btn_full.clicked.connect(lambda: self._start_scan("full"))

        # Quarantine
        qtitle = QLabel("Quarantine")
        qtitle.setFont(QFont("", 12, QFont.Bold))
        vbox.addWidget(qtitle)
        self.quarantine_list = QListWidget()
        vbox.addWidget(self.quarantine_list)

        vbox.addStretch(1)

    def _start_scan(self, mode: str) -> None:
        # Dummy scan logic with delay
        QMessageBox.information(self, "Scan", f"{mode.title()} scan started.")
        QApplication.processEvents()
        time.sleep(1)  # Simulated delay
        self.last_scan_label.setText(f"Last scan: {time.strftime('%Y-%m-%d %H:%M:%S')}")
        QMessageBox.information(self, "Scan", "No threats found. System is clean!")


class FirewallPage(QWidget):
    def __init__(self) -> None:
        super().__init__()
        vbox = QVBoxLayout(self)
        title = QLabel("Firewall Frenzy")
        title.setFont(QFont("", 14, QFont.Bold))
        vbox.addWidget(title)

        self.table = QTableWidget(0, 3)
        self.table.setHorizontalHeaderLabels(["Process", "Local Port", "Status"])
        vbox.addWidget(self.table)

        self.refresh()
        timer = QTimer(self)
        timer.timeout.connect(self.refresh)
        timer.start(3000)

    def refresh(self) -> None:
        # Very rough process listing (dummy)
        self.table.setRowCount(0)
        for proc in psutil.process_iter(['name', 'pid']):
            row = self.table.rowCount()
            self.table.insertRow(row)
            self.table.setItem(row, 0, QTableWidgetItem(proc.info['name'] or "?"))
            self.table.setItem(row, 1, QTableWidgetItem(str(proc.pid)))
            chk = QCheckBox()
            chk.setChecked(True)
            self.table.setCellWidget(row, 2, chk)


class TTSToolPage(QWidget):
    def __init__(self) -> None:
        super().__init__()
        vbox = QVBoxLayout(self)
        title = QLabel("Text-to-Speech Tool")
        title.setFont(QFont("", 14, QFont.Bold))
        vbox.addWidget(title)

        self.text_input = QTextEdit()
        vbox.addWidget(self.text_input)

        hbox = QHBoxLayout()
        self.lang_combo = QComboBox()
        self.lang_combo.addItems(["English", "Nepali"])
        hbox.addWidget(self.lang_combo)

        self.btn_play = QPushButton("Play")
        self.btn_play.clicked.connect(self._play)
        hbox.addWidget(self.btn_play)

        self.btn_save = QPushButton("Save Audio")
        self.btn_save.clicked.connect(self._save_audio)
        hbox.addWidget(self.btn_save)
        vbox.addLayout(hbox)

        vbox.addStretch(1)

    def _play(self) -> None:
        text = self.text_input.toPlainText().strip()
        if not text:
            return
        if _TTS_AVAILABLE:
            engine = pyttsx3.init()
            engine.setProperty('voice', self._get_voice_id())
            engine.say(text)
            engine.runAndWait()
        else:
            QMessageBox.information(self, "TTS", "pyttsx3 not installed. Unable to play audio.")

    def _save_audio(self) -> None:
        if not _TTS_AVAILABLE:
            QMessageBox.information(self, "TTS", "pyttsx3 not installed. Unable to save audio.")
            return
        text = self.text_input.toPlainText().strip()
        if not text:
            return
        path, _ = QFileDialog.getSaveFileName(self, "Save Audio", "tts.wav", "Wave Files (*.wav)")
        if path:
            engine = pyttsx3.init()
            engine.save_to_file(text, path)
            engine.runAndWait()
            QMessageBox.information(self, "TTS", f"Saved to {path}")

    def _get_voice_id(self) -> str | None:
        # Simple English/Nepali voice selection
        language = self.lang_combo.currentText()
        engine = pyttsx3.init()
        for voice in engine.getProperty('voices'):
            if language == "English" and "en" in voice.languages[0].decode():
                return voice.id
            if language == "Nepali" and ("hi" in voice.languages[0].decode() or "ne" in voice.languages[0].decode()):
                return voice.id
        return None


class ChatMessage(QWidget):
    def __init__(self, text: str, is_user: bool = False) -> None:
        super().__init__()
        layout = QHBoxLayout(self)
        label = QLabel(text)
        label.setWordWrap(True)
        label.setStyleSheet("background: #2d89ef; color: white; padding: 6px; border-radius: 6px;" if is_user else
                             "background: #e0e0e0; padding: 6px; border-radius: 6px;")
        if is_user:
            layout.addStretch(1)
            layout.addWidget(label)
        else:
            layout.addWidget(label)
            layout.addStretch(1)


class AIAssistantPage(QWidget):
    def __init__(self) -> None:
        super().__init__()
        vbox = QVBoxLayout(self)
        title = QLabel("AI Assistant")
        title.setFont(QFont("", 14, QFont.Bold))
        vbox.addWidget(title)

        # Scroll area or simple container for messages
        self.chat_area = QVBoxLayout()
        self.chat_area.addStretch(1)
        vbox.addLayout(self.chat_area)

        hbox = QHBoxLayout()
        self.input_line = QLineEdit()
        self.input_line.setPlaceholderText("Ask me anything ...")
        hbox.addWidget(self.input_line)
        send_btn = QPushButton("Send")
        send_btn.clicked.connect(self._send)
        hbox.addWidget(send_btn)
        vbox.addLayout(hbox)

        vbox.addStretch(1)

    def _send(self) -> None:
        text = self.input_line.text().strip()
        if not text:
            return
        # Append user message
        self._append_message(text, is_user=True)
        self.input_line.clear()
        # Dummy response
        response = f"[Stub] You asked: '{text}'. This feature is under construction."
        QTimer.singleShot(500, lambda: self._append_message(response, is_user=False))

    def _append_message(self, text: str, is_user: bool = False) -> None:
        msg = ChatMessage(text, is_user)
        self.chat_area.insertWidget(self.chat_area.count() - 1, msg)


class SettingsPage(QWidget):
    def __init__(self, main_app: 'TechSewaApp') -> None:  # noqa: F821 – forward ref
        super().__init__()
        self.main_app = main_app
        vbox = QVBoxLayout(self)
        title = QLabel("Settings")
        title.setFont(QFont("", 14, QFont.Bold))
        vbox.addWidget(title)

        self.theme_checkbox = QCheckBox("Dark Theme")
        self.theme_checkbox.setChecked(False)
        self.theme_checkbox.stateChanged.connect(self._toggle_theme)
        vbox.addWidget(self.theme_checkbox)

        lang_label = QLabel("Language")
        vbox.addWidget(lang_label)
        self.lang_combo = QComboBox()
        self.lang_combo.addItems(["English", "Nepali"])
        vbox.addWidget(self.lang_combo)

        update_btn = QPushButton("Check for Updates")
        update_btn.clicked.connect(lambda: QMessageBox.information(self, "Updates", "You are up to date!"))
        vbox.addWidget(update_btn)

        vbox.addStretch(1)

    def _toggle_theme(self, state: int) -> None:
        dark = state == Qt.Checked
        apply_theme(QApplication.instance(), dark)


class AboutPage(QWidget):
    def __init__(self) -> None:
        super().__init__()
        vbox = QVBoxLayout(self)
        title = QLabel("About TechSewa")
        title.setFont(QFont("", 14, QFont.Bold))
        vbox.addWidget(title)

        lbl = QLabel(
            f"Version: {__version__}\nDeveloper: Ayush Ojha\nGitHub: flawnlawyer\nFor feedback: ojhaayush497@gmail.com"
        )
        lbl.setAlignment(Qt.AlignTop)
        vbox.addWidget(lbl)
        vbox.addStretch(1)


# -----------------------------------------------------------------------------
# Main application window
# -----------------------------------------------------------------------------


class TechSewaApp(QMainWindow):
    """Main Window class for TechSewa."""

    def __init__(self) -> None:
        super().__init__()
        self.setWindowTitle("TechSewa")
        self.setWindowIcon(QIcon())
        self.resize(1280, 720)
        self._init_ui()

    # ------------------------- UI Building Helpers ------------------------ #

    def _init_ui(self) -> None:
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        root_layout = QGridLayout(central_widget)
        root_layout.setContentsMargins(0, 0, 0, 0)
        root_layout.setSpacing(0)

        # Sidebar
        self.sidebar = QListWidget()
        self.sidebar.setFixedWidth(160)
        self.sidebar.setSpacing(8)
        self.sidebar.setUniformItemSizes(True)
        self.sidebar.itemClicked.connect(self._sidebar_clicked)
        root_layout.addWidget(self.sidebar, 0, 0, 2, 1)

        # Populate sidebar
        modules = [
            ("Home / Dashboard", "🏠"),
            ("Antivirus", "🛡️"),
            ("Firewall Frenzy", "🔥"),
            ("TTS Tool", "🔊"),
            ("AI Assistant", "🤖"),
            ("Settings", "⚙️"),
            ("About", "ℹ️"),
        ]
        for name, icon in modules:
            item = QListWidgetItem(f"{icon}  {name}")
            item.setData(Qt.UserRole, name)
            self.sidebar.addItem(item)

        # Top Navbar
        top_bar = QWidget()
        top_layout = QHBoxLayout(top_bar)
        top_layout.setContentsMargins(12, 6, 12, 6)
        app_name_lbl = QLabel("TechSewa")
        app_name_lbl.setFont(QFont("", 16, QFont.Bold))
        top_layout.addWidget(app_name_lbl)

        self.search_bar = QLineEdit()
        self.search_bar.setPlaceholderText("Find your issue...")
        self.search_bar.setMaximumWidth(300)
        top_layout.addWidget(self.search_bar)

        top_layout.addStretch(1)

        # Theme switch (simple checkbox)
        self.theme_toggle = QCheckBox("Dark")
        self.theme_toggle.stateChanged.connect(lambda st: apply_theme(QApplication.instance(), st == Qt.Checked))
        top_layout.addWidget(self.theme_toggle)

        # Language toggle
        self.lang_toggle = QComboBox()
        self.lang_toggle.addItems(["English", "Nepali"])
        top_layout.addWidget(self.lang_toggle)

        # Profile button
        profile_btn = QPushButton()
        profile_btn.setIcon(QIcon())
        profile_btn.setText("User")
        top_layout.addWidget(profile_btn)

        root_layout.addWidget(top_bar, 0, 1, 1, 1)

        # Stacked pages
        self.pages = FadeStackedWidget()
        self._dashboard_page = DashboardPage()
        self._antivirus_page = AntivirusPage()
        self._firewall_page = FirewallPage()
        self._tts_page = TTSToolPage()
        self._ai_page = AIAssistantPage()
        self._settings_page = SettingsPage(self)
        self._about_page = AboutPage()

        for page in [
            self._dashboard_page,
            self._antivirus_page,
            self._firewall_page,
            self._tts_page,
            self._ai_page,
            self._settings_page,
            self._about_page,
        ]:
            self.pages.addWidget(page)

        root_layout.addWidget(self.pages, 1, 1, 1, 1)

        # Default selection
        self.sidebar.setCurrentRow(0)
        self.pages.setCurrentIndex(0)

    # ------------------------- Event Handlers ---------------------------- #

    def _sidebar_clicked(self, item: QListWidgetItem) -> None:
        mapping: Dict[str, int] = {
            "Home / Dashboard": 0,
            "Antivirus": 1,
            "Firewall Frenzy": 2,
            "TTS Tool": 3,
            "AI Assistant": 4,
            "Settings": 5,
            "About": 6,
        }
        name = item.data(Qt.UserRole)
        self.pages.setCurrentIndex(mapping.get(name, 0))


# -----------------------------------------------------------------------------
# Entrypoint
# -----------------------------------------------------------------------------

def main() -> None:
    app = QApplication(sys.argv)
    apply_theme(app, dark=False)
    win = TechSewaApp()
    win.show()
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()