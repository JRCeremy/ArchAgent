import sys

from PySide6.QtWidgets import (
    QApplication,
    QComboBox,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QMainWindow,
    QPushButton,
    QTextEdit,
    QVBoxLayout,
    QWidget,
)

from config_loader import load_config
from prompt_manager import build_full_prompt
from model_client import run_model
from output_cleaner import clean_output
from server_manager import ServerManager


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        # Load config and create server manager
        self.config = load_config()
        self.server_manager = ServerManager()

        # Presets: each preset chooses a model + prompt pair
        self.presets = {
            "Quick Help": {
                "model": "fallback",
                "prompt": "linux_helper_short",
            },
            "Learn": {
                "model": "general",
                "prompt": "linux_helper_adaptive",
            },
            "Code": {
                "model": "code",
                "prompt": "coding_helper_deepseek",
            },
        }

        # Window basics
        self.setWindowTitle("project_linux_universal")
        self.resize(900, 600)

        # Central widget + main layout
        central = QWidget()
        self.setCentralWidget(central)
        main_layout = QVBoxLayout(central)

        # ---------------------------
        # Top controls row
        # ---------------------------
        top_row = QHBoxLayout()
        main_layout.addLayout(top_row)

        # Preset selector
        top_row.addWidget(QLabel("Preset"))
        self.preset_selector = QComboBox()
        self.preset_selector.addItems(self.presets.keys())
        top_row.addWidget(self.preset_selector)

        # Prompt selector
        top_row.addWidget(QLabel("Prompt"))
        self.prompt_selector = QComboBox()
        self.prompt_selector.addItems(self.config["prompt"]["profiles"].keys())
        self.prompt_selector.setCurrentText(self.config["prompt"]["active_profile"])
        top_row.addWidget(self.prompt_selector)

        # Model selector
        top_row.addWidget(QLabel("Model"))
        self.model_selector = QComboBox()
        self.model_selector.addItems(self.config["models"]["available"].keys())
        self.model_selector.setCurrentText(self.config["models"]["default"])
        top_row.addWidget(self.model_selector)

        # ---------------------------
        # Output panel
        # ---------------------------
        self.output_panel = QTextEdit()
        self.output_panel.setReadOnly(True)
        self.output_panel.setPlaceholderText("Model output will appear here...")
        main_layout.addWidget(self.output_panel)

        # ---------------------------
        # Bottom input row
        # ---------------------------
        bottom_row = QHBoxLayout()
        main_layout.addLayout(bottom_row)

        self.ask_box = QLineEdit()
        self.ask_box.setPlaceholderText("Ask something...")
        bottom_row.addWidget(self.ask_box)

        self.send_button = QPushButton("Send")
        bottom_row.addWidget(self.send_button)

        self.clear_button = QPushButton("Clear")
        bottom_row.addWidget(self.clear_button)

        # ---------------------------
        # Status line
        # ---------------------------
        self.status_label = QLabel("Ready.")
        main_layout.addWidget(self.status_label)

        # ---------------------------
        # Signal connections
        # ---------------------------
        self.preset_selector.currentTextChanged.connect(self.apply_preset)
        self.model_selector.currentTextChanged.connect(self.on_model_changed)
        self.prompt_selector.currentTextChanged.connect(
            lambda _: self.update_status("Prompt changed.")
        )
        self.send_button.clicked.connect(self.send_prompt)
        self.clear_button.clicked.connect(self.clear_ui)
        self.ask_box.returnPressed.connect(self.send_prompt)

        # ---------------------------
        # Initial startup state
        # ---------------------------
        self.preset_selector.setCurrentText("Quick Help")
        self.apply_preset("Quick Help")

    # ---------------------------------
    # Status helper
    # ---------------------------------
    def update_status(self, prefix="Ready."):
        current_prompt = self.prompt_selector.currentText()
        current_model = self.model_selector.currentText()
        model_info = self.config["models"]["available"][current_model]
        model_path = model_info["path"]

        running_model = self.server_manager.current_model or "none"
        match_state = "MATCH" if running_model == model_path else "MISMATCH"

        self.status_label.setText(
            f"{prefix} Prompt: {current_prompt} | "
            f"Selected model: {current_model} ({model_info['name']}) | "
            f"Expected file: {model_path} | "
            f"Running server: {running_model} | "
            f"{match_state}"
        )

    # ---------------------------------
    # Backend server helpers
    # ---------------------------------
    def get_selected_model_path(self):
        current_model = self.model_selector.currentText()
        return self.config["models"]["available"][current_model]["path"]

    def switch_server_to_selected_model(self):
        model_path = self.get_selected_model_path()
        self.update_status("Switching server...")
        self.server_manager.start(model_path, context=1536, threads=6)
        self.update_status("Server switched.")

    def on_model_changed(self, _):
        self.switch_server_to_selected_model()

    # ---------------------------------
    # Preset handling
    # ---------------------------------
    def apply_preset(self, preset_name):
        preset = self.presets[preset_name]
        self.model_selector.setCurrentText(preset["model"])
        self.prompt_selector.setCurrentText(preset["prompt"])
        self.switch_server_to_selected_model()
        self.update_status(f"Preset: {preset_name}.")

    # ---------------------------------
    # Ask model
    # ---------------------------------
    def send_prompt(self):
        user_input = self.ask_box.text().strip()
        if not user_input:
            return

        current_prompt = self.prompt_selector.currentText()
        current_model = self.model_selector.currentText()

        self.update_status("Thinking...")

        try:
            full_prompt = build_full_prompt(self.config, user_input, current_prompt)
            output = run_model(full_prompt, self.config, current_model)
            output = clean_output(output)
            self.output_panel.setPlainText(output)
            self.update_status("Done.")
        except Exception as e:
            self.output_panel.setPlainText(f"Error:\n{e}")
            self.update_status("Request failed.")

        self.ask_box.clear()

    # ---------------------------------
    # Clear UI
    # ---------------------------------
    def clear_ui(self):
        self.ask_box.clear()
        self.output_panel.clear()
        self.update_status("Cleared.")

    # ---------------------------------
    # Clean shutdown
    # ---------------------------------
    def closeEvent(self, event):
        self.server_manager.stop()
        event.accept()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())
