#!/usr/bin/env python3
"""
TechSewa - Multifunctional System Utility, Cybersecurity, and AI Assistant
Author: Ayush Ojha
GitHub: flawnlawyer
Email: ojhaayush497@gmail.com
"""

import sys
import platform
import psutil
import threading
import time
from datetime import datetime
from typing import Dict, Any, Optional
from dataclasses import dataclass
from enum import Enum

from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QPushButton, QLabel, QFrame, QStackedWidget, QLineEdit, QTextEdit,
    QProgressBar, QComboBox, QCheckBox, QGroupBox, QGridLayout,
    QMessageBox, QFileDialog, QListWidget, QListWidgetItem,
    QTableWidget, QTableWidgetItem, QTabWidget, QSpinBox
)
from PyQt5.QtCore import Qt, QTimer, QThread, pyqtSignal, QPropertyAnimation, QEasingCurve, QEvent
from PyQt5.QtGui import QIcon, QFont

@dataclass
class AppConfig:
    """Application configuration."""
    APP_NAME = "TechSewa"
    VERSION = "1.0.0"
    DEVELOPER = "Ayush Ojha"
    GITHUB = "flawnlawyer"
    EMAIL = "ojhaayush497@gmail.com"
    SIDEBAR_WIDTH = 80
    NAVBAR_HEIGHT = 60

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

class SystemMonitor(QThread):
    """System resource monitoring thread."""
    cpu_updated = pyqtSignal(float)
    memory_updated = pyqtSignal(dict)
    disk_updated = pyqtSignal(dict)
    
    def __init__(self):
        super().__init__()
        self.running = True
        
    def run(self):
        while self.running:
            try:
                cpu_percent = psutil.cpu_percent(interval=1)
                self.cpu_updated.emit(cpu_percent)
                
                memory = psutil.virtual_memory()
                memory_info = {
                    'total': memory.total,
                    'available': memory.available,
                    'percent': memory.percent,
                    'used': memory.used
                }
                self.memory_updated.emit(memory_info)
                
                disk = psutil.disk_usage('/')
                disk_info = {
                    'total': disk.total,
                    'used': disk.used,
                    'free': disk.free,
                    'percent': (disk.used / disk.total) * 100
                }
                self.disk_updated.emit(disk_info)
                
                time.sleep(2)
            except Exception as e:
                print(f"Monitoring error: {e}")
                time.sleep(5)
    
    def stop(self):
        self.running = False
        self.wait()

class AnimatedButton(QPushButton):
    """Custom animated button."""
    
    def __init__(self, text: str = "", icon: str = "", parent: Optional[QWidget] = None):
        super().__init__(text, parent)
        self.setIcon(QIcon(icon) if icon else QIcon())
        self.setup_style()
        self.setup_animations()
    
    def setup_style(self):
        self.setFixedSize(60, 60)
        self.setStyleSheet("""
            QPushButton {
                border: none;
                border-radius: 30px;
                background-color: transparent;
                color: #333333;
                font-size: 12px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: rgba(33, 150, 243, 0.1);
                border: 2px solid #2196F3;
            }
            QPushButton:pressed {
                background-color: rgba(33, 150, 243, 0.2);
            }
        """)
    
    def setup_animations(self):
        self.animation = QPropertyAnimation(self, b"geometry")
        self.animation.setDuration(150)
        self.animation.setEasingCurve(QEasingCurve.OutCubic)
    
    def enterEvent(self, event: QEvent):
        self.animation.setStartValue(self.geometry())
        new_geometry = self.geometry()
        new_geometry.setWidth(new_geometry.width() + 10)
        new_geometry.setHeight(new_geometry.height() + 10)
        new_geometry.moveCenter(self.geometry().center())
        self.animation.setEndValue(new_geometry)
        self.animation.start()
        super().enterEvent(event)
    
    def leaveEvent(self, event: QEvent):
        self.animation.setStartValue(self.geometry())
        self.animation.setEndValue(self.geometry())
        self.animation.start()
        super().leaveEvent(event)

class SystemCard(QFrame):
    """System monitoring card."""
    
    def __init__(self, title: str, value: str = "0", unit: str = "", parent: Optional[QWidget] = None):
        super().__init__(parent)
        self.title = title
        self.value = value
        self.unit = unit
        self.setup_ui()
    
    def setup_ui(self):
        self.setFixedSize(200, 120)
        self.setStyleSheet("""
            QFrame {
                background-color: white;
                border: 1px solid #E0E0E0;
                border-radius: 10px;
                padding: 10px;
            }
            QFrame:hover {
                border: 2px solid #2196F3;
                box-shadow: 0 4px 8px rgba(0,0,0,0.1);
            }
        """)
        
        layout = QVBoxLayout(self)
        layout.setContentsMargins(15, 15, 15, 15)
        
        self.title_label = QLabel(self.title)
        self.title_label.setStyleSheet("color: #666666; font-size: 14px; font-weight: bold;")
        
        self.value_label = QLabel(f"{self.value} {self.unit}")
        self.value_label.setStyleSheet("color: #2196F3; font-size: 24px; font-weight: bold;")
        
        self.progress_bar = QProgressBar()
        self.progress_bar.setRange(0, 100)
        self.progress_bar.setValue(0)
        self.progress_bar.setStyleSheet("""
            QProgressBar {
                border: 1px solid #E0E0E0;
                border-radius: 5px;
                text-align: center;
                background-color: #F5F5F5;
            }
            QProgressBar::chunk {
                background-color: #2196F3;
                border-radius: 5px;
            }
        """)
        
        layout.addWidget(self.title_label)
        layout.addWidget(self.value_label)
        layout.addWidget(self.progress_bar)
        layout.addStretch()
    
    def update_value(self, value: str, progress: int = 0):
        self.value_label.setText(f"{value} {self.unit}")
        self.progress_bar.setValue(progress)

# Main application window will be added next...