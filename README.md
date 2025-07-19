# TechSewa - Digital Assistant & System Utility

🛡️ **TechSewa** is an elegant, powerful, and intuitive Python desktop application that serves as a multifunctional system utility, cybersecurity tool, and AI assistant. Built for everyday users with a power-user soul.

![TechSewa Screenshot](https://via.placeholder.com/800x600/2c3e50/ffffff?text=TechSewa+Desktop+App)

## ✨ Features

### 🏠 **Dashboard**
- Real-time system monitoring (CPU, Memory, Disk, Battery)
- Beautiful stat cards with color-coded progress bars
- Quick action buttons for common tasks
- Modern card-based layout

### 🛡️ **Antivirus Protection**
- Quick Scan functionality
- Full System Scan
- Custom Scan options
- Quarantine management
- Real-time scan progress with animations

### 🔥 **Firewall Management**
- Network application monitoring
- Allow/Block application controls
- Data usage tracking
- Application status overview

### 🗣️ **Text-to-Speech Tool**
- Multi-language support (English/नेपाली)
- Convert text to speech
- Save audio files
- Clean, intuitive interface

### 🤖 **AI Assistant**
- Interactive chat interface
- Intelligent responses (demo implementation)
- Modern chat UI with message history
- Extensible for real AI integration

### ⚙️ **Settings**
- Light/Dark theme switching
- Language selection (English/नेपाली)
- System preferences
- Persistent settings storage

### ℹ️ **About**
- Application information
- Developer details
- Quick access to GitHub and feedback

## 🎨 Design Philosophy

TechSewa combines the best of modern UI/UX design:

- **Apple's Elegance**: Smooth transitions, minimal clutter, refined aesthetics
- **Google's Material Logic**: Responsive design, structured layouts, intuitive navigation
- **Modern Functionality**: Powerful features in an accessible interface

## 🚀 Installation & Setup

### Prerequisites

- Python 3.7 or higher
- PyQt5
- psutil

### Quick Install

1. **Clone or download the repository**
   ```bash
   git clone https://github.com/flawnlawyer/techsewa.git
   cd techsewa
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Run the application**
   ```bash
   python techsewa.py
   ```

### Alternative Installation

If you don't have the requirements file:

```bash
pip install PyQt5>=5.15.0 psutil>=5.8.0
python techsewa.py
```

## 🖥️ System Requirements

- **Operating System**: Windows 10/11, macOS 10.14+, Linux (Ubuntu 18.04+)
- **Python**: 3.7 or higher
- **Memory**: 256 MB RAM minimum, 512 MB recommended
- **Display**: 1366x768 minimum resolution (optimized for higher resolutions)
- **Storage**: 50 MB free space

## 🎯 Usage Guide

### Navigation
- Use the **sidebar** to switch between modules
- **Search bar** in the top navbar for quick issue finding
- **Theme toggle** (🌙/☀️) for light/dark mode switching
- **Language selector** for English/नेपाली support

### Module-Specific Features

#### Dashboard
- View real-time system statistics
- Click "Quick Scan" to jump to antivirus module
- Monitor system health at a glance

#### Antivirus
- Click "Quick Scan" for a rapid system check
- "Full System Scan" for comprehensive protection
- View scan history and quarantine items

#### Firewall
- Monitor network applications
- Toggle Allow/Block status for applications
- Track data usage per application

#### TTS Tool
- Enter text in the input area
- Select language (English/नेपाली)
- Click "Play" to hear the text
- Click "Save Audio" to export as WAV file

#### AI Assistant
- Type questions in the chat input
- Press Enter or click "Send"
- View conversation history
- Get intelligent assistance (demo responses)

## 🎨 Customization

### Themes
TechSewa supports two beautiful themes:
- **Light Theme**: Clean, minimalist design with white backgrounds
- **Dark Theme**: Modern dark interface with blue accents

### Language Support
- **English**: Full interface translation
- **नेपाली (Nepali)**: Localized for Nepali users

## 🔧 Technical Details

### Architecture
- **Single-file application** for easy deployment
- **Modular design** with separated components
- **Type hints** throughout for better code quality
- **PyQt5** for native desktop performance
- **Threaded system monitoring** for real-time updates

### Code Structure
```
techsewa.py
├── Application Constants
├── Data Classes (SystemStats)
├── Custom Widgets (ModernButton, StatCard, etc.)
├── Core Application (TechSewaMainWindow)
├── Module Creation Methods
├── System Integration
└── Main Entry Point
```

### Key Features
- **Animated transitions** between modules
- **Real-time system monitoring** with background threads
- **Persistent settings** with QSettings
- **Modern styling** with custom CSS
- **Responsive layout** that adapts to screen sizes

## 🛠️ Development

### For Developers

The application is designed to be easily extensible:

1. **Adding new modules**: Create new widget methods in `TechSewaMainWindow`
2. **Extending functionality**: Modify existing module methods
3. **Custom styling**: Update the `apply_theme()` method
4. **New languages**: Extend the `update_ui_language()` method

### Code Quality
- Full type hints for better IDE support
- Comprehensive documentation
- Modular, maintainable code structure
- Pylance-compatible (runs clean in VS Code)

## 📧 Contact & Support

- **Developer**: Ayush Ojha
- **GitHub**: [@flawnlawyer](https://github.com/flawnlawyer)
- **Email**: ojhaayush497@gmail.com

## 🌟 Contributing

We welcome contributions! Please feel free to:
- Report bugs
- Suggest new features
- Submit pull requests
- Improve documentation

## 📄 License

This project is developed for educational and personal use. Please respect the developer's work and provide attribution when using or modifying the code.

## 🚀 Future Enhancements

- Real AI integration with language models
- Advanced system optimization tools
- Network security monitoring
- Plugin system for extensibility
- Multi-language TTS support
- Cloud sync for settings
- Mobile companion app

---

**Built with ❤️ for the Nepali tech community and users worldwide.**

*TechSewa - Your Digital Assistant & System Guardian*