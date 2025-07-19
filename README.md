# TechSewa - Multifunctional System Utility & AI Assistant

🧠 **TechSewa** is a powerful, elegant desktop application that combines system utilities, cybersecurity tools, and AI assistance in a modern, user-friendly interface. Built for everyday users with a power-user soul.

## ✨ Features

### 🏠 **Home Dashboard**
- Real-time system health monitoring
- CPU, RAM, Disk, and Battery usage with visual progress bars
- Color-coded metrics (green/yellow/red based on usage levels)
- Live updates every 2 seconds

### 🛡️ **Antivirus Scanner**
- Quick Scan and Full Scan options
- Progress tracking with visual feedback
- Quarantine management
- Scan history and status reporting

### 🔥 **Firewall Frenzy**
- Real-time network activity monitoring
- Running applications list with CPU usage
- Process management and monitoring
- Network usage statistics

### 🔊 **Text-to-Speech Tool**
- Support for English and Nepali languages
- Text input with preview
- Audio playback and file saving
- Multiple output format options

### 🤖 **AI Assistant**
- Interactive chat interface
- System troubleshooting assistance
- Security and performance advice
- Context-aware responses

### ⚙️ **Settings**
- Dark/Light theme switching
- Language selection (English/Nepali)
- Update checker
- Application preferences

### ℹ️ **About**
- Application information
- Developer details
- Feedback system
- Version information

## 🎨 Design Philosophy

TechSewa combines the best of modern UI design:

- **Apple's Refined Elegance**: Smooth transitions, minimal clutter, polished aesthetics
- **Google's Material Logic**: Responsive, structured, intuitive navigation
- **Facebook's Stacked Functionality**: Powerful features with intuitive access

## 🚀 Installation

### Prerequisites
- Python 3.7 or higher
- Linux/Windows/macOS

### Quick Start

1. **Clone or download the project**
   ```bash
   git clone <repository-url>
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

### Manual Installation

If you prefer to install dependencies manually:

```bash
pip install PyQt5>=5.15.0 psutil>=5.8.0
```

## 🎯 Usage

### Getting Started
1. Launch TechSewa
2. The application opens to the Home Dashboard showing system metrics
3. Use the sidebar navigation to switch between modules
4. Explore different features and tools

### Navigation
- **Sidebar**: Click on any module icon to switch views
- **Theme Toggle**: Use Settings → Appearance to switch between Dark/Light themes
- **Language**: Change language in Settings → Language

### Key Features

#### System Monitoring
- Real-time CPU, memory, and disk usage
- Battery status (if available)
- Color-coded progress bars for quick status assessment

#### Security Tools
- **Antivirus**: Run quick or full system scans
- **Firewall**: Monitor network activity and running processes

#### AI Assistant
- Ask questions about system health, security, or general tech support
- Get contextual responses and recommendations

#### TTS Tool
- Enter text in English or Nepali
- Convert to speech and save as audio files

## 🛠️ Technical Details

### Architecture
- **Framework**: PyQt5 for cross-platform GUI
- **System Monitoring**: psutil for real-time metrics
- **Threading**: Background system monitoring
- **Theming**: Dynamic CSS-based styling

### Code Structure
```
techsewa.py
├── ThemeManager          # Theme and styling management
├── SystemMonitor        # Background system metrics
├── SidebarButton        # Custom navigation buttons
├── MetricCard          # System metric display cards
├── Module Classes      # Individual feature modules
└── TechSewaApp        # Main application window
```

### Key Classes
- `TechSewaApp`: Main application window and navigation
- `ThemeManager`: Handles dark/light theme switching
- `SystemMonitor`: Background thread for system metrics
- `HomeModule`: Dashboard with real-time system monitoring
- `AntivirusModule`: Security scanning interface
- `FirewallModule`: Network and process monitoring
- `TTSModule`: Text-to-speech functionality
- `AIAssistantModule`: Chat-based AI assistance
- `SettingsModule`: Application configuration
- `AboutModule`: Information and feedback

## 🎨 Customization

### Themes
The application supports dynamic theme switching:
- **Dark Theme**: Modern, easy on the eyes
- **Light Theme**: Clean, professional appearance

### Styling
All UI elements use CSS-based styling for consistent theming:
- Rounded corners and modern borders
- Hover effects and smooth transitions
- Color-coded status indicators

## 🔧 Development

### Adding New Modules
1. Create a new module class inheriting from `QWidget`
2. Add the module to the `Module` enum
3. Register in `TechSewaApp.setup_modules()`
4. Add navigation button in `setup_sidebar()`

### Extending Features
- **Real TTS**: Integrate with gTTS or pyttsx3
- **Actual Antivirus**: Connect to ClamAV or similar
- **AI Integration**: Connect to OpenAI API or local models
- **System Tools**: Add disk cleanup, registry editor, etc.

## 📱 System Requirements

### Minimum
- **OS**: Linux 6.12.8+, Windows 10+, macOS 10.14+
- **RAM**: 2GB
- **Storage**: 100MB free space
- **Python**: 3.7+

### Recommended
- **OS**: Latest stable release
- **RAM**: 4GB+
- **Storage**: 500MB free space
- **Python**: 3.9+

## 🤝 Contributing

### Developer Information
- **Developer**: Ayush Ojha
- **GitHub**: [flawnlawyer](https://github.com/flawnlawyer)
- **Email**: ojhaayush497@gmail.com

### Feedback
We welcome feedback and contributions! Please:
1. Report bugs via email
2. Suggest new features
3. Contribute code improvements
4. Share your experience

## 📄 License

This project is developed for educational and personal use. Please respect the developer's work and provide proper attribution.

## 🚀 Future Roadmap

### Planned Features
- [ ] Real antivirus integration (ClamAV)
- [ ] Advanced firewall rules management
- [ ] System optimization tools
- [ ] Backup and recovery features
- [ ] Multi-language support (Nepali interface)
- [ ] Plugin system for extensibility
- [ ] Cloud sync for settings
- [ ] Advanced AI capabilities

### Performance Improvements
- [ ] GPU monitoring integration
- [ ] Network traffic analysis
- [ ] Process optimization recommendations
- [ ] Memory leak detection

---

**TechSewa** - Empowering users with powerful tools in an elegant interface. 🧠✨

*Built with ❤️ by Ayush Ojha*