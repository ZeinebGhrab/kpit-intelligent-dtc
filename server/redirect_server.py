from flask import Flask, request, render_template_string, redirect, url_for
from supabase import create_client, Client
import os
from dotenv import load_dotenv
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

# Load environment variables from .env file
load_dotenv()

# Configuration Supabase
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_ANON_KEY") or os.getenv("SUPABASE_KEY")
SUPABASE_SERVICE_KEY = os.getenv("SUPABASE_SERVICE_KEY")

if not SUPABASE_URL or not SUPABASE_KEY:
    raise Exception("Missing Supabase credentials in .env file")

# Supabase Client Initialization
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)
print("Client created:", Client)
admin_supabase: Client = create_client(SUPABASE_URL, SUPABASE_SERVICE_KEY) if SUPABASE_SERVICE_KEY else supabase

# Default admin email
DEFAULT_ADMIN_EMAIL = os.getenv("GMAIL_USER")

# Flask application creation
app = Flask(__name__)

# HTML Templates with Modern Design from reset.html
RESET_FORM_HTML = '''
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Reset Password | KPIT</title>
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/animate.css/4.1.1/animate.min.css">
    <style>
        :root {
            --primary-color: #0a6f34;
            --primary-dark: #0b9243;
            --primary-light: #e8f5e9;
            --white: #ffffff;
            --light-gray: #f5f5f5;
            --dark-gray: #333333;
            --border-radius: 8px;
            --box-shadow: 0 10px 30px rgba(0, 0, 0, 0.1);
        }

        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
        }

        body {
            background-color: var(--light-gray);
            display: flex;
            justify-content: center;
            align-items: center;
            min-height: 100vh;
            color: var(--dark-gray);
            background-image: 
                radial-gradient(circle at 10% 20%, var(--primary-light) 0%, transparent 20%),
                radial-gradient(circle at 90% 80%, var(--primary-light) 0%, transparent 20%);
            background-size: cover;
            background-attachment: fixed;
        }

        .reset-container {
            background-color: var(--white);
            width: 100%;
            max-width: 480px;
            padding: 50px 40px;
            border-radius: var(--border-radius);
            box-shadow: var(--box-shadow);
            text-align: center;
            position: relative;
            overflow: hidden;
            animation: fadeInUp 0.6s ease-out;
            border: 1px solid rgba(0, 0, 0, 0.05);
        }

        .reset-container::before {
            content: '';
            position: absolute;
            top: 0;
            left: 0;
            width: 100%;
            height: 5px;
            background: linear-gradient(90deg, var(--primary-color), var(--primary-dark));
        }

        .logo-container {
            margin-bottom: 30px;
            transition: transform 0.3s;
        }

        .logo-container:hover {
            transform: scale(1.05);
        }

        .logo {
            max-width: 180px;
            height: auto;
            filter: drop-shadow(0 2px 4px rgba(0, 0, 0, 0.1));
        }

        h1 {
            font-size: 26px;
            margin-bottom: 20px;
            color: var(--dark-gray);
            position: relative;
            display: inline-block;
        }

        h1::after {
            content: '';
            position: absolute;
            bottom: -8px;
            left: 50%;
            transform: translateX(-50%);
            width: 50px;
            height: 3px;
            background: linear-gradient(90deg, var(--primary-color), var(--primary-dark));
            border-radius: 3px;
        }

        p {
            color: #666;
            margin-bottom: 30px;
            line-height: 1.6;
        }

        .form-group {
            margin-bottom: 25px;
            text-align: left;
            position: relative;
        }

        label {
            display: block;
            margin-bottom: 10px;
            font-weight: 600;
            color: var(--dark-gray);
            transition: all 0.3s;
        }

        input {
            width: 100%;
            padding: 14px 16px;
            border: 1px solid #ddd;
            border-radius: var(--border-radius);
            font-size: 16px;
            transition: all 0.3s;
            background-color: #fafafa;
        }

        input:focus {
            outline: none;
            border-color: var(--primary-color);
            box-shadow: 0 0 0 3px rgba(10, 111, 52, 0.1);
            background-color: var(--white);
        }

        .btn {
            width: 100%;
            padding: 16px;
            background-color: var(--primary-color);
            color: var(--white);
            border: none;
            border-radius: var(--border-radius);
            font-size: 16px;
            font-weight: 600;
            cursor: pointer;
            transition: all 0.3s;
            position: relative;
            overflow: hidden;
            box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
        }

        .btn:hover {
            background-color: var(--primary-dark);
            transform: translateY(-2px);
            box-shadow: 0 6px 12px rgba(0, 0, 0, 0.15);
        }

        .btn:active {
            transform: translateY(0);
        }

        .btn::after {
            content: '';
            position: absolute;
            top: -50%;
            left: -60%;
            width: 200%;
            height: 200%;
            background: rgba(255, 255, 255, 0.2);
            transform: rotate(30deg);
            transition: all 0.3s;
        }

        .btn:hover::after {
            left: 100%;
        }

        .message {
            margin-top: 25px;
            padding: 15px;
            border-radius: var(--border-radius);
            display: none;
            animation: fadeIn 0.5s;
        }

        .success {
            background-color: rgba(10, 111, 52, 0.1);
            color: var(--primary-dark);
            border: 1px solid var(--primary-color);
        }

        .error {
            background-color: rgba(231, 76, 60, 0.1);
            color: #c0392b;
            border: 1px solid #e74c3c;
        }

        .footer {
            margin-top: 30px;
            font-size: 13px;
            color: #999;
            animation: fadeIn 1s 0.5s both;
        }

        .requirements {
            text-align: left;
            font-size: 12px;
            color: #666;
            margin-top: 10px;
            padding: 15px;
            background-color: #f8f9fa;
            border-radius: var(--border-radius);
            border-left: 4px solid var(--primary-color);
        }

        .requirements ul {
            margin-left: 20px;
            margin-top: 8px;
        }

        .requirements li {
            margin-bottom: 4px;
        }

        @media (max-width: 480px) {
            .reset-container {
                padding: 40px 25px;
                margin: 0 20px;
            }

            h1 {
                font-size: 22px;
            }
        }

        @keyframes fadeInUp {
            from {
                opacity: 0;
                transform: translateY(30px);
            }
            to {
                opacity: 1;
                transform: translateY(0);
            }
        }

        @keyframes fadeIn {
            from { opacity: 0; }
            to { opacity: 1; }
        }

        @keyframes float {
            0%, 100% { transform: translateY(0); }
            50% { transform: translateY(-10px); }
        }

        .floating-icon {
            position: absolute;
            opacity: 0.1;
            z-index: -1;
            animation: float 6s ease-in-out infinite;
        }

        .floating-icon:nth-child(1) {
            top: 10%;
            left: 5%;
            font-size: 40px;
            animation-delay: 0s;
        }

        .floating-icon:nth-child(2) {
            top: 60%;
            right: 5%;
            font-size: 50px;
            animation-delay: 1s;
        }

        .floating-icon:nth-child(3) {
            bottom: 10%;
            left: 15%;
            font-size: 30px;
            animation-delay: 2s;
        }
    </style>
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0-beta3/css/all.min.css">
</head>
<body>
    <!-- Floating decorative elements -->
    <i class="fas fa-lock floating-icon"></i>
    <i class="fas fa-key floating-icon"></i>
    <i class="fas fa-shield-alt floating-icon"></i>

    <div class="reset-container animate__animated animate__fadeInUp">
        <div class="logo-container">
            <h1 style="color: var(--primary-color); font-size: 32px; margin-bottom: 5px;">🔐 KPIT</h1>
            <p style="margin-bottom: 0; color: #999; font-size: 14px;">Secure Access Portal</p>
        </div>

        <h1 class="animate__animated animate__fadeIn">Reset Your Password</h1>
        <p class="animate__animated animate__fadeIn animate__delay-1s">Enter your new password below to secure your account.</p>

        <form action="/update-password" method="POST" id="resetForm">
            <input type="hidden" name="access_token" value="{{ access_token }}">

            <div class="form-group animate__animated animate__fadeIn animate__delay-1s">
                <label for="new_password">New Password</label>
                <input type="password" id="new_password" name="new_password" required placeholder="Enter your new password">
            </div>

            <div class="form-group animate__animated animate__fadeIn animate__delay-2s">
                <label for="confirm_password">Confirm New Password</label>
                <input type="password" id="confirm_password" name="confirm_password" required placeholder="Confirm your new password">
            </div>

            <div class="requirements animate__animated animate__fadeIn animate__delay-2s">
                <strong>Password Requirements:</strong>
                <ul>
                    <li>At least 8 characters long</li>
                    <li>One uppercase letter (A-Z)</li>
                    <li>One lowercase letter (a-z)</li>
                    <li>One number (0-9)</li>
                    <li>One special character (!@#$%^&*)</li>
                </ul>
            </div>

            <button type="submit" class="btn animate__animated animate__fadeIn animate__delay-3s">
                <span class="animate__animated animate__fadeIn">Reset Password</span>
            </button>
        </form>

        {% if error %}
        <div id="message" class="message error" style="display: block;">
            {{ error }}
        </div>
        {% endif %}

        <div class="footer animate__animated animate__fadeIn animate__delay-4s">
            <p>© 2024 KPIT Technologies. All rights reserved.</p>
        </div>
    </div>

    <script>
        document.addEventListener('DOMContentLoaded', function() {
            const newPassword = document.getElementById('new_password');
            const confirmPassword = document.getElementById('confirm_password');
            const resetForm = document.getElementById('resetForm');
            const messageElement = document.getElementById('message');

            resetForm.addEventListener('submit', function(e) {
                // Reset any existing messages
                if (messageElement) {
                    messageElement.style.display = 'none';
                    messageElement.className = 'message';
                }

                // Validate password match
                if (newPassword.value !== confirmPassword.value) {
                    e.preventDefault();
                    showMessage('Passwords do not match. Please try again.', 'error');
                    confirmPassword.focus();
                    return;
                }

                // Validate password length
                if (newPassword.value.length < 8) {
                    e.preventDefault();
                    showMessage('Password must be at least 8 characters long.', 'error');
                    newPassword.focus();
                    return;
                }

                // Validate password strength
                const password = newPassword.value;
                const hasUpperCase = /[A-Z]/.test(password);
                const hasLowerCase = /[a-z]/.test(password);
                const hasNumbers = /\d/.test(password);
                const hasNonalphas = /\W/.test(password);

                if (!hasUpperCase || !hasLowerCase || !hasNumbers || !hasNonalphas) {
                    e.preventDefault();
                    showMessage('Password must meet all requirements listed above.', 'error');
                    return;
                }

                // Show loading state
                const btn = this.querySelector('.btn');
                btn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Processing...';
                btn.disabled = true;
            });

            function showMessage(message, type) {
                if (!messageElement) {
                    // Create message element if it doesn't exist
                    const newMessageElement = document.createElement('div');
                    newMessageElement.id = 'message';
                    newMessageElement.className = `message ${type} animate__animated animate__fadeIn`;
                    newMessageElement.textContent = message;
                    newMessageElement.style.display = 'block';
                    resetForm.parentNode.insertBefore(newMessageElement, resetForm.nextSibling);
                } else {
                    messageElement.textContent = message;
                    messageElement.className = `message ${type} animate__animated animate__fadeIn`;
                    messageElement.style.display = 'block';
                }

                // Scroll to message
                if (messageElement) {
                    messageElement.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
                }
            }
        });
    </script>
</body>
</html>
'''

