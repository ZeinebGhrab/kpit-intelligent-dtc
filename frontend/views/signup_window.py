import re
from dotenv import load_dotenv
import os
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from PyQt5.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QLineEdit, QPushButton, QFrame, QSizePolicy, QScrollArea,
    QCheckBox, QDialog, QDialogButtonBox, QTextBrowser, QMessageBox
)
from PyQt5.QtGui import QPixmap, QIcon, QTextCursor
from PyQt5.QtCore import Qt, QPropertyAnimation, QEasingCurve

from server.supabase_config import supabase_config

base_dir = os.path.dirname(os.path.abspath(__file__))
load_dotenv()
DEFAULT_ADMIN_EMAIL = os.getenv("GMAIL_USER")

class TermsDialog(QDialog):

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Terms of Use and Privacy Policy")
        self.setMinimumSize(600, 500)

        # Style configuration
        self.setStyleSheet("""
            QDialog {
                background-color: white;
            }
            QTextBrowser {
                background-color: white;
                color: black;
                font-size: 12px;
                border: none;
            }
            QScrollBar:vertical {
                border: none;
                background: #f1f1f1;
                width: 10px;
                margin: 0px 0px 0px 0px;
            }
            QScrollBar::handle:vertical {
                background: #888;
                min-height: 20px;
                border-radius: 4px;
            }
            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
                height: 0px;
            }
        """)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)

        text_browser = QTextBrowser()
        text_browser.setOpenExternalLinks(True)

        terms_text = """
<h1 style='color: black;'>Terms and Conditions</h1>
<p style='color: black;'><strong>Last updated: July 20, 2025</strong></p>

<h2 style='color: black;'>1. Acceptance of Terms</h2>
<p style='color: black;'>By using KPIT's services, you agree to these Terms and Conditions and our Privacy Policy.</p>

<h2 style='color: black;'>2. User Account</h2>
<p style='color: black;'>2.1 You must provide accurate and complete information when creating your account.<br>
2.2 You are responsible for maintaining the confidentiality of your login credentials.</p>

<h2 style='color: black;'>3. Intellectual Property</h2>
<p style='color: black;'>All KPIT content, trademarks, and logos are protected by intellectual property rights.</p>

<h2 style='color: black;'>4. Liability Limitations</h2>
<p style='color: black;'>KPIT shall not be liable for any indirect damages resulting from the use of the service.</p>

<h1 style='color: black;'>Privacy Policy</h1>

<h2 style='color: black;'>1. Collected Data</h2>
<p style='color: black;'>We collect the following data:<br>
- Personal information (name, surname, email)<br>
- Login data<br>
- Service usage data</p>

<h2 style='color: black;'>2. Data Usage</h2>
<p style='color: black;'>Your data is used to:<br>
- Provide and improve our services<br>
- Personalize your experience<br>
- Communicate with you</p>

<h2 style='color: black;'>3. Data Protection</h2>
<p style='color: black;'>We implement appropriate technical and organizational security measures to protect your data.</p>

<h2 style='color: black;'>4. Data Sharing</h2>
<p style='color: black;'>Your data will not be sold to third parties. It may be shared with:<br>
- Service providers necessary for service operation<br>
- Legal authorities when required by law</p>

<h2 style='color: black;'>5. Your Rights</h2>
<p style='color: black;'>Under GDPR, you have the right to:<br>
- Access and rectify your data<br>
- Request data deletion<br>
- Data portability<br>
- Object to data processing</p>
"""
        text_browser.setHtml(terms_text)
        text_browser.moveCursor(QTextCursor.Start)

        button_box = QDialogButtonBox(QDialogButtonBox.Ok)
        button_box.accepted.connect(self.accept)

        layout.addWidget(text_browser)
        layout.addWidget(button_box)


class SignupWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("KPIT - Account creation")
        self.setMinimumSize(800, 600)
        self.setWindowIcon(QIcon(os.path.join(base_dir, "../assets/kpit_logo.png")))

        # Initialize window_manager
        self.window_manager = None

        # Initialize Supabase FIRST
        self.initialize_supabase()

        # Widget principal
        main_widget = QWidget()
        self.setCentralWidget(main_widget)
        main_layout = QHBoxLayout(main_widget)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        # Left section (logo)
        left_frame = QFrame()
        left_frame.setObjectName("leftFrame")
        left_frame.setFixedWidth(350)
        left_layout = QVBoxLayout(left_frame)
        left_layout.setContentsMargins(0, 0, 0, 0)

        logo_container = QWidget()
        logo_container_layout = QVBoxLayout(logo_container)
        logo_container_layout.setContentsMargins(20, 20, 20, 20)

        logo_label = QLabel()
        try:
            logo_path = os.path.join(base_dir, "../assets/kpit_logo.png")
            logo_pixmap = QPixmap(logo_path)
            logo_label.setPixmap(logo_pixmap)
        except:
            logo_label.setText("KPIT")
        logo_label.setAlignment(Qt.AlignCenter)

        logo_container_layout.addStretch()
        logo_container_layout.addWidget(logo_label)
        logo_container_layout.addStretch()

        left_layout.addWidget(logo_container)

        # Right section (form)
        right_scroll = QScrollArea()
        right_scroll.setWidgetResizable(True)
        right_scroll.setFrameShape(QFrame.NoFrame)

        right_frame = QFrame()
        right_frame.setObjectName("rightFrame")
        right_scroll.setWidget(right_frame)

        right_layout = QVBoxLayout(right_frame)
        right_layout.setContentsMargins(60, 60, 60, 60)
        right_layout.setSpacing(20)

        title_label = QLabel("Sign In")
        title_label.setObjectName("titleLabel")
        title_label.setAlignment(Qt.AlignCenter)
        title_label.setStyleSheet("""
            font-size: 45px;
            font-weight: bold;
            color: #43a047;
            margin-bottom: 20px;
        """)

        def create_field(label_text, placeholder, is_password=False):
            label = QLabel(label_text)
            field = QLineEdit()
            field.setPlaceholderText(placeholder)
            if is_password:
                field.setEchoMode(QLineEdit.Password)
            field.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
            field.setMinimumHeight(40)
            return label, field

        firstname_label, self.firstname_input = create_field("First Name:", "Your first name")
        firstname_label.setStyleSheet("""
            font-weight: bold;  
            """)
        lastname_label, self.lastname_input = create_field("Last Name:", "Your last name")
        lastname_label.setStyleSheet("""
            font-weight: bold;  
            """)
        email_label, self.email_input = create_field("Email:", "your.email@kpit.com")
        email_label.setStyleSheet("""
            font-weight: bold;  
            """)
        password_label, self.password_input = create_field("Password:", "Create a password", True)
        password_label.setStyleSheet("""
            font-weight: bold;  
            """)
        confirm_password_label, self.confirm_password_input = create_field("Confirm password:", "Confirm your password", True)
        confirm_password_label.setStyleSheet("""
            font-weight: bold;  
            """)
        terms_container = QWidget()
        terms_layout = QHBoxLayout(terms_container)
        terms_layout.setContentsMargins(0, 0, 0, 0)

        self.terms_check = QCheckBox()
        terms_label = QLabel(
        'I accept the <a href="#" style="color:#43a047">Terms and Conditions</a>'
        )
        terms_label.setStyleSheet("""
            QLabel {
            font-weight: bold;  
            }
            """)
        terms_label.setOpenExternalLinks(False)
        terms_label.linkActivated.connect(self.show_terms_dialog)

        terms_layout.addWidget(self.terms_check)
        terms_layout.addWidget(terms_label)
        terms_layout.addStretch()

     

        self.signup_btn = QPushButton("Sign in")
        self.signup_btn.setObjectName("loginBtn")
        self.signup_btn.clicked.connect(self.attempt_signup)

        login_label = QLabel("<a href='#' style='color:#43a047; font-weight:bold;'>Already have an account ? Login</a>")
        login_label.setProperty("link", "true")
        login_label.setAlignment(Qt.AlignCenter)
        login_label.setOpenExternalLinks(False)

        right_layout.addWidget(title_label)
        right_layout.addSpacing(20)

        for label, field in [
            (firstname_label, self.firstname_input),
            (lastname_label, self.lastname_input),
            (email_label, self.email_input),
            (password_label, self.password_input),
            (confirm_password_label, self.confirm_password_input)
        ]:
            right_layout.addWidget(label)
            right_layout.addWidget(field)

        right_layout.addWidget(terms_container)
        right_layout.addSpacing(20)
        right_layout.addWidget(self.signup_btn)
        right_layout.addWidget(login_label)
        right_layout.addStretch()

        main_layout.addWidget(left_frame)
        main_layout.addWidget(right_scroll)

        self.animate_ui()
        login_label.linkActivated.connect(self.show_login_window)

    def initialize_supabase(self):
        """Initialize Supabase client"""
        try:
            if not supabase_config.is_configured():
                print("Supabase not configured - missing environment variables")
                self.supabase = None
                return

            self.supabase = supabase_config.get_client()
            print("Supabase initialized successfully in SignupWindow")
        except Exception as e:
            print(f"Error initializing Supabase in SignupWindow: {e}")
            self.supabase = None

    def show_terms_dialog(self):
        dialog = TermsDialog(self)
        dialog.setModal(True)
        dialog_width = min(self.width() - 100, 800)
        dialog_height = min(self.height() - 100, 600)
        dialog.resize(dialog_width, dialog_height)
        parent_rect = self.frameGeometry()
        dialog.move(parent_rect.center() - dialog.rect().center())
        dialog.exec_()

    def animate_ui(self):
        for widget in [self.firstname_input, self.lastname_input, self.email_input,
                       self.password_input, self.confirm_password_input]:
            animation = QPropertyAnimation(widget, b"pos")
            animation.setDuration(800)
            animation.setEasingCurve(QEasingCurve.OutBack)
            start_pos = widget.pos()
            widget.move(start_pos.x() + 100, start_pos.y())
            animation.setEndValue(start_pos)
            animation.start()

    def validate_password(self, password):
        """Validate password strength"""
        if len(password) < 8:
            return False, "The password must contain at least 8 characters."
        if not re.search(r"[A-Z]", password):
            return False, "The password must contain at least one uppercase letter."
        if not re.search(r"[a-z]", password):
            return False, "The password must contain at least one lowercase letter."
        if not re.search(r"[0-9]", password):
            return False, "The password must include at least one number."
        if not re.search(r"[!@#$%^&*(),.?\":{}|<>]", password):
            return False, "The password must include at least one special character."
        return True, ""

    def validate_and_submit(self):
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

        # Récupération des données
        email = self.email_input.text().strip()
        password = self.password_input.text()
        confirm = self.confirm_password_input.text()
        firstname = self.firstname_input.text().strip()
        lastname = self.lastname_input.text().strip()

        # Validations
        if not all([email, password, confirm, firstname, lastname]):
            self.show_error("Error", "Please fill in all required fields.")
            return

        if not re.match(r"[^@]+@[^@]+\.[^@]+", email):
            self.show_error("Error", "Please enter a valid email address.")
            return

        if password != confirm:
            self.show_error("Error", "The passwords do not match.")
            return

        is_valid, msg = self.validate_password(password)
        if not is_valid:
            self.show_error("Your password is too weak. Please use a stronger one.", msg)
            return

        if not self.terms_check.isChecked():
            self.show_error("Error", "Please agree to the Terms and Conditions.")
            return

        try:
            print(f"Sign-up attempt for: {email}")

            response = self.supabase.auth.sign_up({
                "email": email,
                "password": password,
                "options": {
                    "data": {
                        "prenom": firstname,
                        "nom": lastname,
                        "status": "pending_approval",
                    }
                }
            })
            
            if response.user:
                # Create a user profile in the custom table
                self.create_user_profile(response.user.id, email, firstname, lastname)

                # Send the email to the admin
                email_sent = self.send_admin_notification(email, firstname, lastname, response.user.id)

                if email_sent:
                    self.show_success(
                        "Your registration request has been submitted",
                        f"Your request has been successfully submitted!\n\n"
                        f"A notification email has been sent to the administrator.\n"
                        f"You will receive a confirmation at {email} once your account is approved by the admin."
                    )
                else:
                    self.show_success(
                        "Account Created",
                        f"Your request has been successfully submitted!\n\n"
                        f"Your account is pending approval by the administrator.\n"
                        f"You will receive a confirmation at {email} once approved."
                    )

                # Return to login window
                if self.window_manager:
                    self.window_manager.show_login_window()
                else:
                    self.close()

            else:
                self.show_error("Error", "Unable to create your account. Please try again.")

        except Exception as e:
            print("Error :", repr(e))
            import traceback
            print("Traceback:", traceback.format_exc())

            error_msg = str(e).lower()

            if "user already registered" in error_msg or "already been registered" in error_msg:
                self.show_error(
                    "Existing Account",
                    "This email is already associated with an account. Please sign in or use a different email address."
                    "Please sign in or use a different email address."
                )
            elif "invalid email" in error_msg:
                self.show_error("Invalid Email", "Please enter a valid email address")
            elif "password" in error_msg and "weak" in error_msg:
                self.show_error("Weak Password", "Please choose a stronger password")
            elif "database error" in error_msg:
                self.show_error(
                    "Configuration Error",
                    "There is an issue with the database configuration."
                    "Please contact the administrator."
                )
            else:
                self.show_error(
                    "Registration Error",
                    f"An error occurred during registration:\n{str(e)}"
                )

    def create_user_profile(self, user_id, email, firstname, lastname):
        """Create a user profile in the user_profiles table"""
        try:
            self.supabase.table('user_profiles').insert({
                'id': user_id,
                'email': email,
                'prenom': firstname,
                'nom': lastname,
                'status': 'pending_approval',
            }).execute()
            print("User profile created in user_profiles")
        except Exception as e:
            print(f"Profile creation error {e}")

    def send_admin_notification(self, user_email, firstname, lastname, user_id):
        """Send email ONLY to admin"""
        try:

            if not os.getenv("GMAIL_USER") or not os.getenv("GMAIL_APP_PASSWORD"):
                print("Missing SMTP variables in .env file")
                return False

            msg = MIMEMultipart()
            msg["From"] = os.getenv("GMAIL_USER")
            msg["To"] = DEFAULT_ADMIN_EMAIL
            msg["Subject"] = "🔔 KPIT - New Registration Request Pending"

            body = f"""
            <div style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto; padding: 20px; background-color: #f8f9fa; border-radius: 8px;">
                <h2 style="color: #2c3e50; text-align: center;">🔔 New Registration Request KPIT</h2>

                <div style="background-color: white; padding: 20px; border-radius: 8px; margin: 20px 0; box-shadow: 0 2px 4px rgba(0,0,0,0.1);">
                    <h3 style="color: #3498db; margin-top: 0;">Applicant Information :</h3>
                    <ul style="list-style: none; padding: 0;">
                        <li style="margin: 10px 0;"><strong>👤 Full name :</strong> {firstname} {lastname}</li>
                        <li style="margin: 10px 0;"><strong>📧 Mail :</strong> {user_email}</li>
                        <li style="margin: 10px 0;"><strong>🆔 User ID  :</strong> {user_id}</li>
                        <li style="margin: 10px 0;"><strong>⏰ Request date :</strong> {self.get_current_datetime()}</li>
                    </ul>
                </div>

                <div style="text-align: center; margin: 30px 0;">
                    <p style="font-size: 16px; color: #555;">To approve or reject this request, access the admin panel :</p>
                    <a href="http://localhost:8000/admin" 
                       style="display: inline-block; background-color: #3498db; color: white; padding: 12px 24px; 
                              text-decoration: none; border-radius: 5px; font-weight: bold; margin: 10px;">
                        🔗 Access Admin Panel
                    </a>
                </div>

                <hr style="border: none; border-top: 1px solid #eee; margin: 20px 0;">
                <p style="color: #7f8c8d; font-size: 12px; text-align: center;">
                    This email was automatically sent by the KPIT system. <br>
                    The user will not receive any notification until you approve their request.
                </p>
            </div>
            """

            msg.attach(MIMEText(body, "html"))

            with smtplib.SMTP(os.getenv("smtp_server", "smtp.gmail.com"), int(os.getenv("smtp_port", 587))) as server:
                server.starttls()
                server.login(os.getenv("GMAIL_USER"), os.getenv("GMAIL_APP_PASSWORD"))
                server.sendmail(os.getenv("GMAIL_USER"), DEFAULT_ADMIN_EMAIL, msg.as_string())

            print(f"Admin notification email sent successfully: ({DEFAULT_ADMIN_EMAIL})")
            return True

        except Exception as e:
            print(f"Error sending admin email: {str(e)}")
            return False

    def get_current_datetime(self):
        """Returns the current formatted date and time"""
        from datetime import datetime
        return datetime.now().strftime("%d/%m/%Y à %H:%M")

    def show_error(self, title, message):
        msg = QMessageBox(self)
        msg.setIcon(QMessageBox.Icon.Critical)
        msg.setWindowTitle(title)
        msg.setText(message)
        msg.setStyleSheet("""
            QMessageBox {
                background-color: #2d2d2d;
                color: #e0e0e0;
            }
            QMessageBox QPushButton {
                background-color: #43a047;
                color: white;
                padding: 8px 16px;
                border: none;
                border-radius: 4px;
                min-width: 80px;
            }
            QMessageBox QPushButton:hover {
                background-color: #2e7d32;
            }
        """)
        msg.exec()

    def show_success(self, title, message):
        msg = QMessageBox(self)
        msg.setIcon(QMessageBox.Icon.Information)
        msg.setWindowTitle(title)
        msg.setText(message)
        msg.setStyleSheet("""
            QMessageBox {
                background-color: #2d2d2d;
                color: #e0e0e0;
            }
            QMessageBox QPushButton {
                background-color: #43a047;
                color: white;
                padding: 8px 16px;
                border: none;
                border-radius: 4px;
                min-width: 80px;
            }
            QMessageBox QPushButton:hover {
                background-color: #2e7d32;
            }
        """)
        msg.exec()

    def show_login_window(self):
        """Navigate to login window"""
        if self.window_manager:
            self.window_manager.show_login_window()
        else:
            # Fallback if no handler exists
            from login_window import LoginWindow
            self.hide()
            self.login_window = LoginWindow()
            self.login_window.show()

    def closeEvent(self, event):
        """Handle window closing"""
        if self.window_manager:
            self.window_manager.quit_application()
        event.accept()

    def attempt_signup(self):
        """Method to handle signup button click - calls the existing validation method"""
        self.validate_and_submit()
