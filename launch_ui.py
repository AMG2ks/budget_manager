#!/usr/bin/env python3
"""
Smart Budget Manager - Web UI Launcher
Simple launcher script for the Streamlit web interface.
"""

import sys
import subprocess
import os
from pathlib import Path

def check_dependencies():
    """Check if required dependencies are installed."""
    try:
        import streamlit
        import plotly
        import pandas
        return True
    except ImportError as e:
        print(f"❌ Missing dependency: {e}")
        print("Please install dependencies with: pip install -r requirements.txt")
        return False

def check_app_file():
    """Check if app.py exists."""
    app_path = Path("app.py")
    if not app_path.exists():
        print("❌ app.py not found in current directory")
        print("Please run this script from the budget_manager root directory")
        return False
    return True

def launch_ui():
    """Launch the Streamlit web interface."""
    print("🚀 Launching Smart Budget Manager Web Interface...")
    print("📱 The web app will open in your default browser")
    print("🔧 Press Ctrl+C to stop the server")
    print("")
    
    try:
        # Launch Streamlit
        subprocess.run([
            sys.executable, "-m", "streamlit", "run", "app.py",
            "--theme.base", "light",
            "--theme.primaryColor", "#1f77b4",
            "--theme.backgroundColor", "#ffffff",
            "--theme.secondaryBackgroundColor", "#f0f2f6"
        ])
    except KeyboardInterrupt:
        print("\n👋 Thanks for using Smart Budget Manager!")
    except Exception as e:
        print(f"❌ Error launching web interface: {e}")
        print("Try running manually: streamlit run app.py")

def main():
    """Main launcher function."""
    print("💰 Smart Budget Manager - Web Interface Launcher")
    print("=" * 50)
    
    # Check if we're in the right directory
    if not check_app_file():
        return 1
    
    # Check dependencies
    if not check_dependencies():
        return 1
    
    # Launch the UI
    launch_ui()
    return 0

if __name__ == "__main__":
    sys.exit(main()) 