#!/usr/bin/env python3
"""
TechSewa - A Multifunctional System Utility, Cybersecurity, and AI Assistant
Author: Ayush Ojha
GitHub: flawnlawyer
Email: ojhaayush497@gmail.com

A powerful desktop application with elegant UI for everyday users with power-user features.
"""

import sys
import os
import json
import datetime
import psutil
import webbrowser
from typing import Dict, List, Optional, Any
from dataclasses import dataclass
from pathlib import Path

from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QStackedWidget, QPushButton, QLabel, QLineEdit, QTextEdit,
    QProgressBar, QFrame, QScrollArea, QGridLayout, QSlider,
    QComboBox, QCheckBox, QGroupBox, QListWidget, QListWidgetItem,
    QSplitter, QTabWidget, QTableWidget, QTableWidgetItem,
    QMessageBox, QFileDialog, QSystemTrayIcon, QMenu, QAction,
    QGraphicsDropShadowEffect, QSpacerItem, QSizePolicy
)
from PyQt5.QtCore import (
    Qt, QTimer, QThread, pyqtSignal, QPropertyAnimation,
    QEasingCurve, QRect, QSize, QUrl, QSettings
)
from PyQt5.QtGui import (
    QFont, QPixmap, QPalette, QColor, QIcon, QPainter,
    QBrush, QLinearGradient, QPen, QDesktopServices
)

# Application Constants
APP_NAME = "TechSewa"
APP_VERSION = "1.0.0"
DEVELOPER_NAME = "Ayush Ojha"
DEVELOPER_GITHUB = "flawnlawyer"
DEVELOPER_EMAIL = "ojhaayush497@gmail.com"

@dataclass
class SystemStats:
    """Data class for system statistics"""
    cpu_percent: float
    memory_percent: float
    disk_percent: float
    gpu_percent: float = 0.0
    battery_percent: float = 0.0
    temperature: float = 0.0

class ModernButton(QPushButton):
    """Custom button with modern styling and hover effects"""
    
    def __init__(self, text: str = "", icon_text: str = "📱", parent=None):
        super().__init__(parent)
        self.setText(text)
        self.icon_text = icon_text
        self.setMinimumHeight(60)
        self.setFont(QFont("Segoe UI", 11))
        self.setCursor(Qt.PointingHandCursor)
        
        # Shadow effect
        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(15)
        shadow.setColor(QColor(0, 0, 0, 50))
        shadow.setOffset(0, 2)
        self.setGraphicsEffect(shadow)