SUCCESS_HTML = '''
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Password Reset Successful | KPIT</title>
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/animate.css/4.1.1/animate.min.css">
    <style>
        :root {
            --primary-color: #0a6f34;
            --primary-dark: #0b9243;
            --primary-light: #e8f5e9;
            --success-color: #27ae60;
            --white: #ffffff;
            --light-gray: #f5f5f5;
            --dark-gray: #333333;
            --border-radius: 8px;
            --box-shadow: 0 10px 30px rgba(0, 0, 0, 0.1);
        }

        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
        }

        body {
            background-color: var(--light-gray);
            display: flex;
            justify-content: center;
            align-items: center;
            min-height: 100vh;
            color: var(--dark-gray);
            background-image: 
                radial-gradient(circle at 10% 20%, var(--primary-light) 0%, transparent 20%),
                radial-gradient(circle at 90% 80%, var(--primary-light) 0%, transparent 20%);
            background-size: cover;
            background-attachment: fixed;
        }

        .success-container {
            background-color: var(--white);
            width: 100%;
            max-width: 480px;
            padding: 50px 40px;
            border-radius: var(--border-radius);
            box-shadow: var(--box-shadow);
            text-align: center;
            position: relative;
            overflow: hidden;
            animation: fadeInUp 0.6s ease-out;
            border: 1px solid rgba(0, 0, 0, 0.05);
        }

        .success-container::before {
            content: '';
            position: absolute;
            top: 0;
            left: 0;
            width: 100%;
            height: 5px;
            background: linear-gradient(90deg, var(--success-color), #219a52);
        }

        .success-icon {
            font-size: 80px;
            color: var(--success-color);
            margin-bottom: 30px;
            animation: bounce 1s ease-in-out;
        }

        h1 {
            font-size: 28px;
            margin-bottom: 20px;
            color: var(--success-color);
            position: relative;
            display: inline-block;
        }

        h1::after {
            content: '';
            position: absolute;
            bottom: -8px;
            left: 50%;
            transform: translateX(-50%);
            width: 60px;
            height: 3px;
            background: linear-gradient(90deg, var(--success-color), #219a52);
            border-radius: 3px;
        }

        p {
            color: #666;
            margin-bottom: 20px;
            line-height: 1.6;
            font-size: 16px;
        }

        .btn {
            display: inline-block;
            padding: 16px 32px;
            background-color: var(--success-color);
            color: var(--white);
            text-decoration: none;
            border-radius: var(--border-radius);
            font-size: 16px;
            font-weight: 600;
            cursor: pointer;
            transition: all 0.3s;
            border: none;
            box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
            margin-top: 10px;
        }

        .btn:hover {
            background-color: #219a52;
            transform: translateY(-2px);
            box-shadow: 0 6px 12px rgba(0, 0, 0, 0.15);
        }

        .footer {
            margin-top: 40px;
            font-size: 13px;
            color: #999;
        }

        @media (max-width: 480px) {
            .success-container {
                padding: 40px 25px;
                margin: 0 20px;
            }

            h1 {
                font-size: 24px;
            }

            .success-icon {
                font-size: 60px;
            }
        }

        @keyframes fadeInUp {
            from {
                opacity: 0;
                transform: translateY(30px);
            }
            to {
                opacity: 1;
                transform: translateY(0);
            }
        }

        @keyframes bounce {
            0%, 20%, 50%, 80%, 100% {
                transform: translateY(0);
            }
            40% {
                transform: translateY(-10px);
            }
            60% {
                transform: translateY(-5px);
            }
        }
    </style>
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0-beta3/css/all.min.css">
</head>
<body>
    <div class="success-container animate__animated animate__fadeInUp">
        <div class="success-icon">
            <i class="fas fa-check-circle"></i>
        </div>

        <h1 class="animate__animated animate__fadeIn">Password Reset Successful!</h1>

        <p class="animate__animated animate__fadeIn animate__delay-1s">
            Your password has been updated successfully.
        </p>

        <p class="animate__animated animate__fadeIn animate__delay-2s">
            You can now close this window and log in to the KPIT application with your new password.
        </p>

        <button onclick="window.close()" class="btn animate__animated animate__fadeIn animate__delay-3s">
            <i class="fas fa-times-circle" style="margin-right: 8px;"></i>
            Close Window
        </button>

        <div class="footer animate__animated animate__fadeIn animate__delay-4s">
            <p>© 2024 KPIT Technologies. All rights reserved.</p>
        </div>
    </div>
</body>
</html>
'''


