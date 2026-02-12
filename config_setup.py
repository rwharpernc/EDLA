"""
Interactive setup for edla_config.json when the file does not exist.
Run before importing config so that paths and optional keys can be created.
Do not import config from this module.
"""
import json
import os
import sys
from pathlib import Path

from PyQt6.QtWidgets import (
    QDialog,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QPushButton,
    QFileDialog,
    QMessageBox,
    QGroupBox,
    QFormLayout,
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont

CONFIG_FILENAME = "edla_config.json"


def get_base_dir_for_setup():
    """Return application base directory without importing config."""
    if getattr(sys, "frozen", False):
        return Path(sys.executable).parent
    return Path(__file__).parent


def _default_log_dir():
    return Path(os.path.expanduser("~")) / "Saved Games" / "Frontier Developments" / "Elite Dangerous"


def _default_app_data_dir():
    return Path(os.path.expanduser("~")) / ".edla"


def run_setup(base_dir: Path) -> bool:
    """
    Show a dialog to collect log_dir, app_data_dir, and optional api_key,
    then write edla_config.json to base_dir.
    Returns True if config was saved, False if user cancelled.
    """
    dialog = ConfigSetupDialog(base_dir)
    return dialog.exec() == QDialog.DialogCode.Accepted


class ConfigSetupDialog(QDialog):
    """Dialog to gather paths and optional API key and write edla_config.json."""

    def __init__(self, base_dir: Path):
        super().__init__()
        self.base_dir = Path(base_dir)
        self.setWindowTitle("EDLA Configuration Setup")
        self.setMinimumWidth(520)
        self._build_ui()

    def _build_ui(self):
        layout = QVBoxLayout(self)
        layout.setSpacing(12)

        intro = QLabel(
            "No configuration file was found. Enter paths below (or leave blank to use defaults). "
            "This will create edla_config.json next to the application. It will not be shared in the repo."
        )
        intro.setWordWrap(True)
        intro.setStyleSheet("color: #c0c0c0;")
        layout.addWidget(intro)

        group = QGroupBox("Paths and optional key")
        form = QFormLayout(group)
        form.setSpacing(8)

        default_log = str(_default_log_dir())
        default_app = str(_default_app_data_dir())

        self.log_edit = QLineEdit()
        self.log_edit.setPlaceholderText(f"Default: {default_log}")
        self.log_edit.setMinimumWidth(360)
        log_row = QHBoxLayout()
        log_row.addWidget(self.log_edit)
        browse_log = QPushButton("Browse…")
        browse_log.clicked.connect(self._browse_log)
        log_row.addWidget(browse_log)
        form.addRow("Log directory (Elite Dangerous journals):", log_row)

        self.app_data_edit = QLineEdit()
        self.app_data_edit.setPlaceholderText(f"Default: {default_app}")
        self.app_data_edit.setMinimumWidth(360)
        app_row = QHBoxLayout()
        app_row.addWidget(self.app_data_edit)
        browse_app = QPushButton("Browse…")
        browse_app.clicked.connect(self._browse_app_data)
        app_row.addWidget(browse_app)
        form.addRow("App data directory (profiles, database):", app_row)

        self.api_key_edit = QLineEdit()
        self.api_key_edit.setPlaceholderText("Optional – leave empty if not needed")
        self.api_key_edit.setEchoMode(QLineEdit.EchoMode.Password)
        form.addRow("API key (optional):", self.api_key_edit)

        layout.addWidget(group)

        use_defaults = QPushButton("Use defaults for all paths")
        use_defaults.clicked.connect(self._use_defaults)
        layout.addWidget(use_defaults)

        buttons = QHBoxLayout()
        buttons.addStretch()
        cancel_btn = QPushButton("Cancel")
        cancel_btn.clicked.connect(self.reject)
        buttons.addWidget(cancel_btn)
        save_btn = QPushButton("Save and continue")
        save_btn.setDefault(True)
        save_btn.clicked.connect(self._save)
        buttons.addWidget(save_btn)
        layout.addLayout(buttons)

        self.setStyleSheet("""
            QDialog { background-color: #2d2d2d; }
            QLabel, QGroupBox { color: #e0e0e0; }
            QGroupBox::title { color: #8ec07c; }
            QLineEdit {
                background-color: #3c3c3c;
                color: #d4d4d4;
                border: 1px solid #555;
                padding: 4px;
            }
            QPushButton {
                background-color: #0e639c;
                color: white;
                border: none;
                padding: 6px 14px;
            }
            QPushButton:hover { background-color: #1177bb; }
            QPushButton:pressed { background-color: #0d5689; }
        """)

    def _browse_log(self):
        start = self.log_edit.text().strip() or str(_default_log_dir())
        path = QFileDialog.getExistingDirectory(self, "Select Elite Dangerous log directory", start)
        if path:
            self.log_edit.setText(path)

    def _browse_app_data(self):
        start = self.app_data_edit.text().strip() or str(_default_app_data_dir())
        path = QFileDialog.getExistingDirectory(self, "Select app data directory", start)
        if path:
            self.app_data_edit.setText(path)

    def _use_defaults(self):
        self.log_edit.clear()
        self.app_data_edit.clear()
        self.api_key_edit.clear()

    def _save(self):
        log_dir = self.log_edit.text().strip()
        app_data_dir = self.app_data_edit.text().strip()
        api_key = self.api_key_edit.text().strip()

        data = {
            "log_dir": log_dir,
            "app_data_dir": app_data_dir,
            "api_key": api_key,
        }

        config_path = self.base_dir / CONFIG_FILENAME
        try:
            with open(config_path, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=2)
        except OSError as e:
            QMessageBox.critical(
                self,
                "Cannot save config",
                f"Could not write {config_path}:\n{e}",
            )
            return

        self.accept()