class AnimatedStackedWidget(QStackedWidget):
    """Stacked widget with smooth transition animations"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.animation = QPropertyAnimation(self, b"geometry")
        self.animation.setDuration(300)
        self.animation.setEasingCurve(QEasingCurve.OutCubic)

    def slideToWidget(self, widget_index: int):
        """Animate transition to specified widget"""
        if self.currentIndex() != widget_index:
            self.setCurrentIndex(widget_index)

class SystemMonitor(QThread):
    """Background thread for monitoring system stats"""
    
    stats_updated = pyqtSignal(SystemStats)
    
    def __init__(self):
        super().__init__()
        self.running = True
        
    def run(self):
        """Main monitoring loop"""
        while self.running:
            try:
                # Get system statistics
                cpu = psutil.cpu_percent(interval=1)
                memory = psutil.virtual_memory().percent
                disk = psutil.disk_usage('/').percent
                
                # Battery info (if available)
                battery = 0.0
                try:
                    battery_info = psutil.sensors_battery()
                    if battery_info:
                        battery = battery_info.percent
                except:
                    pass
                
                # GPU info (basic implementation)
                gpu = 0.0  # Would need GPU-specific library for real data
                
                stats = SystemStats(
                    cpu_percent=cpu,
                    memory_percent=memory,
                    disk_percent=disk,
                    gpu_percent=gpu,
                    battery_percent=battery
                )
                
                self.stats_updated.emit(stats)
                self.msleep(2000)  # Update every 2 seconds
                
            except Exception as e:
                print(f"System monitoring error: {e}")
                self.msleep(5000)
    
    def stop(self):
        """Stop monitoring"""
        self.running = False
        self.quit()
        self.wait()

class StatCard(QFrame):
    """Modern stat card widget"""
    
    def __init__(self, title: str, icon: str, color: str = "#3498db"):
        super().__init__()
        self.title = title
        self.icon = icon
        self.color = color
        self.value = 0.0
        self.setup_ui()
        
    def setup_ui(self):
        """Setup the stat card UI"""
        self.setFixedSize(200, 120)
        self.setFrameStyle(QFrame.StyledPanel)
        
        layout = QVBoxLayout(self)
        layout.setSpacing(5)
        layout.setContentsMargins(15, 10, 15, 10)
        
        # Header with icon and title
        header_layout = QHBoxLayout()
        
        icon_label = QLabel(self.icon)
        icon_label.setFont(QFont("Segoe UI Emoji", 16))
        icon_label.setAlignment(Qt.AlignCenter)
        icon_label.setFixedSize(30, 30)
        
        title_label = QLabel(self.title)
        title_label.setFont(QFont("Segoe UI", 10, QFont.Bold))
        title_label.setStyleSheet(f"color: {self.color};")
        
        header_layout.addWidget(icon_label)
        header_layout.addWidget(title_label)
        header_layout.addStretch()
        
        # Value display
        self.value_label = QLabel("0%")
        self.value_label.setFont(QFont("Segoe UI", 18, QFont.Bold))
        self.value_label.setAlignment(Qt.AlignCenter)
        
        # Progress bar
        self.progress_bar = QProgressBar()
        self.progress_bar.setFixedHeight(8)
        self.progress_bar.setTextVisible(False)
        self.progress_bar.setStyleSheet(f"""
            QProgressBar {{
                border: none;
                border-radius: 4px;
                background-color: #ecf0f1;
            }}
            QProgressBar::chunk {{
                border-radius: 4px;
                background-color: {self.color};
            }}
        """)
        
        layout.addLayout(header_layout)
        layout.addWidget(self.value_label)
        layout.addWidget(self.progress_bar)
        
    def update_value(self, value: float):
        """Update the displayed value"""
        self.value = value
        self.value_label.setText(f"{value:.1f}%")
        self.progress_bar.setValue(int(value))

class TechSewaMainWindow(QMainWindow):
    """Main application window"""
    
    def __init__(self):
        super().__init__()
        self.settings = QSettings("TechSewa", "TechSewa")
        self.current_theme = self.settings.value("theme", "light")
        self.current_language = self.settings.value("language", "English")
        
        self.setup_ui()
        self.setup_system_monitor()
        self.apply_theme()
        
    def setup_ui(self):
        """Initialize the main UI"""
        self.setWindowTitle(f"{APP_NAME} - Your Digital Assistant")
        self.setMinimumSize(1200, 800)
        self.resize(1400, 900)
        
        # Center the window
        self.center_window()
        
        # Create central widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # Main layout
        main_layout = QHBoxLayout(central_widget)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        
        # Create sidebar
        self.create_sidebar()
        
        # Create main content area
        self.create_main_content()
        
        # Add to main layout
        main_layout.addWidget(self.sidebar_frame)
        main_layout.addWidget(self.main_content_widget, 1)
        
    def center_window(self):
        """Center the window on screen"""
        screen = QApplication.primaryScreen().geometry()
        size = self.geometry()
        x = (screen.width() - size.width()) // 2
        y = (screen.height() - size.height()) // 2
        self.move(x, y)
        
    def create_sidebar(self):
        """Create the animated sidebar"""
        self.sidebar_frame = QFrame()
        self.sidebar_frame.setFixedWidth(250)
        self.sidebar_frame.setFrameStyle(QFrame.StyledPanel)
        
        sidebar_layout = QVBoxLayout(self.sidebar_frame)
        sidebar_layout.setContentsMargins(10, 20, 10, 20)
        sidebar_layout.setSpacing(10)
        
        # Logo/App name
        logo_label = QLabel(APP_NAME)
        logo_label.setFont(QFont("Segoe UI", 20, QFont.Bold))
        logo_label.setAlignment(Qt.AlignCenter)
        logo_label.setStyleSheet("color: #2c3e50; padding: 20px;")
        sidebar_layout.addWidget(logo_label)
        
        # Navigation buttons
        self.nav_buttons = []
        nav_items = [
            ("🏠", "Dashboard", 0),
            ("🛡️", "Antivirus", 1),
            ("🔥", "Firewall", 2),
            ("🗣️", "TTS Tool", 3),
            ("🤖", "AI Assistant", 4),
            ("⚙️", "Settings", 5),
            ("ℹ️", "About", 6)
        ]
        
        for icon, text, index in nav_items:
            btn = ModernButton(f"  {text}", icon)
            btn.setObjectName(f"nav_btn_{index}")
            btn.clicked.connect(lambda checked, idx=index: self.switch_module(idx))
            self.nav_buttons.append(btn)
            sidebar_layout.addWidget(btn)
            
        sidebar_layout.addStretch()
        
    def create_main_content(self):
        """Create the main content area with top navbar"""
        self.main_content_widget = QWidget()
        content_layout = QVBoxLayout(self.main_content_widget)
        content_layout.setContentsMargins(0, 0, 0, 0)
        content_layout.setSpacing(0)
        
        # Top navbar
        self.create_top_navbar()
        content_layout.addWidget(self.top_navbar)
        
        # Stacked widget for different modules
        self.stacked_widget = AnimatedStackedWidget()
        content_layout.addWidget(self.stacked_widget, 1)
        
        # Create all module widgets
        self.create_modules()
        
    def create_top_navbar(self):
        """Create the top navigation bar"""
        self.top_navbar = QFrame()
        self.top_navbar.setFixedHeight(70)
        self.top_navbar.setFrameStyle(QFrame.StyledPanel)
        
        navbar_layout = QHBoxLayout(self.top_navbar)
        navbar_layout.setContentsMargins(20, 10, 20, 10)
        
        # Search bar
        search_frame = QFrame()
        search_layout = QHBoxLayout(search_frame)
        search_layout.setContentsMargins(0, 0, 0, 0)
        
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("🔍 Find your issue...")
        self.search_input.setFixedHeight(40)
        self.search_input.setFont(QFont("Segoe UI", 11))
        
        search_layout.addWidget(self.search_input)
        
        # Controls
        controls_layout = QHBoxLayout()
        
        # Language toggle
        self.language_combo = QComboBox()
        self.language_combo.addItems(["English", "नेपाली"])
        self.language_combo.setCurrentText(self.current_language)
        self.language_combo.currentTextChanged.connect(self.change_language)
        
        # Theme toggle
        self.theme_btn = QPushButton("🌙" if self.current_theme == "light" else "☀️")
        self.theme_btn.clicked.connect(self.toggle_theme)
        self.theme_btn.setFixedSize(40, 40)
        
        # Profile button
        profile_btn = QPushButton("👤")
        profile_btn.setFixedSize(40, 40)
        profile_btn.clicked.connect(self.show_profile)
        
        controls_layout.addWidget(self.language_combo)
        controls_layout.addWidget(self.theme_btn)
        controls_layout.addWidget(profile_btn)
        
        navbar_layout.addWidget(search_frame, 1)
        navbar_layout.addLayout(controls_layout)
        
    def create_modules(self):
        """Create all application modules"""
        # Dashboard
        self.dashboard_widget = self.create_dashboard()
        self.stacked_widget.addWidget(self.dashboard_widget)
        
        # Antivirus
        self.antivirus_widget = self.create_antivirus()
        self.stacked_widget.addWidget(self.antivirus_widget)
        
        # Firewall
        self.firewall_widget = self.create_firewall()
        self.stacked_widget.addWidget(self.firewall_widget)
        
        # TTS Tool
        self.tts_widget = self.create_tts_tool()
        self.stacked_widget.addWidget(self.tts_widget)
        
        # AI Assistant
        self.ai_widget = self.create_ai_assistant()
        self.stacked_widget.addWidget(self.ai_widget)
        
        # Settings
        self.settings_widget = self.create_settings()
        self.stacked_widget.addWidget(self.settings_widget)
        
        # About
        self.about_widget = self.create_about()
        self.stacked_widget.addWidget(self.about_widget)
        
    def create_dashboard(self) -> QWidget:
        """Create the dashboard module"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setContentsMargins(30, 30, 30, 30)
        layout.setSpacing(20)
        
        # Title
        title = QLabel("System Dashboard")
        title.setFont(QFont("Segoe UI", 24, QFont.Bold))
        title.setStyleSheet("color: #2c3e50; margin-bottom: 20px;")
        layout.addWidget(title)
        
        # Stat cards container
        stats_frame = QFrame()
        stats_layout = QGridLayout(stats_frame)
        stats_layout.setSpacing(20)
        
        # Create stat cards
        self.cpu_card = StatCard("CPU Usage", "🖥️", "#e74c3c")
        self.memory_card = StatCard("Memory", "💾", "#f39c12")
        self.disk_card = StatCard("Disk Space", "💿", "#27ae60")
        self.battery_card = StatCard("Battery", "🔋", "#9b59b6")
        
        stats_layout.addWidget(self.cpu_card, 0, 0)
        stats_layout.addWidget(self.memory_card, 0, 1)
        stats_layout.addWidget(self.disk_card, 1, 0)
        stats_layout.addWidget(self.battery_card, 1, 1)
        
        layout.addWidget(stats_frame)
        
        # Quick actions
        actions_frame = QFrame()
        actions_layout = QHBoxLayout(actions_frame)
        
        quick_scan_btn = ModernButton("Quick Scan", "⚡")
        system_cleanup_btn = ModernButton("System Cleanup", "🧹")
        update_check_btn = ModernButton("Check Updates", "🔄")
        
        quick_scan_btn.clicked.connect(lambda: self.switch_module(1))
        
        actions_layout.addWidget(quick_scan_btn)
        actions_layout.addWidget(system_cleanup_btn)
        actions_layout.addWidget(update_check_btn)
        actions_layout.addStretch()
        
        layout.addWidget(actions_frame)
        layout.addStretch()
        
        return widget
        
    def create_antivirus(self) -> QWidget:
        """Create the antivirus module"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setContentsMargins(30, 30, 30, 30)
        layout.setSpacing(20)
        
        # Title
        title = QLabel("Antivirus Protection")
        title.setFont(QFont("Segoe UI", 24, QFont.Bold))
        title.setStyleSheet("color: #2c3e50;")
        layout.addWidget(title)
        
        # Scan options
        scan_frame = QGroupBox("Scan Options")
        scan_layout = QVBoxLayout(scan_frame)
        
        quick_scan_btn = ModernButton("Quick Scan", "⚡")
        full_scan_btn = ModernButton("Full System Scan", "🔍")
        custom_scan_btn = ModernButton("Custom Scan", "📁")
        
        quick_scan_btn.clicked.connect(self.quick_scan)
        full_scan_btn.clicked.connect(self.full_scan)
        
        scan_layout.addWidget(quick_scan_btn)
        scan_layout.addWidget(full_scan_btn)
        scan_layout.addWidget(custom_scan_btn)
        
        # Scan progress
        self.scan_progress = QProgressBar()
        self.scan_progress.setVisible(False)
        self.scan_status = QLabel("Last scan: Never")
        self.scan_status.setFont(QFont("Segoe UI", 10))
        
        scan_layout.addWidget(self.scan_progress)
        scan_layout.addWidget(self.scan_status)
        
        layout.addWidget(scan_frame)
        
        # Quarantine
        quarantine_frame = QGroupBox("Quarantine")
        quarantine_layout = QVBoxLayout(quarantine_frame)
        
        self.quarantine_list = QListWidget()
        self.quarantine_list.addItem("No items in quarantine")
        
        quarantine_layout.addWidget(self.quarantine_list)
        
        layout.addWidget(quarantine_frame)
        layout.addStretch()
        
        return widget
        
    def create_firewall(self) -> QWidget:
        """Create the firewall module"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setContentsMargins(30, 30, 30, 30)
        layout.setSpacing(20)
        
        # Title
        title = QLabel("Firewall Management")
        title.setFont(QFont("Segoe UI", 24, QFont.Bold))
        title.setStyleSheet("color: #2c3e50;")
        layout.addWidget(title)
        
        # Network applications table
        apps_frame = QGroupBox("Network Applications")
        apps_layout = QVBoxLayout(apps_frame)
        
        self.apps_table = QTableWidget(0, 4)
        self.apps_table.setHorizontalHeaderLabels(["Application", "Status", "Data Usage", "Action"])
        self.apps_table.horizontalHeader().setStretchLastSection(True)
        
        # Add some dummy data
        self.populate_firewall_table()
        
        apps_layout.addWidget(self.apps_table)
        layout.addWidget(apps_frame)
        layout.addStretch()
        
        return widget
        
    def create_tts_tool(self) -> QWidget:
        """Create the TTS tool module"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setContentsMargins(30, 30, 30, 30)
        layout.setSpacing(20)
        
        # Title
        title = QLabel("Text-to-Speech Tool")
        title.setFont(QFont("Segoe UI", 24, QFont.Bold))
        title.setStyleSheet("color: #2c3e50;")
        layout.addWidget(title)
        
        # Input section
        input_frame = QGroupBox("Text Input")
        input_layout = QVBoxLayout(input_frame)
        
        self.tts_input = QTextEdit()
        self.tts_input.setPlaceholderText("Enter text to convert to speech...")
        self.tts_input.setMaximumHeight(150)
        
        # Controls
        controls_layout = QHBoxLayout()
        
        self.tts_language = QComboBox()
        self.tts_language.addItems(["English", "नेपाली"])
        
        play_btn = ModernButton("Play", "▶️")
        save_btn = ModernButton("Save Audio", "💾")
        
        play_btn.clicked.connect(self.play_tts)
        save_btn.clicked.connect(self.save_tts)
        
        controls_layout.addWidget(QLabel("Language:"))
        controls_layout.addWidget(self.tts_language)
        controls_layout.addStretch()
        controls_layout.addWidget(play_btn)
        controls_layout.addWidget(save_btn)
        
        input_layout.addWidget(self.tts_input)
        input_layout.addLayout(controls_layout)
        
        layout.addWidget(input_frame)
        layout.addStretch()
        
        return widget
        
    def create_ai_assistant(self) -> QWidget:
        """Create the AI assistant module"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setContentsMargins(30, 30, 30, 30)
        layout.setSpacing(20)
        
        # Title
        title = QLabel("AI Assistant")
        title.setFont(QFont("Segoe UI", 24, QFont.Bold))
        title.setStyleSheet("color: #2c3e50;")
        layout.addWidget(title)
        
        # Chat area
        self.chat_area = QTextEdit()
        self.chat_area.setReadOnly(True)
        self.chat_area.append("🤖 <b>TechSewa AI:</b> Hello! How can I help you today?")
        
        # Input area
        input_layout = QHBoxLayout()
        
        self.ai_input = QLineEdit()
        self.ai_input.setPlaceholderText("Ask me anything...")
        self.ai_input.setFixedHeight(40)
        self.ai_input.returnPressed.connect(self.send_ai_message)
        
        send_btn = ModernButton("Send", "📤")
        send_btn.clicked.connect(self.send_ai_message)
        send_btn.setFixedWidth(100)
        
        input_layout.addWidget(self.ai_input)
        input_layout.addWidget(send_btn)
        
        layout.addWidget(self.chat_area, 1)
        layout.addLayout(input_layout)
        
        return widget
        
    def create_settings(self) -> QWidget:
        """Create the settings module"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setContentsMargins(30, 30, 30, 30)
        layout.setSpacing(20)
        
        # Title
        title = QLabel("Settings")
        title.setFont(QFont("Segoe UI", 24, QFont.Bold))
        title.setStyleSheet("color: #2c3e50;")
        layout.addWidget(title)
        
        # Appearance settings
        appearance_frame = QGroupBox("Appearance")
        appearance_layout = QVBoxLayout(appearance_frame)
        
        theme_layout = QHBoxLayout()
        theme_layout.addWidget(QLabel("Theme:"))
        self.theme_combo = QComboBox()
        self.theme_combo.addItems(["Light", "Dark"])
        self.theme_combo.setCurrentText(self.current_theme.title())
        self.theme_combo.currentTextChanged.connect(self.change_theme)
        theme_layout.addWidget(self.theme_combo)
        theme_layout.addStretch()
        
        language_layout = QHBoxLayout()
        language_layout.addWidget(QLabel("Language:"))
        self.settings_language = QComboBox()
        self.settings_language.addItems(["English", "नेपाली"])
        self.settings_language.setCurrentText(self.current_language)
        self.settings_language.currentTextChanged.connect(self.change_language)
        language_layout.addWidget(self.settings_language)
        language_layout.addStretch()
        
        appearance_layout.addLayout(theme_layout)
        appearance_layout.addLayout(language_layout)
        
        # System settings
        system_frame = QGroupBox("System")
        system_layout = QVBoxLayout(system_frame)
        
        startup_checkbox = QCheckBox("Start TechSewa with Windows")
        auto_update_checkbox = QCheckBox("Check for updates automatically")
        notifications_checkbox = QCheckBox("Enable notifications")
        
        system_layout.addWidget(startup_checkbox)
        system_layout.addWidget(auto_update_checkbox)
        system_layout.addWidget(notifications_checkbox)
        
        layout.addWidget(appearance_frame)
        layout.addWidget(system_frame)
        layout.addStretch()
        
        return widget
        
    def create_about(self) -> QWidget:
        """Create the about module"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setContentsMargins(30, 30, 30, 30)
        layout.setSpacing(20)
        layout.setAlignment(Qt.AlignCenter)
        
        # App icon/logo
        logo_label = QLabel("🛡️")
        logo_label.setFont(QFont("Segoe UI Emoji", 48))
        logo_label.setAlignment(Qt.AlignCenter)
        
        # App name and version
        app_name = QLabel(f"{APP_NAME}")
        app_name.setFont(QFont("Segoe UI", 28, QFont.Bold))
        app_name.setAlignment(Qt.AlignCenter)
        app_name.setStyleSheet("color: #2c3e50;")
        
        version_label = QLabel(f"Version {APP_VERSION}")
        version_label.setFont(QFont("Segoe UI", 14))
        version_label.setAlignment(Qt.AlignCenter)
        version_label.setStyleSheet("color: #7f8c8d;")
        
        # Description
        description = QLabel("A multifunctional system utility, cybersecurity, and AI assistant")
        description.setFont(QFont("Segoe UI", 12))
        description.setAlignment(Qt.AlignCenter)
        description.setWordWrap(True)
        description.setStyleSheet("color: #34495e; margin: 20px;")
        
        # Developer info
        developer_label = QLabel(f"Developed by {DEVELOPER_NAME}")
        developer_label.setFont(QFont("Segoe UI", 12, QFont.Bold))
        developer_label.setAlignment(Qt.AlignCenter)
        
        # Links
        links_layout = QHBoxLayout()
        
        github_btn = ModernButton("GitHub", "🐱")
        github_btn.clicked.connect(lambda: webbrowser.open(f"https://github.com/{DEVELOPER_GITHUB}"))
        
        email_btn = ModernButton("Feedback", "📧")
        email_btn.clicked.connect(lambda: webbrowser.open(f"mailto:{DEVELOPER_EMAIL}"))
        
        links_layout.addStretch()
        links_layout.addWidget(github_btn)
        links_layout.addWidget(email_btn)
        links_layout.addStretch()
        
        layout.addStretch()
        layout.addWidget(logo_label)
        layout.addWidget(app_name)
        layout.addWidget(version_label)
        layout.addWidget(description)
        layout.addWidget(developer_label)
        layout.addLayout(links_layout)
        layout.addStretch()
        
        return widget
        
    def setup_system_monitor(self):
        """Setup system monitoring"""
        self.system_monitor = SystemMonitor()
        self.system_monitor.stats_updated.connect(self.update_system_stats)
        self.system_monitor.start()
        
    def update_system_stats(self, stats: SystemStats):
        """Update system statistics display"""
        self.cpu_card.update_value(stats.cpu_percent)
        self.memory_card.update_value(stats.memory_percent)
        self.disk_card.update_value(stats.disk_percent)
        self.battery_card.update_value(stats.battery_percent)
        
    def switch_module(self, index: int):
        """Switch to specified module with animation"""
        # Update button styles
        for i, btn in enumerate(self.nav_buttons):
            if i == index:
                btn.setStyleSheet("""
                    QPushButton {
                        background: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1,
                                                  stop: 0 #3498db, stop: 1 #2980b9);
                        color: white;
                        border: none;
                        border-radius: 8px;
                        padding: 12px;
                        text-align: left;
                        font-weight: bold;
                    }
                """)
            else:
                btn.setStyleSheet("")
                
        self.stacked_widget.slideToWidget(index)
        
    def toggle_theme(self):
        """Toggle between light and dark themes"""
        self.current_theme = "dark" if self.current_theme == "light" else "light"
        self.settings.setValue("theme", self.current_theme)
        self.theme_btn.setText("☀️" if self.current_theme == "dark" else "🌙")
        self.apply_theme()
        
    def change_theme(self, theme: str):
        """Change theme from settings"""
        self.current_theme = theme.lower()
        self.settings.setValue("theme", self.current_theme)
        self.apply_theme()
        
    def change_language(self, language: str):
        """Change application language"""
        self.current_language = language
        self.settings.setValue("language", language)
        # Update all language-dependent UI elements
        self.update_ui_language()
        
    def update_ui_language(self):
        """Update UI elements based on selected language"""
        if self.current_language == "नेपाली":
            # Add Nepali translations here
            pass
        else:
            # English is default
            pass
            
    def apply_theme(self):
        """Apply the selected theme"""
        if self.current_theme == "dark":
            self.setStyleSheet("""
                QMainWindow {
                    background-color: #2c3e50;
                    color: #ecf0f1;
                }
                QFrame {
                    background-color: #34495e;
                    border: 1px solid #2c3e50;
                    border-radius: 8px;
                }
                QPushButton {
                    background: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1,
                                              stop: 0 #5d6d7e, stop: 1 #4a5568);
                    color: #ecf0f1;
                    border: none;
                    border-radius: 8px;
                    padding: 12px;
                    font-weight: bold;
                }
                QPushButton:hover {
                    background: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1,
                                              stop: 0 #6c7b7f, stop: 1 #5a6c7a);
                }
                QLineEdit, QTextEdit, QComboBox {
                    background-color: #2c3e50;
                    color: #ecf0f1;
                    border: 2px solid #34495e;
                    border-radius: 6px;
                    padding: 8px;
                }
                QGroupBox {
                    font-weight: bold;
                    border: 2px solid #34495e;
                    border-radius: 8px;
                    margin-top: 1ex;
                    padding-top: 15px;
                }
                QGroupBox::title {
                    subcontrol-origin: margin;
                    left: 10px;
                    padding: 0 5px 0 5px;
                }
            """)
        else:
            self.setStyleSheet("""
                QMainWindow {
                    background-color: #f8f9fa;
                    color: #2c3e50;
                }
                QFrame {
                    background-color: white;
                    border: 1px solid #e9ecef;
                    border-radius: 8px;
                }
                QPushButton {
                    background: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1,
                                              stop: 0 #ffffff, stop: 1 #f8f9fa);
                    color: #2c3e50;
                    border: 2px solid #e9ecef;
                    border-radius: 8px;
                    padding: 12px;
                    font-weight: bold;
                }
                QPushButton:hover {
                    background: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1,
                                              stop: 0 #f8f9fa, stop: 1 #e9ecef);
                    border-color: #3498db;
                }
                QLineEdit, QTextEdit, QComboBox {
                    background-color: white;
                    color: #2c3e50;
                    border: 2px solid #e9ecef;
                    border-radius: 6px;
                    padding: 8px;
                }
                QLineEdit:focus, QTextEdit:focus {
                    border-color: #3498db;
                }
                QGroupBox {
                    font-weight: bold;
                    border: 2px solid #e9ecef;
                    border-radius: 8px;
                    margin-top: 1ex;
                    padding-top: 15px;
                }
                QGroupBox::title {
                    subcontrol-origin: margin;
                    left: 10px;
                    padding: 0 5px 0 5px;
                }
            """)
            
    def quick_scan(self):
        """Perform a quick antivirus scan"""
        self.scan_progress.setVisible(True)
        self.scan_progress.setValue(0)
        
        # Simulate scan progress
        self.scan_timer = QTimer()
        self.scan_timer.timeout.connect(self.update_scan_progress)
        self.scan_value = 0
        self.scan_timer.start(50)
        
    def full_scan(self):
        """Perform a full system scan"""
        QMessageBox.information(self, "Full Scan", "Full system scan would start here.\nThis is a demo implementation.")
        
    def update_scan_progress(self):
        """Update scan progress"""
        self.scan_value += 2
        self.scan_progress.setValue(self.scan_value)
        
        if self.scan_value >= 100:
            self.scan_timer.stop()
            self.scan_progress.setVisible(False)
            self.scan_status.setText(f"Last scan: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M')}")
            QMessageBox.information(self, "Scan Complete", "Quick scan completed successfully!\nNo threats detected.")
            
    def populate_firewall_table(self):
        """Populate firewall table with dummy data"""
        apps_data = [
            ("Chrome", "Allowed", "245 MB", "Block"),
            ("Firefox", "Allowed", "156 MB", "Block"),
            ("Steam", "Blocked", "0 MB", "Allow"),
            ("Discord", "Allowed", "89 MB", "Block"),
            ("VS Code", "Allowed", "34 MB", "Block")
        ]
        
        self.apps_table.setRowCount(len(apps_data))
        for row, (app, status, usage, action) in enumerate(apps_data):
            self.apps_table.setItem(row, 0, QTableWidgetItem(app))
            self.apps_table.setItem(row, 1, QTableWidgetItem(status))
            self.apps_table.setItem(row, 2, QTableWidgetItem(usage))
            
            action_btn = QPushButton(action)
            action_btn.setStyleSheet("QPushButton { padding: 5px 15px; }")
            self.apps_table.setCellWidget(row, 3, action_btn)
            
    def play_tts(self):
        """Play text-to-speech"""
        text = self.tts_input.toPlainText()
        if text.strip():
            QMessageBox.information(self, "TTS", f"Playing: {text[:50]}...\n\nThis is a demo implementation.")
        else:
            QMessageBox.warning(self, "TTS", "Please enter some text to convert.")
            
    def save_tts(self):
        """Save TTS audio"""
        text = self.tts_input.toPlainText()
        if text.strip():
            filename, _ = QFileDialog.getSaveFileName(self, "Save Audio", "", "WAV Files (*.wav)")
            if filename:
                QMessageBox.information(self, "TTS", f"Audio would be saved as: {filename}\n\nThis is a demo implementation.")
        else:
            QMessageBox.warning(self, "TTS", "Please enter some text to convert.")
            
    def send_ai_message(self):
        """Send message to AI assistant"""
        message = self.ai_input.text().strip()
        if message:
            # Add user message
            self.chat_area.append(f"<p><b>You:</b> {message}</p>")
            
            # Clear input
            self.ai_input.clear()
            
            # Simulate AI response
            responses = [
                "I'm here to help! This is a demo AI assistant.",
                "That's an interesting question. In a real implementation, I would provide detailed assistance.",
                "I can help you with system optimization, security questions, and general tech support.",
                "Feel free to ask me about any computer-related issues you're experiencing.",
                "This AI assistant would integrate with real language models for actual responses."
            ]
            
            import random
            response = random.choice(responses)
            self.chat_area.append(f"<p><b>🤖 TechSewa AI:</b> {response}</p>")
            
            # Scroll to bottom
            scrollbar = self.chat_area.verticalScrollBar()
            scrollbar.setValue(scrollbar.maximum())
            
    def show_profile(self):
        """Show user profile menu"""
        QMessageBox.information(self, "Profile", "User profile menu would be displayed here.\n\nFeatures:\n- User settings\n- Account management\n- Usage statistics")
        
    def closeEvent(self, event):
        """Handle application close event"""
        # Stop system monitor
        if hasattr(self, 'system_monitor'):
            self.system_monitor.stop()
            
        # Save settings
        self.settings.setValue("theme", self.current_theme)
        self.settings.setValue("language", self.current_language)
        
        event.accept()

def main():
    """Main application entry point"""
    app = QApplication(sys.argv)
    app.setApplicationName(APP_NAME)
    app.setApplicationVersion(APP_VERSION)
    app.setOrganizationName("TechSewa")
    
    # Set application icon (would use actual icon file in production)
    app.setWindowIcon(QIcon())
    
    # Create and show main window
    window = TechSewaMainWindow()
    window.show()
    
    # Start event loop
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()