# Routes

@app.route('/')
def home():
    return '''
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>KPIT Server Status</title>
        <style>
            body {
                font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                background: linear-gradient(135deg, #0a6f34 0%, #0b9243 100%);
                color: white;
                text-align: center;
                padding: 50px 20px;
                min-height: 100vh;
                display: flex;
                flex-direction: column;
                justify-content: center;
                align-items: center;
                margin: 0;
            }
            .container {
                background: rgba(255, 255, 255, 0.1);
                padding: 40px;
                border-radius: 15px;
                backdrop-filter: blur(10px);
                border: 1px solid rgba(255, 255, 255, 0.2);
                max-width: 500px;
                width: 100%;
            }
            h1 {
                font-size: 48px;
                margin-bottom: 20px;
            }
            p {
                font-size: 18px;
                margin: 15px 0;
                opacity: 0.9;
            }
            .status {
                display: inline-block;
                padding: 8px 16px;
                background: rgba(39, 174, 96, 0.2);
                border: 1px solid #27ae60;
                border-radius: 20px;
                margin: 20px 0;
            }
        </style>
    </head>
    <body>
        <div class="container">
            <h1>🚀 KPIT Server</h1>
            <p>Password reset server is active on port 8000</p>
            <div class="status">
                <span style="color: #27ae60;">✅ Online</span>
            </div>
            <p style="font-size: 14px; opacity: 0.7;">
                Ready to handle password reset requests
            </p>
        </div>
    </body>
    </html>
    '''


