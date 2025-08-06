import os
import json
import re
import random
import pandas as pd
from jinja2 import Environment, FileSystemLoader

from PyQt5.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QLineEdit, QPushButton, QFrame, QTableWidget,
    QTableWidgetItem, QFileDialog, QMessageBox, QTextEdit,
    QHeaderView 
)
from PyQt5.QtGui import QIcon
import torch
from transformers import AutoTokenizer, AutoModelForSeq2SeqLM


class PrincipalWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("KPIT - DTC Generator")
        self.setMinimumSize(1000, 700)
        base_dir = os.path.dirname(os.path.abspath(__file__))  # -> views/
        logo_path = os.path.join(base_dir, "../assets/kpit_logo.png")
        self.setWindowIcon(QIcon(logo_path))

        # Load AI model
        model_id = "./t5_model"
        self.tokenizer = AutoTokenizer.from_pretrained(model_id)
        self.model = AutoModelForSeq2SeqLM.from_pretrained(model_id)
        self.device = torch.device("cpu")
        self.model.to(self.device)

        self.current_test_case_data = None

        self._build_ui()
        self.apply_styles()

    # ---------------- UI ---------------- #
    def _build_ui(self):
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.setSpacing(20)

        # --- File Excel --- #
        top_frame = QFrame()
        top_layout = QHBoxLayout(top_frame)
        top_layout.setContentsMargins(0, 0, 0, 0)

        self.excel_path_input = QLineEdit()
        self.excel_path_input.setPlaceholderText("Select the Excel file...")
        self.excel_path_input.setMinimumHeight(40)
        self.excel_path_input.setStyleSheet("padding: 8px;")

        # Browse Button 
        browse_btn = QPushButton("Browse")
        browse_btn.setObjectName("browseBtn")
        browse_btn.clicked.connect(self.browse_file)
        browse_btn.setMinimumHeight(40)

        # Add to section
        top_layout.addWidget(QLabel("Excel File:"))
        top_layout.addWidget(self.excel_path_input)
        top_layout.addWidget(browse_btn)

        main_layout.addWidget(top_frame)

        # --- Ligne DTC ID + Tester Name + Run Button --- #
        test_case_frame = QFrame()
        test_case_layout = QHBoxLayout(test_case_frame)

        self.test_case_input = QLineEdit()
        self.test_case_input.setPlaceholderText("Enter the test case ID...")
        self.test_case_input.setMinimumHeight(40)
        self.test_case_input.setStyleSheet("padding: 8px;")

        self.tester_name_input = QLineEdit()
        self.tester_name_input.setPlaceholderText("Enter tester name...")
        self.tester_name_input.setMinimumHeight(40)
        self.tester_name_input.setStyleSheet("padding: 8px;")

        # Run Button 
        self.run_btn = QPushButton("Run")
        self.run_btn.setObjectName("loginBtn")
        self.run_btn.clicked.connect(self.generate_test_case)
        self.run_btn.setFixedWidth(100)
        self.run_btn.setMinimumHeight(40)

        test_case_layout.addWidget(QLabel("Test Case ID:"))
        test_case_layout.addWidget(self.test_case_input)
        test_case_layout.addSpacing(20)
        test_case_layout.addWidget(QLabel("Tester Name:"))
        test_case_layout.addWidget(self.tester_name_input)
        test_case_layout.addSpacing(20)
        test_case_layout.addWidget(self.run_btn)  # Run button to the right of the Tester Name field

        main_layout.addWidget(test_case_frame)


        # --- Result Table --- #
        self.table = QTableWidget()
        self.table.setColumnCount(4)
        self.table.setHorizontalHeaderLabels(["DTC ID", "Coding", "Trigger Conditions", "Debounce Time"])
        self.table.setMinimumHeight(100)  
        self.table.horizontalHeader().setStretchLastSection(True)
        self.table.verticalHeader().setVisible(False)
        main_layout.addWidget(self.table, 1)

        # Adjust the column widths
        header = self.table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeToContents)  # DTC ID takes just the necessary space
        header.setSectionResizeMode(1, QHeaderView.Stretch)           # Coding takes up more space
        header.setSectionResizeMode(2, QHeaderView.Stretch)           # Trigger Conditions takes up more space
        header.setSectionResizeMode(3, QHeaderView.ResizeToContents)  # Debounce Time compacted

        self.table.verticalHeader().setDefaultSectionSize(60)  # Default height 60px
        self.table.verticalHeader().setMinimumSectionSize(40)  # Minimum 40px
        self.table.setWordWrap(True)                          # Allows word wrapping (line breaks)
        self.table.resizeRowsToContents()                     # Adjusts the height according to the content


        # --- Generated Test Case Display --- #
        main_layout.addWidget(QLabel("Generated Test Case:"))
        self.test_case_text = QTextEdit()
        self.test_case_text.setReadOnly(True)
        self.test_case_text.setMinimumHeight(400)
        main_layout.addWidget(self.test_case_text)

        # --- Download Button  --- #
        self.download_btn = QPushButton("Download Test Case")
        self.download_btn.setEnabled(False)
        self.download_btn.clicked.connect(self.download_test_case)
        main_layout.addWidget(self.download_btn)

    def apply_styles(self):
        self.setStyleSheet("""
                
        /* General background */
        QWidget {
            background-color: #121212;
            color: #e0e0e0;
            font-family: 'Segoe UI', sans-serif;
            font-size: 14px;
        }

        /* Labels */
        QLabel {
            color: #a5d6a7;
            font-weight: bold;
        }

        /* Text fields */
        QLineEdit {
            background-color: #1e1e1e;
            color: #ffffff;
            border: 1px solid #2e7d32;
            border-radius: 4px;
            padding: 8px;
        }

        /* Buttons */
        QPushButton#browseBtn, QPushButton#loginBtn, QPushButton {
            background-color: #2e7d32;
            color: white;
            border: none;
            border-radius: 4px;
            padding: 10px 16px;
        }
        QPushButton#browseBtn:hover, QPushButton#loginBtn:hover, QPushButton:hover {
            background-color: #1b5e20;
        }

        /* Table */
        QTableWidget {
            background-color: #1e1e1e;
            color: #e0e0e0;
            border: 1px solid #2e7d32;
            gridline-color: #2e7d32;
            alternate-background-color: #1b1b1b;
        }

        QTableWidget::item {
            padding: 6px;
        }

        /* Table headers */
        QHeaderView::section {
            background-color: #2e7d32;
            color: white;
            padding: 6px;
            border: none;
            font-weight: bold;
        }

        /* Text area */
        QTextEdit {
            background-color: #1e1e1e;
            color: #e0e0e0;
            border: 1px solid #2e7d32;
            border-radius: 4px;
            padding: 10px;
        }
        """)

    # ---------------- IA ---------------- #
    def generate_rule_output_raw(self, rule_text):
        inputs = self.tokenizer(rule_text, return_tensors="pt", truncation=True, max_length=256).to(self.device)
        outputs = self.model.generate(**inputs, max_new_tokens=256, num_beams=10, early_stopping=True)
        return self.tokenizer.decode(outputs[0], skip_special_tokens=True)

    def parse_model_output(self, raw_output):
        """
        Parse the raw output text from the model into structured codding and trigger_conditions.
        If operator is missing in triggers, default to '<'.
        """
        raw_output = raw_output.replace("\n", " ").strip()
        # Extract CODDING and TRIGGERS or IF sections
        coding_match = re.search(r'CODDING:\s*(.*?)\s*(TRIGGERS:|IF:|$)', raw_output, re.IGNORECASE)
        triggers_match = re.search(r'(TRIGGERS:|IF:)\s*(.*)', raw_output, re.IGNORECASE)

        coding_raw = coding_match.group(1).strip() if coding_match else ""
        triggers_raw = triggers_match.group(2).strip() if triggers_match else ""

        # Parse codding
        codding = []
        coding_parts = re.split(r'\s{2,}', coding_raw)  # split by 2+ spaces
        for part in coding_parts:
            part = part.strip()
            if part:
                codding.append(part)

        # Parse triggers
        triggers = []
        if triggers_raw:
            parts = triggers_raw.split()
            i = 0
            while i < len(parts):
                var = parts[i]
                op = "<"  # default operator
                val = None
                hex_code = ""

                # Check if next token is an operator
                if i + 1 < len(parts) and parts[i + 1] in [">", "<", "==", "!=", ">=", "<="]:
                    op = parts[i + 1]
                    val = parts[i + 2] if i + 2 < len(parts) else None
                    if i + 3 < len(parts) and parts[i + 3].startswith("0x"):
                        hex_code = parts[i + 3]
                        i += 4
                    else:
                        i += 3
                else:
                    # No explicit operator, value directly after var
                    val = parts[i + 1] if i + 1 < len(parts) else None
                    if i + 2 < len(parts) and parts[i + 2].startswith("0x"):
                        hex_code = parts[i + 2]
                        i += 3
                    else:
                        i += 2

                if val:
                    triggers.append({
                        "variable": var,
                        "operator": op,
                        "value": val,
                        "hex_code": hex_code
                    })

        return codding, triggers

    def generate_test_case_for_dtc(self, input_dtc, excel_path):
        df = pd.read_excel(excel_path)
        row = df[df["DTC"] == input_dtc]
        if row.empty:
            QMessageBox.warning(self, "Warning", f"DTC {input_dtc} Not found.")
            return None
        row = row.iloc[0]

        rule_text = row["Implementation"]
        ECU = row.get("ECU", "ECU1")
        Bus = row.get("BUS", "BUS")
        Debounce = int(float(row.get("Debounce time", 1000)))

        raw_output = self.generate_rule_output_raw(rule_text)

        codding, trigger_conditions = self.parse_model_output(raw_output)

        # Generate random values for trigger_conditions
        for cond in trigger_conditions:
            try:
                val = float(cond.get("value", ""))
            except (ValueError, TypeError):
                val = None
            op = cond.get("operator", "<")

            if val is not None:
                if op == ">":
                    cond["error_value"] = round(random.uniform(val + 1, val * 1.5), 1)
                    cond["normal_value"] = round(random.uniform(val * 0.5, val - 1), 1)
                elif op == "<":
                    cond["error_value"] = round(random.uniform(val * 0.5, val - 1), 1)
                    cond["normal_value"] = round(random.uniform(val + 1, val * 1.5), 1)
                else:
                    cond["error_value"] = val
                    cond["normal_value"] = round(random.uniform(val + 1, val * 1.5), 1)

        tester_name = self.tester_name_input.text().strip() or "Unknown Tester"
        data = {
            "tester_name": tester_name.strip().lower().replace(" ", "."),
            "dtc_code": input_dtc,
            "ECU": ECU,
            "Bus": Bus,
            "Debounce": Debounce,
            "codding": codding,
            "trigger_conditions": trigger_conditions,
        }
        return data

    # ---------------- Actions UI ---------------- #
    def browse_file(self):
        file_path, _ = QFileDialog.getOpenFileName(self, "Select Excel File", "", "Excel Files (*.xlsx *.xls)")
        if file_path:
            self.excel_path_input.setText(file_path)

    def generate_test_case(self):
        excel_path = self.excel_path_input.text().strip()
        dtc_id = self.test_case_input.text().strip()
        if not excel_path or not dtc_id:
            QMessageBox.warning(self, "Warning", "Select an Excel file and a DTC ID.")
            return

        data = self.generate_test_case_for_dtc(dtc_id, excel_path)
        if not data:
            return

        # Dictionary list to string conversion
        def dict_list_to_str(dict_list):
            lines = []
            for d in dict_list:
                if isinstance(d, dict):
                    line = ", ".join(f"{k}={v}" for k, v in d.items())
                else:
                    line = str(d)
                lines.append(line)
            return "\n".join(lines)

        self.table.setRowCount(1)
        self.table.setItem(0, 0, QTableWidgetItem(dtc_id))
        coding_list = data.get("codding", [])
        if coding_list:
            coding_str = " and ".join(str(c).strip() for c in coding_list if str(c).strip())
        else:
            coding_str = ""


        trigger_str = " or ".join(
            f"{tc.get('variable','')} {tc.get('operator','')} {tc.get('value','')}"
            for tc in data["trigger_conditions"]
        )
        self.table.setItem(0, 1, QTableWidgetItem(coding_str))
        self.table.setItem(0, 2, QTableWidgetItem(trigger_str))
        self.table.setItem(0, 3, QTableWidgetItem(str(data.get("Debounce", "1000"))))

        self.current_test_case_data = data
        self.download_btn.setEnabled(True)

        # Render the test case template and display it in the QTextEdit
        env = Environment(loader=FileSystemLoader("."))
        template = env.get_template("dtc_test_template.robot.j2")
        rendered_test_case = template.render(**data)
        self.test_case_text.setPlainText(rendered_test_case)

        QMessageBox.information(self, "Success", "Test case generated and displayed.")

    def download_test_case(self):
        if not self.current_test_case_data:
            QMessageBox.warning(self, "Warning", "No test case data to download.")
            return

        save_path, _ = QFileDialog.getSaveFileName(
            self,
            "Save Test Case Robot File",
            f"{self.current_test_case_data['dtc_code']}_testcase.robot",
            "Robot Framework Files (*.robot)"
        )
        if save_path:
            # Save the rendered content currently displayed in QTextEdit
            rendered_test_case = self.test_case_text.toPlainText()
            with open(save_path, "w", encoding="utf-8") as f:
                f.write(rendered_test_case)
            QMessageBox.information(self, "Saved", f"Test case saved:\n{save_path}")



    def set_user_data(self, user_data):
        self.user_data = user_data
        print("User data set:", user_data)
