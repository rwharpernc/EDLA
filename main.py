"""
Elite Dangerous Log Analyzer - Main Application
"""
import sys
from typing import Dict, Optional
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QPushButton, QLabel, QLineEdit, QListWidget, QListWidgetItem,
    QStackedWidget, QFrame, QTextEdit, QMenu, QMessageBox
)
from PyQt6.QtCore import Qt, QTimer, QThread, pyqtSignal
from PyQt6.QtGui import QFont, QPalette, QColor, QAction

import logging
from config import DEFAULT_LOG_DIR, APP_NAME, APP_VERSION, APP_AUTHOR, LOGS_DIR, DOCUMENTS_DIR, BASE_DIR
from profile_manager import ProfileManager
from log_monitor import LogMonitor
from event_tracker import EventTracker

# Set up logging
log_file = LOGS_DIR / "app.log"
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(log_file),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)


class LogMonitorThread(QThread):
    """Thread for running log monitor"""
    event_received = pyqtSignal(dict)
    
    def __init__(self, log_monitor: LogMonitor):
        super().__init__()
        self.log_monitor = log_monitor
        self.running = False
    
    def run(self):
        """Start monitoring in thread"""
        self.running = True
        self.log_monitor.start()
    
    def stop_monitoring(self):
        """Stop monitoring"""
        if self.running:
            self.log_monitor.stop()
            self.running = False


class ProfileScreen(QWidget):
    """Screen for managing commander profiles"""
    
    def __init__(self, profile_manager: ProfileManager, parent=None):
        super().__init__(parent)
        self.profile_manager = profile_manager
        self.build_ui()
        self.refresh_profile_list()
    
    def showEvent(self, event):
        """Refresh list when screen is shown"""
        super().showEvent(event)
        self.refresh_profile_list()
    
    def build_ui(self):
        layout = QVBoxLayout()
        layout.setSpacing(10)
        layout.setContentsMargins(15, 15, 15, 15)
        
        # Title
        title = QLabel("Commander Profiles")
        title_font = QFont()
        title_font.setPointSize(18)
        title_font.setBold(True)
        title.setFont(title_font)
        layout.addWidget(title)
        
        # Info label
        info_label = QLabel("Profiles are automatically created from journal files.\nYou can also manually add profiles below:")
        info_label.setStyleSheet("color: #888888; font-size: 10px; padding: 5px;")
        info_label.setWordWrap(True)
        layout.addWidget(info_label)
        
        # Refresh button
        refresh_btn = QPushButton("🔄 Refresh from Journal Files")
        refresh_btn.setStyleSheet("""
            QPushButton {
                background-color: #0078d4;
                color: white;
                border: none;
                padding: 8px 16px;
                border-radius: 4px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #106ebe;
            }
        """)
        refresh_btn.clicked.connect(self.refresh_from_journals)
        layout.addWidget(refresh_btn)
        
        # Profile list
        list_label = QLabel("Existing Profiles:")
        list_font = QFont()
        list_font.setPointSize(10)
        list_label.setFont(list_font)
        layout.addWidget(list_label)
        
        self.profile_list = QListWidget()
        self.profile_list.itemDoubleClicked.connect(self.select_profile)
        layout.addWidget(self.profile_list)
        
        # Add profile section
        add_frame = QFrame()
        add_frame.setFrameShape(QFrame.Shape.StyledPanel)
        add_frame.setStyleSheet("QFrame { background-color: #2b2b2b; border-radius: 5px; padding: 10px; }")
        add_layout = QVBoxLayout()
        add_layout.setSpacing(10)
        
        add_label = QLabel("Add New Profile (Manual):")
        add_font = QFont()
        add_font.setPointSize(10)
        add_label.setFont(add_font)
        add_layout.addWidget(add_label)
        
        input_layout = QHBoxLayout()
        self.profile_input = QLineEdit()
        self.profile_input.setPlaceholderText("Commander Name")
        self.profile_input.returnPressed.connect(self.add_profile)
        input_layout.addWidget(self.profile_input)
        
        add_button = QPushButton("Add Profile")
        add_button.clicked.connect(self.add_profile)
        add_button.setStyleSheet("""
            QPushButton {
                background-color: #0078d4;
                color: white;
                border: none;
                padding: 8px 16px;
                border-radius: 4px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #106ebe;
            }
            QPushButton:pressed {
                background-color: #005a9e;
            }
        """)
        input_layout.addWidget(add_button)
        
        add_layout.addLayout(input_layout)
        add_frame.setLayout(add_layout)
        layout.addWidget(add_frame)
        
        layout.addStretch()
        self.setLayout(layout)
    
    def refresh_profile_list(self):
        """Refresh the list of profiles"""
        self.profile_list.clear()
        profiles = self.profile_manager.list_profiles()
        
        for profile_name in profiles:
            item = QListWidgetItem(profile_name)
            self.profile_list.addItem(item)
    
    def refresh_from_journals(self):
        """Refresh profiles from journal files"""
        # Find the main window
        widget = self
        while widget and not isinstance(widget, EliteDangerousApp):
            widget = widget.parent()
        
        if widget and hasattr(widget, 'refresh_commanders'):
            widget.refresh_commanders()
        self.refresh_profile_list()
    
    def add_profile(self):
        """Add a new profile"""
        commander_name = self.profile_input.text().strip()
        if commander_name:
            self.profile_manager.get_profile(commander_name)
            self.profile_input.clear()
            self.refresh_profile_list()
            
            # Find the main window and update commander menu
            widget = self
            while widget and not isinstance(widget, EliteDangerousApp):
                widget = widget.parent()
            
            if widget and hasattr(widget, 'update_commander_menu'):
                widget.update_commander_menu()
    
    def select_profile(self, item: QListWidgetItem):
        """Select a profile"""
        commander_name = item.text()
        # Find the main window
        widget = self
        while widget and not isinstance(widget, EliteDangerousApp):
            widget = widget.parent()
        
        if widget and hasattr(widget, 'select_commander'):
            widget.select_commander(commander_name)
            widget.stacked_widget.setCurrentIndex(0)  # Switch to monitor screen


