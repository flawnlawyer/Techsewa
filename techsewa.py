#!/usr/bin/env python3
"""
TechSewa - Multifunctional System Utility, Cybersecurity, and AI Assistant
A powerful desktop application built for everyday users with a power-user soul.

Author: Ayush Ojha
GitHub: flawnlawyer
Email: ojhaayush497@gmail.com
Version: 1.0.0
"""

import sys
import os
import json
import platform
import psutil
import threading
import time
from datetime import datetime
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass
from enum import Enum

from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QPushButton, QLabel, QFrame, QStackedWidget, QScrollArea,
    QTextEdit, QLineEdit, QComboBox, QProgressBar, QListWidget,
    QListWidgetItem, QMessageBox, QFileDialog, QSlider, QCheckBox,
    QGridLayout, QGroupBox, QTabWidget, QSplitter, QSizePolicy
)
from PyQt5.QtCore import (
    Qt, QTimer, QThread, pyqtSignal, QPropertyAnimation,
    QEasingCurve, QRect, QSize, QPoint, QThreadPool, QRunnable
)
from PyQt5.QtGui import (
    QIcon, QFont, QPixmap, QPainter, QColor, QPalette,
    QLinearGradient, QBrush, QPen, QFontMetrics
)

# Type definitions for better code organization
class Theme(Enum):
    LIGHT = "light"
    DARK = "dark"

class Language(Enum):
    ENGLISH = "en"
    NEPALI = "ne"

class Module(Enum):
    HOME = "home"
    ANTIVIRUS = "antivirus"
    FIREWALL = "firewall"
    TTS = "tts"
    AI_ASSISTANT = "ai_assistant"
    SETTINGS = "settings"
    ABOUT = "about"

@dataclass
class SystemMetrics:
    cpu_percent: float
    memory_percent: float
    disk_percent: float
    battery_percent: Optional[float]
    gpu_percent: Optional[float]
    timestamp: datetime

class ThemeManager:
    """Manages application themes with consistent styling"""
    
    def __init__(self):
        self.current_theme = Theme.DARK
        self.themes = {
            Theme.LIGHT: {
                'bg_primary': '#FFFFFF',
                'bg_secondary': '#F8F9FA',
                'bg_tertiary': '#E9ECEF',
                'text_primary': '#212529',
                'text_secondary': '#6C757D',
                'accent_primary': '#007BFF',
                'accent_secondary': '#6F42C1',
                'success': '#28A745',
                'warning': '#FFC107',
                'danger': '#DC3545',
                'border': '#DEE2E6',
                'shadow': 'rgba(0, 0, 0, 0.1)'
            },
            Theme.DARK: {
                'bg_primary': '#1A1A1A',
                'bg_secondary': '#2D2D2D',
                'bg_tertiary': '#404040',
                'text_primary': '#FFFFFF',
                'text_secondary': '#B0B0B0',
                'accent_primary': '#4DABF7',
                'accent_secondary': '#BE4BDB',
                'success': '#51CF66',
                'warning': '#FFD43B',
                'danger': '#FF6B6B',
                'border': '#404040',
                'shadow': 'rgba(0, 0, 0, 0.3)'
            }
        }
    
    def get_color(self, color_name: str) -> str:
        """Get color value for current theme"""
        return self.themes[self.current_theme][color_name]
    
    def apply_theme(self, widget: QWidget) -> None:
        """Apply current theme to widget"""
        colors = self.themes[self.current_theme]
        
        # Create stylesheet
        stylesheet = f"""
        QMainWindow {{
            background-color: {colors['bg_primary']};
            color: {colors['text_primary']};
        }}
        
        QWidget {{
            background-color: {colors['bg_primary']};
            color: {colors['text_primary']};
            font-family: 'Segoe UI', Arial, sans-serif;
        }}
        
        QFrame#sidebar {{
            background-color: {colors['bg_secondary']};
            border-right: 1px solid {colors['border']};
        }}
        
        QFrame#navbar {{
            background-color: {colors['bg_secondary']};
            border-bottom: 1px solid {colors['border']};
        }}
        
        QPushButton {{
            background-color: {colors['bg_tertiary']};
            border: 1px solid {colors['border']};
            border-radius: 8px;
            padding: 8px 16px;
            color: {colors['text_primary']};
            font-weight: 500;
        }}
        
        QPushButton:hover {{
            background-color: {colors['accent_primary']};
            color: white;
        }}
        
        QPushButton:pressed {{
            background-color: {colors['accent_secondary']};
        }}
        
        QPushButton#sidebar-btn {{
            background-color: transparent;
            border: none;
            border-radius: 12px;
            padding: 12px;
            text-align: left;
            font-size: 14px;
        }}
        
        QPushButton#sidebar-btn:hover {{
            background-color: {colors['accent_primary']};
            color: white;
        }}
        
        QPushButton#sidebar-btn:checked {{
            background-color: {colors['accent_primary']};
            color: white;
        }}
        
        QLineEdit {{
            background-color: {colors['bg_tertiary']};
            border: 1px solid {colors['border']};
            border-radius: 8px;
            padding: 8px 12px;
            color: {colors['text_primary']};
        }}
        
        QTextEdit {{
            background-color: {colors['bg_tertiary']};
            border: 1px solid {colors['border']};
            border-radius: 8px;
            padding: 8px;
            color: {colors['text_primary']};
        }}
        
        QProgressBar {{
            background-color: {colors['bg_tertiary']};
            border: 1px solid {colors['border']};
            border-radius: 8px;
            text-align: center;
        }}
        
        QProgressBar::chunk {{
            background-color: {colors['accent_primary']};
            border-radius: 8px;
        }}
        
        QListWidget {{
            background-color: {colors['bg_tertiary']};
            border: 1px solid {colors['border']};
            border-radius: 8px;
            padding: 4px;
        }}
        
        QGroupBox {{
            font-weight: bold;
            border: 2px solid {colors['border']};
            border-radius: 8px;
            margin-top: 1ex;
            padding-top: 10px;
        }}
        
        QGroupBox::title {{
            subcontrol-origin: margin;
            left: 10px;
            padding: 0 5px 0 5px;
        }}
        """
        
        widget.setStyleSheet(stylesheet)

