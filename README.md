# 🚗 KPIT Intelligent DTC Test Case Generator

An **AI-powered desktop application** that automatically generates **Robot Framework test cases** for **automotive Diagnostic Trouble Code (DTC) validation**.

---

## 📑 Table of Contents
1. [✨ Key Features](#-key-features)
2. [🏗 Project Architecture](#-project-architecture)
3. [⚙️ Requirements](#️-requirements)
4. [🔧 Initial Setup](#-initial-setup)
5. [🚀 Getting Started](#-getting-started)
6. [📊 Excel File Format](#-excel-file-format)
7. [🛠 User Manual](#-user-manual)
8. [🛠 Troubleshooting](#-troubleshooting)
9. [📜 License](#-license)

---

## ✨ Key Features

**AI-Powered Parsing**
- Fine-tuned **T5 model** transforms implementation rules into test logic
- Automatically extracts **coding parameters** and **trigger conditions**
- Generates **randomized test values** for normal/error conditions

**User-Friendly Interface**
- Modern **PyQt5 GUI** with interactive tables
- **Excel file import** with validation
- **One-click test case generation**

**Enterprise Ready**
- **User authentication** via Supabase
- **Admin approval workflow**
- **Password reset functionality**

---

## 🏗 Project Architecture

```bash
kpit-intelligent-dtc/
│
├── server/                       # Server-side application directory
│   ├── redirect_server.py        # Flask server for password reset handling
│   └── supabase_config.py        # Supabase client configuration
│
├── t5_model/                      # Fine-tuned T5 model directory
│   ├── added_tokens.json          # Custom token mappings
│   ├── config.json                # Core model architecture configuration  
│   ├── generation_config.json     # Text generation parameters
│   ├── special_tokens_map.json    # Special token definitions
│   ├── tokenizer_config.json      # Tokenizer settings
│   └── (model files)              # pytorch_model.bin, etc.
│
├── frontend/                      # Main frontend application directory
│   ├── main.py                    # Primary application entry point
│   ├── window_manager.py          # Central window management system
│   ├── views/                     # Contains all application views/windows
│   │    ├── principal_window.py     # Main DTC test case generation interface
│   │    ├── login_window.py         # User authentication window
│   │    └── signup_window.py        # User registration system
│   │
│   └──  assets/
│        ├── kpit_logo.png # Logo displayed in the GUI # [UI Theme] Qt Stylesheet for application styling
│        └── styles.qss
│
├── ai_model/                       # AI model development directory
│   ├── train_model_readable.py     # Model training script
│   └── training_dataset_readable.xlsx  # Training dataset
│
├── dtc_test_template.robot.j2 # Jinja2 template for Robot Framework test case
│
├── requirements.txt # Python dependencies
├── run.py # Startup script launching Flask server and Qt app
│
├── app_snapshots/                  # High-fidelity application screenshots
│   ├── login_window.png           # [Auth] Login interface with Supabase integration
│   ├── signup_window.png          # [Auth] User registration form with validation
│   ├── principal_window.png       # [Core] Main DTC test generation interface
│   └── admin_panel.png            # [Admin] User management dashboard 
└── README.md
```

---

## ⚙️ Requirements

- Python **3.8+**
- PyQt5
- Pandas
- Jinja2
- Torch
- Transformers (Hugging Face)

**Install dependencies:**

```bash
pip install -r requirements.txt
```
---

## 🔧 Initial Setup

### 1. Clone the repository

```bash
git clone https://github.com/ZeinebGhrab/kpit-intelligent-dtc.git
cd kpit-intelligent-dtc
```

### 2. Train the AI model (Mandatory first step)

```bash
cd ai_model
python train_model_readable.py 
```
💡 Requires GPU (≥4GB VRAM)
⏱ Estimated time: ~2h on RTX 3060

### 3. Configure Environment

Create `.env` file with these variables:

```ini
# Supabase (get these from project settings)
SUPABASE_URL="your-project-url"
SUPABASE_KEY="your-anon-key"
SUPABASE_SERVICE_KEY="your-service-key"

# Gmail (enable App Passwords)
GMAIL_USER="your-email@gmail.com"
GMAIL_APP_PASSWORD="generated-app-password"
```
---
## 🚀 Getting Started

**Launch Application:**

```bash
python run.py
```

**Workflow:**

- Log in with approved credentials
- Load DTC Excel file (see format below)
- Enter DTC ID and generate test case
- Export Robot Framework file
  
---

## 📊 Excel File Format
Required columns:

| DTC      | ECU  | BUS | Debounce time (ms) | Implementation                                                                                 |
|----------|------|-----|--------------------|------------------------------------------------------------------------------------------------|
| 0x024001 | ECU1 | LIN | 1000               | CURRENT_MONITOR_CAN_ENABLED == TRUE<br>VOLTAGE_SENSOR_CAN_ACTIVE == TRUE<br>Set error if: Voltage_Level > 15V [0x1B2] |

---

## 📖 User Manual
1. **Connect**
   - If you don’t have an account, sign up first.
   - After the admin approves your account, you can log in.
   - Use the "Forgot Password" option to reset your password if needed.

2. **Access the Main Application**
   - Launch the application after logging in.
   - Browse and load your Excel file containing DTC information.

3. **DTC Input and Test Configuration**
   - Enter a valid DTC ID.
   - Provide a tester name and set the increment value as desired.

4. **Generate Test Case**
   - Click **Run** to generate the `.robot` test case file.

5. **Output**
   - View the generated test case within the application or download it for use.
     
---

## 🛠 Troubleshooting
Common Issues:

1. **Supabase Connection Errors:**

- Verify .env credentials
- Check network access to Supabase URL

2. **AI Model Failures:**

- Ensure t5_model directory exists
- Verify minimum RAM requirements

3. **Excel Format Problems:**

- Validate column headers match exactly
- Check for empty cells in required columns
  
---
## 📜 License
Proprietary software © 2025 KPIT Technologies. All rights reserved.