class MonitorScreen(QWidget):
    """Main monitoring screen"""
    
    def __init__(self, event_tracker: EventTracker, parent=None):
        super().__init__(parent)
        self.event_tracker = event_tracker
        self.build_ui()
        self.update_events()
    
    def build_ui(self):
        layout = QVBoxLayout()
        layout.setSpacing(10)
        layout.setContentsMargins(15, 15, 15, 15)
        
        # Title
        title = QLabel("Elite Dangerous Monitor")
        title_font = QFont()
        title_font.setPointSize(18)
        title_font.setBold(True)
        title.setFont(title_font)
        layout.addWidget(title)
        
        # Current commander display
        self.commander_label = QLabel("No commander selected")
        self.commander_label.setStyleSheet("color: #888888; font-size: 12px;")
        layout.addWidget(self.commander_label)
        
        # Status card
        status_frame = QFrame()
        status_frame.setFrameShape(QFrame.Shape.StyledPanel)
        status_frame.setStyleSheet("QFrame { background-color: #2b2b2b; border-radius: 5px; padding: 10px; }")
        status_layout = QVBoxLayout()
        status_layout.setSpacing(5)
        
        self.status_label = QLabel("Status: Not monitoring")
        self.status_label.setStyleSheet("color: #888888; font-size: 12px;")
        status_layout.addWidget(self.status_label)
        
        self.log_dir_label = QLabel(f"Log Directory: {DEFAULT_LOG_DIR}")
        self.log_dir_label.setStyleSheet("color: #666666; font-size: 10px;")
        status_layout.addWidget(self.log_dir_label)
        
        status_frame.setLayout(status_layout)
        layout.addWidget(status_frame)
        
        # Events section
        events_label = QLabel("Recent Events")
        events_font = QFont()
        events_font.setPointSize(12)
        events_font.setBold(True)
        events_label.setFont(events_font)
        layout.addWidget(events_label)
        
        self.events_list = QListWidget()
        self.events_list.setStyleSheet("""
            QListWidget {
                background-color: #1e1e1e;
                border: 1px solid #3c3c3c;
                border-radius: 4px;
            }
            QListWidget::item {
                padding: 5px;
                border-bottom: 1px solid #2b2b2b;
            }
            QListWidget::item:selected {
                background-color: #0078d4;
            }
        """)
        layout.addWidget(self.events_list)
        
        self.setLayout(layout)
    
    def update_commander_display(self, commander_name: Optional[str] = None):
        """Update the commander display"""
        if commander_name:
            self.commander_label.setText(f"Active Commander: {commander_name}")
            self.commander_label.setStyleSheet("color: #4ec9b0; font-size: 12px; font-weight: bold;")
        else:
            self.commander_label.setText("No commander selected")
            self.commander_label.setStyleSheet("color: #888888; font-size: 12px;")
    
    def update_status(self, is_monitoring: bool):
        """Update monitoring status"""
        if is_monitoring:
            self.status_label.setText("Status: ✓ Monitoring")
            self.status_label.setStyleSheet("color: #4ec9b0; font-size: 12px;")
        else:
            self.status_label.setText("Status: Not monitoring")
            self.status_label.setStyleSheet("color: #888888; font-size: 12px;")
    
    def update_events(self):
        """Update the events list"""
        self.events_list.clear()
        events = self.event_tracker.get_recent_events(limit=50)
        
        for event in reversed(events):  # Show newest first
            event_type = event.get("event", "Unknown")
            timestamp = event.get("timestamp", "")[:19] if event.get("timestamp") else "No timestamp"
            text = f"[{timestamp}] {event_type}"
            
            item = QListWidgetItem(text)
            self.events_list.addItem(item)