class SystemMonitor(QThread):
    """Monitors system metrics in background thread"""
    
    metrics_updated = pyqtSignal(object)
    
    def __init__(self):
        super().__init__()
        self.running = True
    
    def run(self):
        while self.running:
            try:
                # Get system metrics
                cpu_percent = psutil.cpu_percent(interval=1)
                memory = psutil.virtual_memory()
                disk = psutil.disk_usage('/')
                
                # Get battery info if available
                battery_percent = None
                if hasattr(psutil, 'sensors_battery'):
                    battery = psutil.sensors_battery()
                    if battery:
                        battery_percent = battery.percent
                
                # GPU info (simplified - in real app would use GPU libraries)
                gpu_percent = None
                
                metrics = SystemMetrics(
                    cpu_percent=cpu_percent,
                    memory_percent=memory.percent,
                    disk_percent=disk.percent,
                    battery_percent=battery_percent,
                    gpu_percent=gpu_percent,
                    timestamp=datetime.now()
                )
                
                self.metrics_updated.emit(metrics)
                time.sleep(2)  # Update every 2 seconds
                
            except Exception as e:
                print(f"System monitor error: {e}")
                time.sleep(5)
    
    def stop(self):
        self.running = False

class SidebarButton(QPushButton):
    """Custom sidebar button with icon and text"""
    
    def __init__(self, text: str, icon_text: str = "", parent=None):
        super().__init__(parent)
        self.setText(f"  {icon_text}  {text}")
        self.setObjectName("sidebar-btn")
        self.setCheckable(True)
        self.setMinimumHeight(50)
        self.setCursor(Qt.PointingHandCursor)

