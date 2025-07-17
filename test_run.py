"""
Test runner for CaseClipSaver - bypasses instance check for testing
"""
import sys
import os

# Add src directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from config import Config
from file_manager import FileManager
from clipboard_monitor import ClipboardMonitor
from tray_ui import TrayUI

def test_app():
    """Run the application for testing"""
    print("=" * 50)
    print("CaseClipSaver v1.0.0 - TEST MODE")
    print("Clipboard Monitor for Case Review Data")
    print("=" * 50)
    
    try:
        # Initialize components
        print("Initializing components...")
        config = Config()
        file_manager = FileManager(config)
        clipboard_monitor = ClipboardMonitor(config, file_manager)
        tray_ui = TrayUI(config, clipboard_monitor, file_manager)
        
        print(f"✓ Output directory: {config.output_directory}")
        print("✓ Components initialized successfully")
        print("")
        print("🎯 Application is running!")
        print("📋 Look for the clipboard icon in your system tray")
        print("📁 Files will be saved to: C:\\casedata\\")
        print("")
        print("📝 Test with this sample data:")
        print("   ICM 635658889 - Critical production incident")
        print("   Support Request Number: 2505160020000588")
        print("")
        print("🖱️  Right-click tray icon for menu options:")
        print("   • Turn ON/OFF - Toggle monitoring")
        print("   • Test Clipboard - Check current clipboard")
        print("   • Status - View current status")
        print("   • Exit - Close application")
        print("")
        print("Press Ctrl+C to stop...")
        
        # Start the tray UI (this will block)
        tray_ui.start()
        
    except KeyboardInterrupt:
        print("\n👋 Application stopped by user")
    except Exception as e:
        print(f"\n❌ Error: {e}")

if __name__ == "__main__":
    test_app()
