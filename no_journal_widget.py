"""
Reusable widget for displaying "No Journal Files" message
"""
from pathlib import Path
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLabel, QFrame
from PyQt6.QtGui import QFont
from PyQt6.QtCore import Qt
from config import DEFAULT_LOG_DIR


def has_journal_files() -> bool:
    """Check if journal files exist"""
    if not DEFAULT_LOG_DIR.exists():
        return False
    log_files = list(DEFAULT_LOG_DIR.glob("*.log"))
    return len(log_files) > 0


class NoJournalFilesWidget(QWidget):
    """Elegant widget displayed when no journal files are found"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.build_ui()
    
    def build_ui(self):
        """Build the informational UI"""
        layout = QVBoxLayout()
        layout.setSpacing(20)
        layout.setContentsMargins(40, 40, 40, 40)
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        # Main container frame
        container = QFrame()
        container.setStyleSheet("""
            QFrame {
                background-color: #2b2b2b;
                border: 2px solid #3c3c3c;
                border-radius: 10px;
                padding: 30px;
            }
        """)
        container_layout = QVBoxLayout()
        container_layout.setSpacing(15)
        container_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        # Icon/Emoji (using text)
        icon_label = QLabel("📋")
        icon_font = QFont()
        icon_font.setPointSize(48)
        icon_label.setFont(icon_font)
        icon_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        container_layout.addWidget(icon_label)
        
        # Title
        title = QLabel("No Journal Files Found")
        title_font = QFont()
        title_font.setPointSize(20)
        title_font.setBold(True)
        title.setFont(title_font)
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title.setStyleSheet("color: #4ec9b0; margin-bottom: 10px;")
        container_layout.addWidget(title)
        
        # Main message
        message = QLabel(
            "Elite Dangerous journal files were not found in the expected location.\n\n"
            "This is normal if you haven't played Elite Dangerous yet, or if the game\n"
            "is installed in a different location."
        )
        message.setAlignment(Qt.AlignmentFlag.AlignCenter)
        message.setStyleSheet("color: #cccccc; font-size: 12px; line-height: 1.6;")
        message.setWordWrap(True)
        container_layout.addWidget(message)
        
        # Expected location
        location_frame = QFrame()
        location_frame.setStyleSheet("""
            QFrame {
                background-color: #1e1e1e;
                border: 1px solid #3c3c3c;
                border-radius: 5px;
                padding: 15px;
                margin-top: 10px;
            }
        """)
        location_layout = QVBoxLayout()
        location_layout.setSpacing(5)
        
        location_title = QLabel("Expected Journal File Location:")
        location_title.setStyleSheet("color: #888888; font-size: 10px; font-weight: bold;")
        location_layout.addWidget(location_title)
        
        location_path = QLabel(str(DEFAULT_LOG_DIR))
        location_path.setStyleSheet("color: #4ec9b0; font-size: 11px; font-family: monospace;")
        location_path.setWordWrap(True)
        location_layout.addWidget(location_path)
        
        location_frame.setLayout(location_layout)
        container_layout.addWidget(location_frame)
        
        # Instructions
        instructions = QLabel(
            "<b>To get started:</b><br><br>"
            "1. Install and launch Elite Dangerous<br>"
            "2. Play the game at least once to generate journal files<br>"
            "3. Journal files are created automatically when you start playing<br>"
            "4. Return to this application and refresh to see your data"
        )
        instructions.setAlignment(Qt.AlignmentFlag.AlignLeft)
        instructions.setStyleSheet("color: #aaaaaa; font-size: 11px; line-height: 1.8; padding: 15px;")
        instructions.setWordWrap(True)
        container_layout.addWidget(instructions)
        
        container.setLayout(container_layout)
        layout.addWidget(container)
        
        layout.addStretch()
        self.setLayout(layout)