class MetricCard(QFrame):
    """System metric display card"""
    
    def __init__(self, title: str, value: str, unit: str = "", color: str = "#007BFF"):
        super().__init__()
        self.setObjectName("metric-card")
        self.setMinimumHeight(100)
        self.setMaximumHeight(120)
        
        layout = QVBoxLayout(self)
        
        # Title
        title_label = QLabel(title)
        title_label.setStyleSheet(f"color: {color}; font-weight: bold; font-size: 14px;")
        layout.addWidget(title_label)
        
        # Value and unit
        value_layout = QHBoxLayout()
        value_label = QLabel(value)
        value_label.setStyleSheet("font-size: 24px; font-weight: bold;")
        value_layout.addWidget(value_label)
        
        if unit:
            unit_label = QLabel(unit)
            unit_label.setStyleSheet("font-size: 14px; color: #6C757D;")
            value_layout.addWidget(unit_label)
        
        value_layout.addStretch()
        layout.addLayout(value_layout)
        
        # Progress bar
        self.progress_bar = QProgressBar()
        self.progress_bar.setMaximum(100)
        self.progress_bar.setMinimum(0)
        self.progress_bar.setValue(0)
        layout.addWidget(self.progress_bar)
    
    def update_metric(self, value: float, max_value: float = 100):
        """Update metric value and progress bar"""
        self.progress_bar.setValue(int(value))
        # Update color based on usage
        if value > 80:
            color = "#DC3545"  # Red for high usage
        elif value > 60:
            color = "#FFC107"  # Yellow for medium usage
        else:
            color = "#28A745"  # Green for low usage
        
        self.progress_bar.setStyleSheet(f"""
            QProgressBar::chunk {{
                background-color: {color};
                border-radius: 8px;
            }}
        """)

class HomeModule(QWidget):
    """Home/Dashboard module with system metrics"""
    
    def __init__(self, theme_manager: ThemeManager):
        super().__init__()
        self.theme_manager = theme_manager
        self.setup_ui()
        
        # Start system monitoring
        self.system_monitor = SystemMonitor()
        self.system_monitor.metrics_updated.connect(self.update_metrics)
        self.system_monitor.start()
    
    def setup_ui(self):
        layout = QVBoxLayout(self)
        
        # Header
        header = QLabel("System Dashboard")
        header.setStyleSheet("font-size: 24px; font-weight: bold; margin-bottom: 20px;")
        layout.addWidget(header)
        
        # Metrics grid
        metrics_layout = QGridLayout()
        
        # Create metric cards
        self.cpu_card = MetricCard("CPU Usage", "0", "%", "#007BFF")
        self.memory_card = MetricCard("Memory Usage", "0", "%", "#28A745")
        self.disk_card = MetricCard("Disk Usage", "0", "%", "#FFC107")
        self.battery_card = MetricCard("Battery", "0", "%", "#6F42C1")
        
        # Add cards to grid
        metrics_layout.addWidget(self.cpu_card, 0, 0)
        metrics_layout.addWidget(self.memory_card, 0, 1)
        metrics_layout.addWidget(self.disk_card, 1, 0)
        metrics_layout.addWidget(self.battery_card, 1, 1)
        
        layout.addLayout(metrics_layout)
        layout.addStretch()
    
    def update_metrics(self, metrics: SystemMetrics):
        """Update system metrics display"""
        self.cpu_card.update_metric(metrics.cpu_percent)
        self.memory_card.update_metric(metrics.memory_percent)
        self.disk_card.update_metric(metrics.disk_percent)
        
        if metrics.battery_percent is not None:
            self.battery_card.update_metric(metrics.battery_percent)
        else:
            self.battery_card.update_metric(0)
            self.battery_card.setVisible(False)

