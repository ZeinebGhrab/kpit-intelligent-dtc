# === PyQt Imports ===
from PyQt5.QtWidgets import QApplication
from PyQt5.QtCore import QObject

# === View Imports ===
from frontend.views.login_window import LoginWindow
from frontend.views.signup_window import SignupWindow
from frontend.views.principal_window import PrincipalWindow

class WindowManager(QObject):
    """Central manager for all application windows"""

    def __init__(self):
        super().__init__()
        self.current_window = None
        self.user_data = None

    # === Window Display Methods ===

    def show_signup_window(self):
        """Display the signup window"""
        if self.current_window:
            self.current_window.hide()
        self.current_window = SignupWindow()
        self.current_window.window_manager = self
        self.current_window.show()

    def show_login_window(self):
        """Display the login window"""
        if self.current_window:
            self.current_window.hide()
        self.current_window = LoginWindow()
        self.current_window.window_manager = self
        self.current_window.show()

    def show_principal_window(self, user_data=None):
        """Display the main window after successful login"""
        self.user_data = user_data

        # Close the previous window cleanly
        if self.current_window:
            self.current_window.close()

        # Create and show the new window
        self.principal_window = PrincipalWindow()
        self.principal_window.window_manager = self
        if user_data:
            self.principal_window.set_user_data(user_data)
        self.principal_window.show()

        # Update current window reference
        self.current_window = self.principal_window

    # === Session Control ===

    def logout(self):
        """Log out and return to the login window"""
        self.user_data = None
        self.show_login_window()

    # === Window Lifecycle ===

    def close_current_window(self):
        """Close the currently active window"""
        if self.current_window:
            self.current_window.close()
            self.current_window = None

    def quit_application(self):
        """Exit the entire application"""
        if self.current_window:
            self.current_window.close()
        QApplication.quit()