class EliteDangerousApp(QMainWindow):
    """Main application window"""
    
    def __init__(self):
        super().__init__()
        self.profile_manager = ProfileManager()
        self.event_tracker = EventTracker(self.profile_manager)
        self.log_monitor = LogMonitor(self.on_log_event)
        self.monitor_thread: Optional[LogMonitorThread] = None
        self.is_monitoring = False
        self.current_commander = None
        
        self.setWindowTitle(f"{APP_NAME} v{APP_VERSION} - Elite Dangerous Log Analyzer © {APP_AUTHOR}")
        self.setGeometry(100, 100, 900, 700)
        
        # Apply dark theme
        self.apply_dark_theme()
        
        # Create central widget with stacked layout
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        
        # Top navigation bar
        nav_bar = QFrame()
        nav_bar.setStyleSheet("""
            QFrame {
                background-color: #0078d4;
                padding: 10px;
            }
        """)
        nav_layout = QHBoxLayout()
        nav_layout.setContentsMargins(15, 10, 15, 10)
        
        # Commander selector button
        self.commander_button = QPushButton("Select Commander")
        self.commander_button.setStyleSheet("""
            QPushButton {
                background-color: #1e88e5;
                color: white;
                border: 2px solid white;
                padding: 8px 16px;
                border-radius: 4px;
                font-weight: bold;
                font-size: 11pt;
            }
            QPushButton:hover {
                background-color: #42a5f5;
                border: 2px solid #ffffff;
            }
            QPushButton:pressed {
                background-color: #1565c0;
            }
        """)
        self.commander_button.clicked.connect(self.show_commander_menu)
        nav_layout.addWidget(self.commander_button)
        
        nav_layout.addStretch()
        
        # Create stacked widget first (needed for button connections)
        self.stacked_widget = QStackedWidget()
        
        # Create screens
        self.monitor_screen = MonitorScreen(self.event_tracker)
        self.profile_screen = ProfileScreen(self.profile_manager)
        
        self.stacked_widget.addWidget(self.monitor_screen)
        self.stacked_widget.addWidget(self.profile_screen)
        
        # Navigation buttons (store as instance variables for style updates)
        self.monitor_btn = QPushButton("Monitor")
        self.monitor_btn.clicked.connect(lambda: self.stacked_widget.setCurrentIndex(0))
        nav_layout.addWidget(self.monitor_btn)
        
        self.profiles_btn = QPushButton("Profiles")
        self.profiles_btn.clicked.connect(lambda: self.stacked_widget.setCurrentIndex(1))
        nav_layout.addWidget(self.profiles_btn)
        
        nav_bar.setLayout(nav_layout)
        main_layout.addWidget(nav_bar)
        
        # Connect stacked widget to update button styles when screen changes
        self.stacked_widget.currentChanged.connect(self.update_nav_button_styles)
        
        # Set initial active button style (Monitor is default, index 0)
        self.update_nav_button_styles(0)
        
        main_layout.addWidget(self.stacked_widget)
        central_widget.setLayout(main_layout)
        
        # Set up commander menu
        self.commander_menu = QMenu(self)
        self.update_commander_menu()
        
        # Add Help menu with About
        self.create_help_menu()
        
        # Refresh commanders from journals on startup
        self.refresh_commanders()
        
        # Start monitoring
        self.start_monitoring()
        
        # Set up timer for UI updates
        self.update_timer = QTimer()
        self.update_timer.timeout.connect(self.update_ui)
        self.update_timer.start(1000)  # Update every second
    
    def apply_dark_theme(self):
        """Apply dark theme to the application"""
        palette = QPalette()
        palette.setColor(QPalette.ColorRole.Window, QColor(30, 30, 30))
        palette.setColor(QPalette.ColorRole.WindowText, QColor(255, 255, 255))
        palette.setColor(QPalette.ColorRole.Base, QColor(30, 30, 30))
        palette.setColor(QPalette.ColorRole.AlternateBase, QColor(43, 43, 43))
        palette.setColor(QPalette.ColorRole.ToolTipBase, QColor(0, 0, 0))
        palette.setColor(QPalette.ColorRole.ToolTipText, QColor(255, 255, 255))
        palette.setColor(QPalette.ColorRole.Text, QColor(255, 255, 255))
        palette.setColor(QPalette.ColorRole.Button, QColor(43, 43, 43))
        palette.setColor(QPalette.ColorRole.ButtonText, QColor(255, 255, 255))
        palette.setColor(QPalette.ColorRole.BrightText, QColor(255, 0, 0))
        palette.setColor(QPalette.ColorRole.Link, QColor(42, 130, 218))
        palette.setColor(QPalette.ColorRole.Highlight, QColor(42, 130, 218))
        palette.setColor(QPalette.ColorRole.HighlightedText, QColor(0, 0, 0))
        self.setPalette(palette)
    
    def update_nav_button_styles(self, index):
        """Update navigation button styles based on active screen"""
        # Active button style (highlighted)
        active_style = """
            QPushButton {
                background-color: white;
                color: #0078d4;
                border: 1px solid white;
                padding: 6px 12px;
                border-radius: 4px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #f0f0f0;
            }
        """
        
        # Inactive button style (transparent)
        inactive_style = """
            QPushButton {
                background-color: transparent;
                color: white;
                border: 1px solid white;
                padding: 6px 12px;
                border-radius: 4px;
            }
            QPushButton:hover {
                background-color: rgba(255, 255, 255, 0.2);
            }
        """
        
        # Update styles based on active screen
        if index == 0:  # Monitor screen
            self.monitor_btn.setStyleSheet(active_style)
            self.profiles_btn.setStyleSheet(inactive_style)
        elif index == 1:  # Profiles screen
            self.monitor_btn.setStyleSheet(inactive_style)
            self.profiles_btn.setStyleSheet(active_style)
    
    def refresh_commanders(self):
        """Refresh commander list by scanning journal files"""
        self.profile_manager.refresh_from_journals()
        self.update_commander_menu()
        self.profile_screen.refresh_profile_list()
    
    def update_commander_menu(self):
        """Update the commander selection menu"""
        self.commander_menu.clear()
        profiles = self.profile_manager.list_profiles()
        
        if profiles:
            for profile_name in profiles:
                action = QAction(profile_name, self)
                action.triggered.connect(lambda checked, name=profile_name: self.select_commander(name))
                self.commander_menu.addAction(action)
            
            # Add separator and refresh option
            self.commander_menu.addSeparator()
            refresh_action = QAction("🔄 Refresh from Journals", self)
            refresh_action.triggered.connect(self.refresh_commanders)
            self.commander_menu.addAction(refresh_action)
        else:
            action = QAction("No commanders found - Scanning journal files...", self)
            action.triggered.connect(self.refresh_commanders)
            self.commander_menu.addAction(action)
    
    def show_commander_menu(self):
        """Show the commander selection menu"""
        button_pos = self.commander_button.mapToGlobal(self.commander_button.rect().bottomLeft())
        self.commander_menu.exec(button_pos)
    
    def select_commander(self, commander_name: str):
        """Select a commander"""
        if "No profiles" in commander_name:
            return
        
        self.current_commander = commander_name
        self.event_tracker.set_current_commander(commander_name)
        self.commander_button.setText(commander_name)
        self.monitor_screen.update_commander_display(commander_name)
        self.update_commander_menu()
    
    def on_log_event(self, event_data: Dict):
        """Handle events from log monitor"""
        if self.current_commander:
            self.event_tracker.process_event(event_data)
    
    def start_monitoring(self):
        """Start monitoring log files"""
        if not self.is_monitoring:
            self.monitor_thread = LogMonitorThread(self.log_monitor)
            self.monitor_thread.start()
            self.is_monitoring = True
            self.monitor_screen.update_status(True)
    
    def stop_monitoring(self):
        """Stop monitoring log files"""
        if self.is_monitoring and self.monitor_thread:
            self.monitor_thread.stop_monitoring()
            self.monitor_thread.wait()
            self.is_monitoring = False
            self.monitor_screen.update_status(False)
    
    def create_help_menu(self):
        """Create Help menu with About dialog"""
        help_menu = self.menuBar().addMenu("&Help")
        
        about_action = QAction("&About EDLA", self)
        about_action.triggered.connect(self.show_about)
        help_menu.addAction(about_action)
        
        license_action = QAction("&License", self)
        license_action.triggered.connect(self.show_license)
        help_menu.addAction(license_action)
    
    def show_about(self):
        """Show About dialog with copyright information"""
        about_text = f"""
        <h2>{APP_NAME} v{APP_VERSION}</h2>
        <p><b>Elite Dangerous Log Analyzer</b></p>
        <p>Copyright © 2025 {APP_AUTHOR}</p>
        <p>All rights reserved.</p>
        <hr>
        <p>This program is free software: you can redistribute it and/or modify
        it under the terms of the GNU General Public License as published by
        the Free Software Foundation, either version 3 of the License, or
        (at your option) any later version.</p>
        <p>This program is distributed in the hope that it will be useful,
        but WITHOUT ANY WARRANTY; without even the implied warranty of
        MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.</p>
        <p>See the License dialog for the full GPL-3.0 license text.</p>
        """
        
        msg = QMessageBox(self)
        msg.setWindowTitle("About EDLA")
        msg.setTextFormat(Qt.TextFormat.RichText)
        msg.setText(about_text)
        msg.setStandardButtons(QMessageBox.StandardButton.Ok)
        msg.exec()
    
    def show_license(self):
        """Show License dialog with full GPL-3.0 text"""
        license_file = BASE_DIR / "LICENSE"
        license_text = ""
        
        if license_file.exists():
            try:
                with open(license_file, 'r', encoding='utf-8') as f:
                    license_text = f.read()
            except Exception as e:
                logger.error(f"Error reading license file: {e}")
                license_text = self._get_default_license_text()
        else:
            license_text = self._get_default_license_text()
        
        # Create a scrollable text widget for the license
        dialog = QMessageBox(self)
        dialog.setWindowTitle("License - GPL-3.0")
        dialog.setText("GNU General Public License v3.0")
        dialog.setInformativeText("Full license text:")
        
        # Create a text area for the license
        text_widget = QTextEdit()
        text_widget.setPlainText(license_text)
        text_widget.setReadOnly(True)
        text_widget.setMinimumSize(600, 400)
        
        # Add the text widget to the dialog
        layout = dialog.layout()
        layout.addWidget(text_widget, 1, 0, 1, layout.columnCount())
        
        dialog.exec()
    
    def _get_default_license_text(self):
        """Get default license text if file can't be read"""
        return f"""GNU GENERAL PUBLIC LICENSE
Version 3, 29 June 2007

Copyright (C) 2025 {APP_AUTHOR}

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see <https://www.gnu.org/licenses/>."""
    
    def update_ui(self):
        """Periodically update the UI"""
        self.monitor_screen.update_events()
    
    def closeEvent(self, event):
        """Handle window close event"""
        self.stop_monitoring()
        event.accept()


def main():
    """Main entry point"""
    app = QApplication(sys.argv)
    app.setStyle('Fusion')  # Use Fusion style for better cross-platform look
    
    window = EliteDangerousApp()
    window.show()
    
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