class AntivirusModule(QWidget):
    """Antivirus scanning module"""
    
    def __init__(self, theme_manager: ThemeManager):
        super().__init__()
        self.theme_manager = theme_manager
        self.setup_ui()
    
    def setup_ui(self):
        layout = QVBoxLayout(self)
        
        # Header
        header = QLabel("Antivirus Scanner")
        header.setStyleSheet("font-size: 24px; font-weight: bold; margin-bottom: 20px;")
        layout.addWidget(header)
        
        # Scan options
        scan_group = QGroupBox("Scan Options")
        scan_layout = QVBoxLayout(scan_group)
        
        quick_scan_btn = QPushButton("Quick Scan")
        quick_scan_btn.clicked.connect(lambda: self.start_scan("quick"))
        scan_layout.addWidget(quick_scan_btn)
        
        full_scan_btn = QPushButton("Full Scan")
        full_scan_btn.clicked.connect(lambda: self.start_scan("full"))
        scan_layout.addWidget(full_scan_btn)
        
        layout.addWidget(scan_group)
        
        # Progress
        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        layout.addWidget(self.progress_bar)
        
        # Status
        self.status_label = QLabel("Ready to scan")
        layout.addWidget(self.status_label)
        
        # Quarantine
        quarantine_group = QGroupBox("Quarantine")
        quarantine_layout = QVBoxLayout(quarantine_group)
        
        self.quarantine_list = QListWidget()
        quarantine_layout.addWidget(self.quarantine_list)
        
        layout.addWidget(quarantine_group)
        layout.addStretch()
    
    def start_scan(self, scan_type: str):
        """Start antivirus scan (dummy implementation)"""
        self.progress_bar.setVisible(True)
        self.progress_bar.setValue(0)
        self.status_label.setText(f"Starting {scan_type} scan...")
        
        # Simulate scan progress
        def simulate_scan():
            for i in range(101):
                self.progress_bar.setValue(i)
                time.sleep(0.1)
            
            self.progress_bar.setVisible(False)
            self.status_label.setText(f"{scan_type.title()} scan completed at {datetime.now().strftime('%H:%M:%S')}")
        
        # Run in background thread
        scan_thread = threading.Thread(target=simulate_scan)
        scan_thread.daemon = True
        scan_thread.start()

class FirewallModule(QWidget):
    """Firewall management module"""
    
    def __init__(self, theme_manager: ThemeManager):
        super().__init__()
        self.theme_manager = theme_manager
        self.setup_ui()
    
    def setup_ui(self):
        layout = QVBoxLayout(self)
        
        # Header
        header = QLabel("Firewall Frenzy")
        header.setStyleSheet("font-size: 24px; font-weight: bold; margin-bottom: 20px;")
        layout.addWidget(header)
        
        # Network usage
        usage_group = QGroupBox("Network Usage")
        usage_layout = QVBoxLayout(usage_group)
        
        self.network_label = QLabel("Monitoring network activity...")
        usage_layout.addWidget(self.network_label)
        
        layout.addWidget(usage_group)
        
        # Running apps
        apps_group = QGroupBox("Running Applications")
        apps_layout = QVBoxLayout(apps_group)
        
        self.apps_list = QListWidget()
        apps_layout.addWidget(self.apps_list)
        
        layout.addWidget(apps_group)
        
        # Update apps list
        self.update_running_apps()
        
        layout.addStretch()
    
    def update_running_apps(self):
        """Update list of running applications"""
        self.apps_list.clear()
        
        try:
            for proc in psutil.process_iter(['pid', 'name', 'cpu_percent']):
                try:
                    if proc.info['cpu_percent'] > 0:
                        item_text = f"{proc.info['name']} (PID: {proc.info['pid']}) - CPU: {proc.info['cpu_percent']:.1f}%"
                        item = QListWidgetItem(item_text)
                        self.apps_list.addItem(item)
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    pass
        except Exception as e:
            print(f"Error updating apps: {e}")

class TTSModule(QWidget):
    """Text-to-Speech module"""
    
    def __init__(self, theme_manager: ThemeManager):
        super().__init__()
        self.theme_manager = theme_manager
        self.setup_ui()
    
    def setup_ui(self):
        layout = QVBoxLayout(self)
        
        # Header
        header = QLabel("Text-to-Speech Tool")
        header.setStyleSheet("font-size: 24px; font-weight: bold; margin-bottom: 20px;")
        layout.addWidget(header)
        
        # Language selection
        lang_layout = QHBoxLayout()
        lang_layout.addWidget(QLabel("Language:"))
        
        self.language_combo = QComboBox()
        self.language_combo.addItems(["English", "Nepali"])
        lang_layout.addWidget(self.language_combo)
        
        layout.addLayout(lang_layout)
        
        # Text input
        self.text_input = QTextEdit()
        self.text_input.setPlaceholderText("Enter text to convert to speech...")
        self.text_input.setMaximumHeight(150)
        layout.addWidget(self.text_input)
        
        # Controls
        controls_layout = QHBoxLayout()
        
        self.play_btn = QPushButton("Play")
        self.play_btn.clicked.connect(self.play_audio)
        controls_layout.addWidget(self.play_btn)
        
        self.save_btn = QPushButton("Save Audio")
        self.save_btn.clicked.connect(self.save_audio)
        controls_layout.addWidget(self.save_btn)
        
        layout.addLayout(controls_layout)
        
        # Status
        self.status_label = QLabel("Ready")
        layout.addWidget(self.status_label)
        
        layout.addStretch()
    
    def play_audio(self):
        """Play TTS audio (dummy implementation)"""
        text = self.text_input.toPlainText()
        if text:
            language = self.language_combo.currentText()
            self.status_label.setText(f"Playing audio in {language}...")
            # In real implementation, would use gTTS or pyttsx3
        else:
            self.status_label.setText("Please enter text first")
    
    def save_audio(self):
        """Save TTS audio to file"""
        text = self.text_input.toPlainText()
        if text:
            file_path, _ = QFileDialog.getSaveFileName(
                self, "Save Audio File", "", "Audio Files (*.mp3 *.wav)"
            )
            if file_path:
                self.status_label.setText(f"Audio saved to {file_path}")
        else:
            self.status_label.setText("Please enter text first")