@app.route('/reset-password')
def handle_reset():
    """Handle password reset links from Supabase"""
    # Try to get access_token from URL parameters first
    access_token = request.args.get('access_token')

    if access_token:
        # Direct access with token
        print(f"✅ Direct reset access with token: {access_token[:20]}...")
        return render_template_string(RESET_FORM_HTML, access_token=access_token)

    # If no direct token, handle fragment-based URLs (Supabase default)
    return '''
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>KPIT - Processing Reset Link</title>
        <style>
            body { 
                font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                text-align: center; 
                padding: 50px 20px;
                background: linear-gradient(135deg, #0a6f34 0%, #0b9243 100%);
                color: white;
                min-height: 100vh;
                display: flex;
                flex-direction: column;
                justify-content: center;
                align-items: center;
                margin: 0;
            }
            .container {
                background: rgba(255, 255, 255, 0.1);
                padding: 40px;
                border-radius: 15px;
                backdrop-filter: blur(10px);
                border: 1px solid rgba(255, 255, 255, 0.2);
                max-width: 500px;
                width: 100%;
            }
            .spinner { 
                border: 4px solid rgba(255, 255, 255, 0.3);
                border-top: 4px solid white;
                border-radius: 50%; 
                width: 50px; 
                height: 50px; 
                animation: spin 1s linear infinite; 
                margin: 20px auto;
            }
            @keyframes spin { 
                0% { transform: rotate(0deg); } 
                100% { transform: rotate(360deg); } 
            }
            h2 { font-size: 24px; margin-bottom: 20px; }
            p { font-size: 16px; opacity: 0.9; line-height: 1.6; }
        </style>
        <script>
            window.onload = function() {
                // Extract token from URL fragment (#)
                const hash = window.location.hash.substring(1);
                const params = new URLSearchParams(hash);
                const access_token = params.get('access_token');
                const type = params.get('type');

                console.log('Hash:', hash);
                console.log('Token:', access_token);
                console.log('Type:', type);

                if (access_token && type === 'recovery') {
                    // Redirect to reset form with token as query parameter
                    window.location.href = '/reset-password-form?access_token=' + access_token;
                } else {
                    document.body.innerHTML = `
                        <div class="container">
                            <h2>❌ Invalid Reset Link</h2>
                            <p>The reset link is invalid or has expired.</p>
                            <p>Please request a new password reset from the KPIT application.</p>
                            <p style="font-size: 12px; margin-top: 30px; opacity: 0.7;">
                                Debug info:<br>
                                Hash: ${hash}<br>
                                Token: ${access_token ? 'Present' : 'Missing'}<br>
                                Type: ${type}
                            </p>
                        </div>
                    `;
                }
            };
        </script>
    </head>
    <body>
        <div class="container">
            <h2>🔄 Processing Reset Link...</h2>
            <div class="spinner"></div>
            <p>Please wait while we process your password reset request.</p>
        </div>
    </body>
    </html>
    '''


