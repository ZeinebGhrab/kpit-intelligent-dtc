# 🚗 KPIT Intelligent DTC Test Case Generator

**An AI-powered desktop application** that automatically generates Robot Framework test cases for automotive Diagnostic Trouble Code (DTC) validation.

## 🌟 Key Features

- **AI-Powered Parsing**:
  - Fine-tuned T5 model transforms implementation rules into test logic
  - Extracts coding parameters and trigger conditions automatically
  - Generates randomized test values (normal/error conditions)

- **User-Friendly Interface**:
  - Modern PyQt5 GUI with interactive tables
  - Excel file import with validation
  - One-click test case generation

- **Enterprise Ready**:
  - User authentication via Supabase
  - Admin approval workflow
  - Password reset functionality
  
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

## Install dependencies:

```bash
pip install -r requirements.txt
```
## 🔧 Initial Setup

### 1. Model Training (Mandatory First Step)

```bash
cd ai_model
python train_model_readable.py 
```
💡 Training requires GPU (4GB VRAM minimum) | Estimated time: ~2h on RTX 3060

### 2. Environment Configuration

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

## 🚀 Getting Started

1. **Launch Application:**

```bash
python run.py
```

2. **Workflow:**

- Log in with approved credentials
- Load DTC Excel file (see format below)
- Enter DTC ID and generate test case
- Export Robot Framework file

## 📊 Excel File Format
Required columns:

| DTC      | ECU  | BUS | Debounce time (ms) | Implementation                                                                                 |
|----------|------|-----|--------------------|------------------------------------------------------------------------------------------------|
| 0x024001 | ECU1 | LIN | 1000               | CURRENT_MONITOR_CAN_ENABLED == TRUE<br>VOLTAGE_SENSOR_CAN_ACTIVE == TRUE<br>Set error if: Voltage_Level > 15V [0x1B2] |

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

## 📜 License
Proprietary software © 2025 KPIT Technologies. All rights reserved.