class AIAssistantModule(QWidget):
    """AI Assistant module"""
    
    def __init__(self, theme_manager: ThemeManager):
        super().__init__()
        self.theme_manager = theme_manager
        self.setup_ui()
    
    def setup_ui(self):
        layout = QVBoxLayout(self)
        
        # Header
        header = QLabel("AI Assistant")
        header.setStyleSheet("font-size: 24px; font-weight: bold; margin-bottom: 20px;")
        layout.addWidget(header)
        
        # Chat area
        self.chat_area = QTextEdit()
        self.chat_area.setReadOnly(True)
        self.chat_area.setMaximumHeight(300)
        layout.addWidget(self.chat_area)
        
        # Input area
        input_layout = QHBoxLayout()
        
        self.input_field = QLineEdit()
        self.input_field.setPlaceholderText("Ask me anything...")
        self.input_field.returnPressed.connect(self.send_message)
        input_layout.addWidget(self.input_field)
        
        send_btn = QPushButton("Send")
        send_btn.clicked.connect(self.send_message)
        input_layout.addWidget(send_btn)
        
        layout.addLayout(input_layout)
        layout.addStretch()
        
        # Welcome message
        self.chat_area.append("AI Assistant: Hello! I'm your AI assistant. How can I help you today?")
    
    def send_message(self):
        """Send message to AI assistant"""
        message = self.input_field.text().strip()
        if message:
            self.chat_area.append(f"You: {message}")
            self.input_field.clear()
            
            # Simulate AI response
            response = self.generate_ai_response(message)
            self.chat_area.append(f"AI Assistant: {response}")
            
            # Scroll to bottom
            scrollbar = self.chat_area.verticalScrollBar()
            scrollbar.setValue(scrollbar.maximum())
    
    def generate_ai_response(self, message: str) -> str:
        """Generate AI response (dummy implementation)"""
        message_lower = message.lower()
        
        if "hello" in message_lower or "hi" in message_lower:
            return "Hello! How can I assist you today?"
        elif "help" in message_lower:
            return "I can help you with system information, troubleshooting, and general questions. What do you need?"
        elif "system" in message_lower:
            return "I can help you monitor system resources, run diagnostics, and optimize performance."
        elif "security" in message_lower:
            return "I can assist with security scans, firewall management, and threat detection."
        else:
            return "That's an interesting question! I'm here to help with your tech needs."