@app.route('/reset-password-form')
def show_reset_form():
    """Show the password reset form"""
    access_token = request.args.get('access_token')

    if not access_token:
        return '''
        <!DOCTYPE html>
        <html lang="en">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>KPIT - Missing Token</title>
            <style>
                body {
                    font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                    background: linear-gradient(135deg, #e74c3c 0%, #c0392b 100%);
                    color: white;
                    text-align: center;
                    padding: 50px 20px;
                    min-height: 100vh;
                    display: flex;
                    justify-content: center;
                    align-items: center;
                    margin: 0;
                }
                .container {
                    background: rgba(255, 255, 255, 0.1);
                    padding: 40px;
                    border-radius: 15px;
                    backdrop-filter: blur(10px);
                    border: 1px solid rgba(255, 255, 255, 0.2);
                    max-width: 500px;
                }
            </style>
        </head>
        <body>
            <div class="container">
                <h2>❌ Missing Token</h2>
                <p>The reset token is missing. Please use the link from your email.</p>
            </div>
        </body>
        </html>
        ''', 400

    print(f"Showing reset form for token: {access_token[:20]}...")
    return render_template_string(RESET_FORM_HTML, access_token=access_token)


@app.route('/update-password', methods=['POST'])
def update_password():
    """Update the user's password"""
    access_token = request.form.get('access_token')
    new_password = request.form.get('new_password')
    confirm_password = request.form.get('confirm_password')

    print(f"🔄 Password update request - Token: {access_token[:20] if access_token else 'None'}...")

    # Validation
    if not all([access_token, new_password, confirm_password]):
        error = "All fields are required"
        return render_template_string(RESET_FORM_HTML, access_token=access_token, error=error), 400

    if new_password != confirm_password:
        error = "Passwords do not match"
        return render_template_string(RESET_FORM_HTML, access_token=access_token, error=error), 400

    if len(new_password) < 8:
        error = "Password must be at least 8 characters long"
        return render_template_string(RESET_FORM_HTML, access_token=access_token, error=error), 400

    # Enhanced password validation
    import re
    if not re.search(r"[A-Z]", new_password):
        error = "Password must contain at least one uppercase letter"
        return render_template_string(RESET_FORM_HTML, access_token=access_token, error=error), 400

    if not re.search(r"[a-z]", new_password):
        error = "Password must contain at least one lowercase letter"
        return render_template_string(RESET_FORM_HTML, access_token=access_token, error=error), 400

    if not re.search(r"[0-9]", new_password):
        error = "Password must contain at least one number"
        return render_template_string(RESET_FORM_HTML, access_token=access_token, error=error), 400

    if not re.search(r"[!@#$%^&*(),.?\":{}|<>]", new_password):
        error = "Password must contain at least one special character"
        return render_template_string(RESET_FORM_HTML, access_token=access_token, error=error), 400

    try:
        # Update password using Supabase
        print("Updating password in Supabase...")

        # Set the session with the access token
        supabase.auth.set_session(access_token, access_token)

        # Update the user's password
        response = supabase.auth.update_user({
            "password": new_password
        })

        print("Password updated successfully")

        # Sign out the user
        supabase.auth.sign_out()

        return SUCCESS_HTML

    except Exception as e:
        print(f"Password update error: {e}")
        error = f"Failed to update password: {str(e)}"
        return render_template_string(RESET_FORM_HTML, access_token=access_token, error=error), 500


