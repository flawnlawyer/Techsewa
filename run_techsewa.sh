#!/bin/bash

# TechSewa Launcher Script
# This script launches the TechSewa application with proper error handling

echo "🧠 Starting TechSewa - System Utility & AI Assistant..."
echo "=================================================="

# Check if Python 3 is available
if ! command -v python3 &> /dev/null; then
    echo "❌ Error: Python 3 is not installed or not in PATH"
    echo "Please install Python 3.7 or higher"
    exit 1
fi

# Check if required packages are installed
echo "🔍 Checking dependencies..."

python3 -c "import PyQt5" 2>/dev/null
if [ $? -ne 0 ]; then
    echo "❌ Error: PyQt5 is not installed"
    echo "Installing PyQt5..."
    pip3 install --break-system-packages PyQt5
fi

python3 -c "import psutil" 2>/dev/null
if [ $? -ne 0 ]; then
    echo "❌ Error: psutil is not installed"
    echo "Installing psutil..."
    pip3 install --break-system-packages psutil
fi

echo "✅ Dependencies check completed"

# Check if the main script exists
if [ ! -f "techsewa.py" ]; then
    echo "❌ Error: techsewa.py not found in current directory"
    echo "Please run this script from the TechSewa directory"
    exit 1
fi

echo "🚀 Launching TechSewa..."
echo ""

# Launch the application
python3 techsewa.py

# Check if the application exited with an error
if [ $? -ne 0 ]; then
    echo ""
    echo "❌ TechSewa encountered an error"
    echo "Please check the error messages above"
    echo ""
    echo "Troubleshooting tips:"
    echo "1. Make sure all dependencies are installed"
    echo "2. Check if you have a display server running (X11/Wayland)"
    echo "3. Try running: pip3 install --break-system-packages PyQt5 psutil"
    exit 1
fi

echo ""
echo "👋 TechSewa has been closed"