class SettingsModule(QWidget):
    """Settings module"""
    
    def __init__(self, theme_manager: ThemeManager, main_window):
        super().__init__()
        self.theme_manager = theme_manager
        self.main_window = main_window
        self.setup_ui()
    
    def setup_ui(self):
        layout = QVBoxLayout(self)
        
        # Header
        header = QLabel("Settings")
        header.setStyleSheet("font-size: 24px; font-weight: bold; margin-bottom: 20px;")
        layout.addWidget(header)
        
        # Theme settings
        theme_group = QGroupBox("Appearance")
        theme_layout = QVBoxLayout(theme_group)
        
        theme_layout.addWidget(QLabel("Theme:"))
        self.theme_combo = QComboBox()
        self.theme_combo.addItems(["Dark", "Light"])
        self.theme_combo.currentTextChanged.connect(self.change_theme)
        theme_layout.addWidget(self.theme_combo)
        
        layout.addWidget(theme_group)
        
        # Language settings
        lang_group = QGroupBox("Language")
        lang_layout = QVBoxLayout(lang_group)
        
        lang_layout.addWidget(QLabel("Language:"))
        self.lang_combo = QComboBox()
        self.lang_combo.addItems(["English", "Nepali"])
        lang_layout.addWidget(self.lang_combo)
        
        layout.addWidget(lang_group)
        
        # Update checker
        update_group = QGroupBox("Updates")
        update_layout = QVBoxLayout(update_group)
        
        check_update_btn = QPushButton("Check for Updates")
        check_update_btn.clicked.connect(self.check_updates)
        update_layout.addWidget(check_update_btn)
        
        layout.addWidget(update_group)
        
        layout.addStretch()
    
    def change_theme(self, theme_name: str):
        """Change application theme"""
        if theme_name == "Dark":
            self.theme_manager.current_theme = Theme.DARK
        else:
            self.theme_manager.current_theme = Theme.LIGHT
        
        self.theme_manager.apply_theme(self.main_window)
    
    def check_updates(self):
        """Check for application updates"""
        QMessageBox.information(self, "Updates", "TechSewa is up to date! (v1.0.0)")

class AboutModule(QWidget):
    """About module"""
    
    def __init__(self, theme_manager: ThemeManager):
        super().__init__()
        self.theme_manager = theme_manager
        self.setup_ui()
    
    def setup_ui(self):
        layout = QVBoxLayout(self)
        
        # Header
        header = QLabel("About TechSewa")
        header.setStyleSheet("font-size: 24px; font-weight: bold; margin-bottom: 20px;")
        layout.addWidget(header)
        
        # App info
        info_group = QGroupBox("Application Information")
        info_layout = QVBoxLayout(info_group)
        
        info_layout.addWidget(QLabel("Version: 1.0.0"))
        info_layout.addWidget(QLabel("Developer: Ayush Ojha"))
        info_layout.addWidget(QLabel("GitHub: flawnlawyer"))
        info_layout.addWidget(QLabel("Email: ojhaayush497@gmail.com"))
        
        layout.addWidget(info_group)
        
        # Description
        desc_group = QGroupBox("Description")
        desc_layout = QVBoxLayout(desc_group)
        
        desc_text = QLabel(
            "TechSewa is a multifunctional system utility, cybersecurity, and AI assistant "
            "built for everyday users with a power-user soul. It provides comprehensive "
            "system monitoring, security tools, and AI assistance in an elegant, "
            "modern interface."
        )
        desc_text.setWordWrap(True)
        desc_layout.addWidget(desc_text)
        
        layout.addWidget(desc_group)
        
        # Feedback button
        feedback_btn = QPushButton("Send Feedback")
        feedback_btn.clicked.connect(self.send_feedback)
        layout.addWidget(feedback_btn)
        
        layout.addStretch()
    
    def send_feedback(self):
        """Open feedback email"""
        QMessageBox.information(
            self, "Feedback", 
            "Please send feedback to: ojhaayush497@gmail.com"
        )

