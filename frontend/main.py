# === System Imports and Path Setup ===
import os
import sys
from pathlib import Path

# Add parent directory to sys.path (before local imports)
sys.path.insert(0, str(Path(__file__).parent.parent))

# === External Imports ===
from PyQt5.QtWidgets import QApplication

# === Internal Imports ===
from frontend.window_manager import WindowManager

# === Utility Functions ===
def create_shortcut_with_icon():
    """Creates a desktop shortcut with an icon, without external dependencies"""
    try:
        import win32com.client  # Part of PyWin32

        # Absolute paths
        desktop = os.path.join(os.path.expanduser('~'), 'Desktop')
        shortcut_path = os.path.join(desktop, "KPIT App.lnk")
        icon_path = os.path.abspath("assets/kpit_logo.ico")
        script_path = os.path.abspath(__file__)

        shell = win32com.client.Dispatch("WScript.Shell")
        shortcut = shell.CreateShortCut(shortcut_path)
        shortcut.TargetPath = sys.executable
        shortcut.Arguments = f'"{script_path}"'
        shortcut.WorkingDirectory = os.path.dirname(script_path)
        shortcut.IconLocation = icon_path
        shortcut.WindowStyle = 1  # 7 = Minimized, 1 = Normal
        shortcut.save()

        print("Shortcut successfully created on desktop")
        return True
    except ImportError:
        print("Warning: pywin32 not installed, cannot create desktop shortcut")
        return False
    except Exception as e:
        print(f"Shortcut creation error: {str(e)}")
        return False

# === Main Application Entry Point ===
def main():
    # Hide console immediately (Windows only)
    if sys.platform == "win32":
        import ctypes
        ctypes.windll.user32.ShowWindow(ctypes.windll.kernel32.GetConsoleWindow(), 0)

    # Create shortcut on first launch
    shortcut_path = os.path.join(os.path.expanduser('~'), 'Desktop', "KPIT App.lnk")
    if not os.path.exists(shortcut_path):
        create_shortcut_with_icon()

    # Initialize Qt application
    app = QApplication(sys.argv)

    # Load CSS style
    css_path = os.path.join(os.path.dirname(__file__), "assets", "styles.qss")
    if os.path.exists(css_path):
        with open(css_path, "r", encoding='utf-8') as f:
            app.setStyleSheet(f.read())

    # Use WindowManager to show login window
    window_manager = WindowManager()
    window_manager.show_login_window()

    sys.exit(app.exec_())

# === Script Execution ===
if __name__ == "__main__":
    # Check and convert icon if needed
    icon_path = os.path.join("assets", "kpit_logo.ico")
    if not os.path.exists(icon_path):
        try:
            from PIL import Image
            img = Image.open("assets/kpit_logo.png")
            img.save(icon_path, format='ICO')
            print("Icon successfully converted to .ico")
        except Exception as e:
            print(f"Icon conversion error: {str(e)}")

    main()