# Admin panel routes 
@app.route('/admin')
def admin_panel():
    """Simple admin panel with modern design"""
    try:
        response = admin_supabase.table('user_profiles').select('*').order('created_at', desc=True).execute()
        users = response.data if response.data else []

        html = '''
        <!DOCTYPE html>
        <html lang="en">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>KPIT Admin Panel</title>
            <style>
                :root {
                    --primary-color: #0a6f34;
                    --primary-dark: #0b9243;
                    --primary-light: #e8f5e9;
                    --white: #ffffff;
                    --light-gray: #f8f9fa;
                    --dark-gray: #333333;
                    --border-radius: 8px;
                    --box-shadow: 0 2px 10px rgba(0, 0, 0, 0.1);
                }

                * {
                    margin: 0;
                    padding: 0;
                    box-sizing: border-box;
                    font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                }

                body {
                    background-color: var(--light-gray);
                    color: var(--dark-gray);
                    line-height: 1.6;
                    padding: 20px;
                }

                .header {
                    background: linear-gradient(135deg, var(--primary-color), var(--primary-dark));
                    color: white;
                    padding: 30px;
                    border-radius: var(--border-radius);
                    text-align: center;
                    margin-bottom: 30px;
                    box-shadow: var(--box-shadow);
                }

                .header h1 {
                    font-size: 32px;
                    margin-bottom: 10px;
                }

                .header p {
                    opacity: 0.9;
                    font-size: 16px;
                }

                .container {
                    max-width: 1200px;
                    margin: 0 auto;
                    background: var(--white);
                    border-radius: var(--border-radius);
                    box-shadow: var(--box-shadow);
                    overflow: hidden;
                }

                .table-header {
                    background-color: var(--primary-color);
                    color: white;
                    padding: 20px;
                    font-size: 20px;
                    font-weight: 600;
                }

                table {
                    width: 100%;
                    border-collapse: collapse;
                }

                th, td {
                    padding: 15px;
                    text-align: left;
                    border-bottom: 1px solid #eee;
                }

                th {
                    background-color: var(--primary-light);
                    font-weight: 600;
                    color: var(--primary-color);
                }

                tr:hover {
                    background-color: #f8f9fa;
                }

                .status-pending {
                    background-color: #fff3cd;
                    color: #856404;
                    padding: 4px 12px;
                    border-radius: 20px;
                    font-size: 12px;
                    font-weight: 600;
                }

                .status-approved {
                    background-color: #d4edda;
                    color: #155724;
                    padding: 4px 12px;
                    border-radius: 20px;
                    font-size: 12px;
                    font-weight: 600;
                }

                .status-rejected {
                    background-color: #f8d7da;
                    color: #721c24;
                    padding: 4px 12px;
                    border-radius: 20px;
                    font-size: 12px;
                    font-weight: 600;
                }

                .no-users {
                    text-align: center;
                    padding: 50px;
                    color: #666;
                }

                .no-users i {
                    font-size: 48px;
                    margin-bottom: 20px;
                    opacity: 0.5;
                }

                @media (max-width: 768px) {
                    body { padding: 10px; }
                    .header { padding: 20px; }
                    .header h1 { font-size: 24px; }
                    th, td { padding: 10px; font-size: 14px; }
                }
                .btn-approve {
    background-color: #28a745;
    color: white;
    padding: 4px 8px;
    border-radius: 4px;
    text-decoration: none;
    margin-left: 10px;
    font-size: 12px;
}

.btn-reject {
    background-color: #dc3545;
    color: white;
    padding: 4px 8px;
    border-radius: 4px;
    text-decoration: none;
    margin-left: 5px;
    font-size: 12px;
}

.btn-approve:hover, .btn-reject:hover {
    opacity: 0.8;
}
            </style>
            <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0-beta3/css/all.min.css">
        </head>
        <body>
            <div class="header">
                <h1><i class="fas fa-shield-alt"></i> KPIT Admin Panel</h1>
                <p>User Registration Management System</p>
            </div>

            <div class="container">
                <div class="table-header">
                    <i class="fas fa-users"></i> User Registrations (''' + str(len(users)) + ''' total)
                </div>
        '''

        if users:
            html += '''
                <table>
                    <thead>
                        <tr>
                            <th><i class="fas fa-user"></i> Name</th>
                            <th><i class="fas fa-envelope"></i> Email</th>
                            <th><i class="fas fa-info-circle"></i> Status</th>
                            <th><i class="fas fa-calendar"></i> Registration Date</th>
                        </tr>
                    </thead>
                    <tbody>
            '''

            for user in users:
                status = user.get("status", "unknown")
                status_class = f"status-{status.replace('_', '-')}"
                status_display = status.replace('_', ' ').title()

                # Format date
                created_at = user.get("created_at", "")
                if created_at:
                    try:
                        from datetime import datetime
                        dt = datetime.fromisoformat(created_at.replace('Z', '+00:00'))
                        formatted_date = dt.strftime("%d/%m/%Y %H:%M")
                    except:
                        formatted_date = created_at
                else:
                    formatted_date = "N/A"

                html += f'''
                <tr>
                    <td><strong>{user.get("prenom", "")} {user.get("nom", "")}</strong></td>
                    <td>{user.get("email", "")}</td>
                    <td>
                        <span class="{status_class}">{status_display}</span>
                        {f'<a href="/approve-user/{user.get("id")}" class="btn-approve"><i class="fas fa-check"></i> Approve</a>' if status == "pending_approval" else ''}
                        {f'<a href="/reject-user/{user.get("id")}" class="btn-reject"><i class="fas fa-times"></i> Reject</a>' if status == "pending_approval" else ''}
                    </td>
                    <td>{formatted_date}</td>
                </tr>
                '''
            html += '''
                    </tbody>
                </table>
            '''
        else:
            html += '''
                <div class="no-users">
                    <i class="fas fa-user-slash"></i>
                    <h3>No Users Found</h3>
                    <p>No user registrations have been submitted yet.</p>
                </div>
            '''

        html += '''
            </div>
        </body>
        </html>
        '''

        return html

    except Exception as e:
        return f'''
        <!DOCTYPE html>
        <html lang="en">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>KPIT Admin Panel - Error</title>
            <style>
                body {{
                    font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                    background: linear-gradient(135deg, #e74c3c 0%, #c0392b 100%);
                    color: white;
                    text-align: center;
                    padding: 50px 20px;
                    min-height: 100vh;
                    display: flex;
                    justify-content: center;
                    align-items: center;
                    margin: 0;
                }}
                .container {{
                    background: rgba(255, 255, 255, 0.1);
                    padding: 40px;
                    border-radius: 15px;
                    backdrop-filter: blur(10px);
                    border: 1px solid rgba(255, 255, 255, 0.2);
                    max-width: 600px;
                }}
                h1 {{ font-size: 28px; margin-bottom: 20px; }}
                p {{ font-size: 16px; line-height: 1.6; }}
                .error-details {{ 
                    background: rgba(0, 0, 0, 0.2);
                    padding: 20px;
                    border-radius: 8px;
                    margin-top: 20px;
                    font-family: monospace;
                    text-align: left;
                }}
            </style>
        </head>
        <body>
            <div class="container">
                <h1><i class="fas fa-exclamation-triangle"></i> Admin Panel Error</h1>
                <p>An error occurred while loading the admin panel.</p>
                <div class="error-details">
                    <strong>Error Details:</strong><br>
                    {str(e)}
                </div>
                <p style="margin-top: 20px; font-size: 14px; opacity: 0.8;">
                    Please check your Supabase configuration and try again.
                </p>
            </div>
        </body>
        </html>
        '''


@app.route('/approve-user/<user_id>')
def approve_user(user_id):
    try:
        # Update user status in Supabase
        admin_supabase.table('user_profiles').update({
            'status': 'approved'
        }).eq('id', user_id).execute()

        # Send approval email 
        return redirect('/admin?message=User+approved')
    except Exception as e:
        return f"Error: {str(e)}", 500


@app.route('/reject-user/<user_id>')
def reject_user(user_id):
    try:
        # Update user status in Supabase
        admin_supabase.table('user_profiles').update({
            'status': 'rejected'
        }).eq('id', user_id).execute()

        # Send rejection email
        return redirect('/admin?message=User+rejected')
    except Exception as e:
        return f"Error: {str(e)}", 500
    
if __name__ == '__main__':
    print("=" * 60)
    print("🚀 Starting KPIT Flask Server")
    print("=" * 60)
    app.run(host='0.0.0.0', port=8000, debug=False)  # debug=False for production

    app.run(host='0.0.0.0', port=8000, debug=True)