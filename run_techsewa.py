#!/usr/bin/env python3
"""
TechSewa Launcher Script
This script provides instructions and launches the TechSewa application.
"""

import sys
import os

def print_banner():
    """Print the TechSewa banner"""
    print("""
╔══════════════════════════════════════════════════════════════════╗
║                            TechSewa                              ║
║                  Digital Assistant & System Utility              ║
║                                                                  ║
║     A powerful desktop application with elegant PyQt5 UI        ║
║                                                                  ║
║     Developer: Ayush Ojha                                       ║
║     GitHub: flawnlawyer                                         ║
║     Email: ojhaayush497@gmail.com                               ║
╚══════════════════════════════════════════════════════════════════╝
    """)

def check_dependencies():
    """Check if all required dependencies are available"""
    try:
        import PyQt5.QtWidgets
        import psutil
        print("✅ All dependencies are installed successfully!")
        return True
    except ImportError as e:
        print(f"❌ Missing dependency: {e}")
        print("Please install required packages:")
        print("pip install PyQt5>=5.15.0 psutil>=5.8.0")
        return False

def main():
    """Main launcher function"""
    print_banner()
    
    if not check_dependencies():
        sys.exit(1)
    
    print("\n🚀 Launching TechSewa...")
    print("\nFeatures:")
    print("• 🏠 Real-time System Dashboard with live stats")
    print("• 🛡️ Antivirus scanning capabilities")
    print("• 🔥 Firewall management interface")
    print("• 🗣️ Text-to-Speech tool (English/नेपाली)")
    print("• 🤖 AI Assistant for system help")
    print("• ⚙️ Customizable settings (Light/Dark themes)")
    print("• ℹ️ About section with developer info")
    
    print("\n📋 System Requirements:")
    print("• Python 3.7+")
    print("• PyQt5 5.15.0+")
    print("• psutil 5.8.0+")
    print("• Display server (X11/Wayland) for GUI")
    
    print("\n🎯 Usage Instructions:")
    print("1. Use the sidebar to navigate between modules")
    print("2. Toggle theme with the moon/sun button")
    print("3. Switch language between English and नेपाली")
    print("4. Monitor real-time system stats on the dashboard")
    print("5. Use the search bar to find specific features")
    
    # Try to launch the application
    try:
        print("\n🌟 Starting TechSewa application...")
        import techsewa
        techsewa.main()
    except Exception as e:
        print(f"\n❌ Error launching application: {e}")
        print("\n💡 Troubleshooting tips:")
        print("• Ensure you have a display server running (X11/Wayland)")
        print("• Try running with: DISPLAY=:0 python3 run_techsewa.py")
        print("• For headless systems, use: xvfb-run python3 run_techsewa.py")
        print("• Check that all dependencies are properly installed")
        sys.exit(1)

if __name__ == "__main__":
    main()