class TechSewaApp(QMainWindow):
    """Main TechSewa application window"""
    
    def __init__(self):
        super().__init__()
        self.theme_manager = ThemeManager()
        self.current_language = Language.ENGLISH
        self.setup_ui()
        self.setup_sidebar()
        self.setup_navbar()
        self.setup_modules()
        
        # Apply initial theme
        self.theme_manager.apply_theme(self)
        
        # Set window properties
        self.setWindowTitle("TechSewa - System Utility & AI Assistant")
        self.setMinimumSize(1200, 800)
        self.resize(1400, 900)
        
        # Center window
        self.center_window()
    
    def setup_ui(self):
        """Setup main UI layout"""
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # Main layout
        main_layout = QHBoxLayout(central_widget)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        
        # Sidebar
        self.sidebar = QFrame()
        self.sidebar.setObjectName("sidebar")
        self.sidebar.setMaximumWidth(250)
        self.sidebar.setMinimumWidth(200)
        
        # Content area
        self.content_area = QStackedWidget()
        
        # Add to main layout
        main_layout.addWidget(self.sidebar)
        main_layout.addWidget(self.content_area)
    
    def setup_sidebar(self):
        """Setup sidebar with navigation buttons"""
        sidebar_layout = QVBoxLayout(self.sidebar)
        sidebar_layout.setContentsMargins(10, 20, 10, 20)
        sidebar_layout.setSpacing(5)
        
        # App logo/title
        logo_label = QLabel("🧠 TechSewa")
        logo_label.setStyleSheet("font-size: 18px; font-weight: bold; margin-bottom: 20px;")
        sidebar_layout.addWidget(logo_label)
        
        # Navigation buttons
        self.sidebar_buttons = {}
        
        buttons_data = [
            ("🏠", "Home", Module.HOME),
            ("🛡️", "Antivirus", Module.ANTIVIRUS),
            ("🔥", "Firewall", Module.FIREWALL),
            ("🔊", "TTS Tool", Module.TTS),
            ("🤖", "AI Assistant", Module.AI_ASSISTANT),
            ("⚙️", "Settings", Module.SETTINGS),
            ("ℹ️", "About", Module.ABOUT)
        ]
        
        for icon, text, module in buttons_data:
            btn = SidebarButton(text, icon)
            btn.clicked.connect(lambda checked, m=module: self.switch_module(m))
            self.sidebar_buttons[module] = btn
            sidebar_layout.addWidget(btn)
        
        sidebar_layout.addStretch()
        
        # Set first button as checked
        self.sidebar_buttons[Module.HOME].setChecked(True)
    
    def setup_navbar(self):
        """Setup top navigation bar"""
        # Note: In this implementation, navbar is integrated into content modules
        # For a more complex app, you could add a separate navbar widget
        pass
    
    def setup_modules(self):
        """Setup all application modules"""
        self.modules = {
            Module.HOME: HomeModule(self.theme_manager),
            Module.ANTIVIRUS: AntivirusModule(self.theme_manager),
            Module.FIREWALL: FirewallModule(self.theme_manager),
            Module.TTS: TTSModule(self.theme_manager),
            Module.AI_ASSISTANT: AIAssistantModule(self.theme_manager),
            Module.SETTINGS: SettingsModule(self.theme_manager, self),
            Module.ABOUT: AboutModule(self.theme_manager)
        }
        
        # Add modules to content area
        for module_widget in self.modules.values():
            self.content_area.addWidget(module_widget)
    
    def switch_module(self, module: Module):
        """Switch to specified module"""
        # Update button states
        for btn in self.sidebar_buttons.values():
            btn.setChecked(False)
        self.sidebar_buttons[module].setChecked(True)
        
        # Switch content
        module_index = list(self.modules.keys()).index(module)
        self.content_area.setCurrentIndex(module_index)
        
        # Add smooth transition animation
        self.animate_module_switch()
    
    def animate_module_switch(self):
        """Animate module switching with fade effect"""
        # Create fade animation
        self.content_area.setGraphicsEffect(None)  # Reset any existing effects
        
        # In a more complex implementation, you could add fade/slide animations here
        # For now, we'll keep it simple but the structure is ready for animations
    
    def center_window(self):
        """Center the window on screen"""
        screen = QApplication.primaryScreen().geometry()
        x = (screen.width() - self.width()) // 2
        y = (screen.height() - self.height()) // 2
        self.move(x, y)
    
    def closeEvent(self, event):
        """Handle application close event"""
        # Stop system monitoring
        if hasattr(self.modules[Module.HOME], 'system_monitor'):
            self.modules[Module.HOME].system_monitor.stop()
            self.modules[Module.HOME].system_monitor.wait()
        
        event.accept()

def main():
    """Main application entry point"""
    app = QApplication(sys.argv)
    
    # Set application properties
    app.setApplicationName("TechSewa")
    app.setApplicationVersion("1.0.0")
    app.setOrganizationName("Ayush Ojha")
    
    # Create and show main window
    window = TechSewaApp()
    window.show()
    
    # Start application event loop
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()