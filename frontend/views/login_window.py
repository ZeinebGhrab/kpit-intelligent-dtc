import os
from PyQt5.QtCore import Qt, QPropertyAnimation, QEasingCurve
from PyQt5.QtGui import QPixmap, QIcon
from PyQt5.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QLineEdit, QPushButton, QFrame, QCheckBox, QDialog, QMessageBox
)
from server.supabase_config import supabase_config

base_dir = os.path.dirname(os.path.abspath(__file__))

class ResetPasswordDialog(QDialog):

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Password Reset")
        self.setWindowModality(Qt.ApplicationModal)
        self.setFixedSize(450, 350)
        self.setStyleSheet("""
            QDialog {
                background-color: #2d2d2d;
                color: #e0e0e0;
            }
            QLabel {
                color: #e0e0e0;
            }
            QLineEdit {
                background-color: #3d3d3d;
                color: white;
                border: 1px solid #43a047;
                border-radius: 4px;
                padding: 8px;
            }
            QPushButton {
                background-color: #43a047;
                color: white;
                padding: 8px;
                border: none;
                border-radius: 4px;
                min-width: 80px;
            }
            QPushButton:hover {
                background-color: #2e7d32;
            }
        """)

        layout = QVBoxLayout()
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(15)

        # Title
        title_label = QLabel("Password Reset")
        title_label.setStyleSheet("font-size: 18px; font-weight: bold; margin-bottom: 10px;")
        title_label.setAlignment(Qt.AlignCenter)

        # Message
        info_label = QLabel("Enter your email to receive a password reset link :")
        info_label.setWordWrap(True)

        # Email field
        self.email_input = QLineEdit()
        self.email_input.setPlaceholderText("your.email@kpit.com")

       # Buttons
        buttons_layout = QHBoxLayout()
        cancel_btn = QPushButton("Cancel")
        send_btn = QPushButton("Send Link")

        cancel_btn.setObjectName("cancelBtn")
        send_btn.setObjectName("sendBtn")

        buttons_layout.addWidget(cancel_btn)
        buttons_layout.addWidget(send_btn)

        send_btn.setFixedSize(150, 40)
        cancel_btn.setFixedSize(150, 40)
        
        self.setStyleSheet("""
    QDialog {
        background-color: #2d2d2d;
        color: #e0e0e0;
    }
    QLabel {
        color: #e0e0e0;
    }
    QLineEdit {
        background-color: #3d3d3d;
        color: white;
        border: 1px solid #43a047;
        border-radius: 4px;
        padding: 8px;
    }
    QPushButton#sendBtn {
        background-color: #43a047;
        color: white;
        padding: 8px;
        border: none;
        border-radius: 4px;
        min-width: 150px;
        min-height: 40px;
        font-weight: bold;
        margin-top:20px;
    }
    QPushButton#sendBtn:hover {
        background-color: #2e7d32;
    }
    QPushButton#cancelBtn {
        background-color: #FF0000;
        color: white;
        padding: 8px;
        border: none;
        border-radius: 4px;
        min-width: 150px;
        min-height: 40px;
        font-weight: bold;
        margin-top:20px;
    }
    QPushButton#cancelBtn:hover {
        background-color: #d32f2f;
    }
""")


        # Add to layout
        layout.addWidget(title_label)
        layout.addWidget(info_label)
        layout.addWidget(self.email_input)
        layout.addLayout(buttons_layout)
       
        self.status_label = QLabel()
        self.status_label.setWordWrap(True)
        self.status_label.hide()  
        layout.addWidget(self.status_label)
        layout.addStretch()

        self.setLayout(layout)

        # Connections
        cancel_btn.clicked.connect(self.reject)
        send_btn.clicked.connect(self.send_reset_email)

   
   #------- Function to reset password -----------

    def send_reset_email(self):
        email = self.email_input.text().strip()

        if not "@" in email or "." not in email:
            self.show_status("Please enter a valid email address", "error")
            return

        try:
            # Get Supabase client from parent window
            parent_window = self.parent()
            if not hasattr(parent_window, 'supabase') or not parent_window.supabase:
                self.show_status("Database connection not available", "error")
                return

            # Check if Flask server is running
            import requests
            try:
                response = requests.get("http://localhost:8000", timeout=2)
                server_running = True
            except:
                server_running = False

            if not server_running:
                self.show_status("Flask server not running! Please start 'python redirect_server.py' first.", "error")
                return

            # Use Supabase password reset with correct redirect URL
            response = parent_window.supabase.auth.reset_password_email(
                email,
                options={
                    "redirect_to": "http://localhost:8000/reset-password"
                }
            )

            self.show_status(
                "Password reset link sent!\n\n"
                "Check your email and click the reset link.\n"
                "The link will open in your web browser.",
                "success"
            )
            print(f"Password reset email sent to: {email}")

        except Exception as e:
            error_msg = str(e).lower()
            if "user not found" in error_msg or "email not found" in error_msg:
                # For security, don't reveal if email exists or not
                self.show_status("If this email is registered, you will receive a reset link.", "success")
            else:
                self.show_status(f"Error: {str(e)}", "error")
            print(f" Password reset error: {e}")

    def show_status(self, message, type="info"):
        self.status_label.setText(message)
        color = "#43a047" if type == "success" else "#f44336" if type == "error" else "#2196f3"
        self.status_label.setStyleSheet(f"color: {color}; padding: 10px; background-color: #3d3d3d; border-radius: 4px;")
        self.status_label.show()
        
class LoginWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("KPIT - Login")
        self.setMinimumSize(800, 600)
        self.setWindowIcon(QIcon(os.path.join(base_dir, "../assets/kpit_logo.png")))
        

        # Initialize attributes
        self.window_manager = None
        self.ignore_close_event = False
        self.supabase = None

        # Initialize Supabase with enhanced error handling
        self.initialize_supabase()

        # Widget central
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        # Layout principal
        main_layout = QHBoxLayout(central_widget)
        main_layout.setContentsMargins(0, 0, 0, 0)

        # Left section (logo)
        left_frame = QFrame()
        left_frame.setObjectName("leftFrame")
        left_layout = QVBoxLayout(left_frame)

        # KPIT logo centered
        logo_label = QLabel()
        try:
            logo_path = os.path.join(base_dir, "../assets/kpit_logo.png")
            logo_pixmap = QPixmap(logo_path)
            print("Pixmap loaded:", not logo_pixmap.isNull())

            logo_label.setPixmap(logo_pixmap)
        except:
            logo_label.setText("KPIT")
        logo_label.setAlignment(Qt.AlignCenter)

        left_layout.addStretch()
        left_layout.addWidget(logo_label)
        left_layout.addStretch()

        # Right section (form)
        right_frame = QFrame()
        right_frame.setObjectName("rightFrame")
        right_layout = QVBoxLayout(right_frame)
        right_layout.setContentsMargins(50, 80, 50, 80)

        # Title
        title_label = QLabel("LOGIN")
        title_label.setObjectName("titleLabel")
        title_label.setAlignment(Qt.AlignCenter)
        title_label.setStyleSheet("""
            font-size: 45px;
            font-weight: bold;
            color: #43a047;
            margin-bottom: 20px;
        """)

        # Email field
        email_label = QLabel("Email:")
        email_label.setStyleSheet ("""
            font-weight: bold;  
            """)
        self.email_input = QLineEdit()
        self.email_input.setPlaceholderText("your.email@kpit.com")

        # Password field
        password_label = QLabel("Password:")
        password_label.setStyleSheet("""
            font-weight: bold;  
            """)
        self.password_input = QLineEdit()
        self.password_input.setEchoMode(QLineEdit.Password)
        self.password_input.setPlaceholderText("Enter your password")

        self.forgot_label = QLabel(
            "<a href='#' style='color:#43a047;font-weight: bold;margin-bottom: 6px;'>Forgot password ?</a>"
        )
        
        # Green style with hover effect
        self.forgot_label.setStyleSheet("""
            QLabel:hover {
            color: #90EE90;  
            }
            """)
        
         # Options
        options_layout = QVBoxLayout()
        options_layout.addWidget(self.forgot_label)
        

        # Login Button
        login_btn = QPushButton("Login")
        login_btn.setObjectName("loginBtn")

        # Inscription Link
        signup_label = QLabel("<a href='#' style='color:#43a047;font-weight: bold;'>Create a KPIT account</a>")
        signup_label.setAlignment(Qt.AlignCenter)
        signup_label.setStyleSheet("""
            QLabel:hover {
            color: #90EE90;  
            }
            """)

        # Added to layout
        right_layout.addWidget(title_label)
        right_layout.addSpacing(30)
        right_layout.addWidget(email_label)
        right_layout.addWidget(self.email_input)
        right_layout.addSpacing(15)
        right_layout.addWidget(password_label)
        right_layout.addWidget(self.password_input)
        right_layout.addSpacing(10)
        right_layout.addLayout(options_layout)
        right_layout.addSpacing(20)
        right_layout.addWidget(login_btn)
        right_layout.addSpacing(15)
        right_layout.addWidget(signup_label)
        right_layout.addStretch()

        # Added sections
        main_layout.addWidget(left_frame, 1)
        main_layout.addWidget(right_frame, 1)

        # Animation
        self.animate_ui()

        # Signal connections
        signup_label.linkActivated.connect(self.show_signup_window)
        self.forgot_label.linkActivated.connect(self.show_reset_dialog)
        login_btn.clicked.connect(self.attempt_login)

    def initialize_supabase(self):
        """Initialize Supabase with better error handling"""
        try:
            if not supabase_config.is_configured():
                print("Supabase not configured - missing environment variables")
                self.supabase = None
                return

            self.supabase = supabase_config.get_client()
            print("Supabase initialized successfully in LoginWindow")
        except Exception as e:
            print(f"Error initializing Supabase: {e}")
            self.supabase = None

    def animate_ui(self):
        for widget in [self.email_input, self.password_input]:
            animation = QPropertyAnimation(widget, b"pos")
            animation.setDuration(800)
            animation.setEasingCurve(QEasingCurve.OutBack)
            start_pos = widget.pos()
            widget.move(start_pos.x() + 100, start_pos.y())
            animation.setEndValue(start_pos)
            animation.start()

    def show_signup_window(self):
        if self.window_manager:
            self.window_manager.show_signup_window()
        else:
            from signup_window import SignupWindow
            self.hide()
            self.signup_window = SignupWindow()
            self.signup_window.show()

    def show_reset_dialog(self):
        self.reset_dialog = ResetPasswordDialog(self)
        self.reset_dialog.exec_()

    def attempt_login(self):
        email = self.email_input.text().strip()
        password = self.password_input.text()

        if not email or not password:
            self.show_error("Please fill in all fields")
            return

        # Check if Supabase is initialized
        if not self.supabase:
            self.show_error(
                "Configuration Error",
                "Database connection not configured.\n\n"
                "Please check that you have:\n"
                "1. Created a .env file in your project directory\n"
                "2. Added SUPABASE_URL and SUPABASE_ANON_KEY variables\n"
                "3. Installed the supabase package: pip install supabase\n\n"
                "Example .env file:\n"
                "SUPABASE_URL=https://your-project.supabase.co\n"
                "SUPABASE_ANON_KEY=your-anon-key"
            )
            return

        try:
            response = self.supabase.auth.sign_in_with_password({
                "email": email,
                "password": password
            })
            
            print(f"User ID after auth: {response.user.id}")

            user_profile_response = self.supabase.table('user_profiles') .select('*') .eq('email', email) .maybe_single().execute()

            if user_profile_response.data:
                user_profile = user_profile_response.data
                user_status = user_profile.get('status', 'pending_approval')

                if user_status == 'pending_approval':
                    self.show_warning(
                        "Account Pending Approval",
                        f"Your account has not been approved by the administrator yet.\n\n"
                        f"The admin has been notified when you registered.\n"
                        f"You will receive a confirmation email at {email} once your account is activated."
                    )
                    self.supabase.auth.sign_out()
                    return
                elif user_status == 'rejected':
                    self.show_error(
                        "Account Rejected",
                        "Your registration request has been rejected by the administrator.\n"
                        "Please contact the admin for more information."
                    )
                    self.supabase.auth.sign_out()
                    return
                elif user_status != 'approved':
                    self.show_warning(
                        "Unknown Account Status",
                        "Your account status is unclear. Please contact the administrator."
                    )
                    self.supabase.auth.sign_out()
                    return
            else:
                self.show_error(
                    "Profile Not Found",
                    "No profile associated with this account. Please contact the administrator."
                )
                self.supabase.auth.sign_out()
                return

            first_name = user_profile.get('prenom', 'User')
            self.show_success(f"Welcome {first_name}!", "You are now logged in to KPIT.")

            user_data = {
                'user': response.user,
                'profile': user_profile
            }

            self.ignore_close_event = True

            if self.window_manager:
                self.hide()
                self.window_manager.show_principal_window(user_data)
            else:
                from principal_window import PrincipalWindow
                self.hide()
                self.principal_window = PrincipalWindow()
                self.principal_window.set_user_data(user_data)
                self.principal_window.show()

        except Exception as e:
            error_msg = str(e).lower()

            if "invalid login credentials" in error_msg:
                self.show_error("Invalid Credentials", "Email or password is incorrect.")
            elif "email not confirmed" in error_msg:
                self.show_warning(
                    "Email Not Verified",
                    "Please verify your email address before logging in."
                )
            else:
                self.show_error(
                    "Login Error",
                    f"A technical error occurred:\n{str(e)}"
                )

    def show_error(self, title, message=None):
        if message is None:
            message = title
            title = "Error"
        QMessageBox.critical(self, title, message)

    def show_warning(self, title, message):
        QMessageBox.warning(self, title, message)

    def show_success(self, title, message):
        QMessageBox.information(self, title, message)

    def closeEvent(self, event):
        if getattr(self, 'ignore_close_event', False):
            event.accept()
            return
        """Handle window closing with exactly 2 buttons"""
        msg_box = QMessageBox(self)
        msg_box.setWindowTitle("Quit Application")
        msg_box.setText("Are you sure you want to quit?")
        msg_box.setIcon(QMessageBox.Question)

        msg_box.setStyleSheet("""
        QMessageBox {
            background-color: #2d2d2d;
            color: #e0e0e0;
            font-size: 14px;
        }
        QLabel {
            color: #ffffff;
            font-size: 18px;
            font-weight: bold;
            padding: 10px;
        }
        """)

        # Add two buttons: Yes and No
        yes_button = msg_box.addButton("Yes", QMessageBox.AcceptRole)
        no_button = msg_box.addButton("No", QMessageBox.RejectRole)
        

        # Custom styles on each button
        yes_button.setStyleSheet("""
        QPushButton {
            background-color: #2e7d32;
            color: white;
            padding: 6px 12px;
            border-radius: 4px;
            font-weight: bold;
        }
        QPushButton:hover {
            background-color: #1b5e20;
        }
        """)

        no_button.setStyleSheet("""
        QPushButton {
            background-color: #c62828;
            color: white;
            padding: 6px 12px;
            border-radius: 4px;
            font-weight: bold;
        }
        QPushButton:hover {
            background-color: #8e0000;
        }
        """)

        msg_box.setDefaultButton(no_button)  # Set "No" as the default button
        msg_box.exec_()

        if msg_box.clickedButton() == yes_button:
            if hasattr(self, 'window_manager') and self.window_manager:
                self.window_manager.quit_application()
            event.accept()
        else:
            event.ignore()

if __name__ == "__main__":
    import sys
    from PyQt5.QtWidgets import QApplication

    app = QApplication(sys.argv)

    # Basic style
    app.setStyleSheet("""
        #titleLabel {
            font-size: 24px;
            font-weight: bold;
            color: #2c3e50;
        }
        QLineEdit {
            padding: 10px;
            border: 1px solid #bdc3c7;
            border-radius: 4px;
        }
        #loginBtn {
            background-color: #3498db;
            color: white;
            padding: 12px;
            border: none;
            border-radius: 4px;
            font-weight: bold;
        }
        #loginBtn:hover {
            background-color: #2980b9;
        }
        QLabel[href] {
            color: #3498db;
            text-decoration: underline;
        }
        #leftFrame {
            background-color: #f8f9fa;
        }
        #rightFrame {
            background-color: white;
        }
    """)

    window = LoginWindow()
    window.show()
    sys.exit(app.exec_())