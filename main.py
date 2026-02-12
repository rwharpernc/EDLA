"""
Elite Dangerous Log Analyzer - Main Application
"""
import sys
from pathlib import Path
from PyQt6.QtWidgets import QApplication

# Bootstrap: ensure edla_config.json exists before importing config
def _get_base_dir():
    return Path(sys.executable).parent if getattr(sys, "frozen", False) else Path(__file__).parent

app = QApplication(sys.argv)
_base_dir = _get_base_dir()
if not (_base_dir / "edla_config.json").exists():
    from config_setup import run_setup
    if not run_setup(_base_dir):
        sys.exit(0)

import json
from typing import Dict, Optional
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QPushButton, QLabel, QLineEdit, QListWidget, QListWidgetItem,
    QStackedWidget, QFrame, QTextEdit, QMenu, QMessageBox, QComboBox,
    QStatusBar, QScrollArea, QSizePolicy, QProgressBar, QGridLayout
)
from PyQt6.QtCore import Qt, QTimer, QThread, pyqtSignal
from PyQt6.QtGui import QFont, QPalette, QColor, QAction, QBrush

import logging
import traceback
from config import DEFAULT_LOG_DIR, APP_NAME, APP_VERSION, APP_AUTHOR, LOGS_DIR, DOCUMENTS_DIR, BASE_DIR, REVALIDATE_TIMEOUT_MS
from profile_manager import ProfileManager
from log_monitor import LogMonitor
from event_tracker import EventTracker
from session_manager import SessionManager
from dashboard_screen import DashboardScreen
from missions_reputation_screen import MissionsReputationScreen
from current_session_tracker import CurrentSessionTracker
from no_journal_widget import NoJournalFilesWidget, has_journal_files
from journal_startup_reader import get_startup_snapshot

# Set up logging FIRST, before any other imports that might fail
log_file = LOGS_DIR / "app.log"
try:
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(log_file, encoding='utf-8'),
            logging.StreamHandler(sys.stdout)
        ]
    )
except Exception as e:
    # If logging setup fails, try to write to a fallback location
    try:
        fallback_log = BASE_DIR / "app_error.log"
        with open(fallback_log, 'a', encoding='utf-8') as f:
            f.write(f"Failed to set up logging: {e}\n")
    except:
        pass  # If even that fails, we're out of options

logger = logging.getLogger(__name__)

# Set up global exception handler to catch uncaught exceptions
def log_exception(exc_type, exc_value, exc_traceback):
    """Log uncaught exceptions"""
    if issubclass(exc_type, KeyboardInterrupt):
        sys.__excepthook__(exc_type, exc_value, exc_traceback)
        return
    
    error_msg = "".join(traceback.format_exception(exc_type, exc_value, exc_traceback))
    logger.critical(f"Uncaught exception:\n{error_msg}")
    
    # Also try to write to file directly in case logging is broken
    try:
        with open(log_file, 'a', encoding='utf-8') as f:
            f.write(f"\n{'='*80}\n")
            f.write(f"UNCAUGHT EXCEPTION\n")
            f.write(f"{error_msg}\n")
            f.write(f"{'='*80}\n")
    except:
        pass

sys.excepthook = log_exception


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
        outer = QVBoxLayout()
        outer.setContentsMargins(0, 0, 0, 0)
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.Shape.NoFrame)
        scroll.setStyleSheet("QScrollArea { background: transparent; border: none; }")
        scroll_content = QWidget()
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
        self.profile_list.setMinimumHeight(120)
        layout.addWidget(self.profile_list, 1)

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

        # No journal files widget (initially hidden)
        self.no_journal_widget = NoJournalFilesWidget()
        self.no_journal_widget.hide()
        layout.addWidget(self.no_journal_widget)

        scroll_content.setLayout(layout)
        scroll.setWidget(scroll_content)
        outer.addWidget(scroll)
        self.setLayout(outer)
    
    def refresh_profile_list(self):
        """Refresh the list of profiles"""
        self.profile_list.clear()
        profiles = self.profile_manager.list_profiles()
        
        # Check for journal files
        if not has_journal_files() and not profiles:
            # No journal files and no profiles - show informational widget
            self.profile_list.hide()
            self.no_journal_widget.show()
        else:
            self.profile_list.show()
            self.no_journal_widget.hide()
            
            if profiles:
                for profile_name in profiles:
                    item = QListWidgetItem(profile_name)
                    self.profile_list.addItem(item)
            else:
                # Journal files exist but no profiles found
                item = QListWidgetItem("No profiles found. Click 'Refresh from Journal Files' to scan for commanders.")
                item.setForeground(QBrush(QColor(136, 136, 136)))  # #888888 color
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
            
            if widget and hasattr(widget, 'update_commander_combo'):
                widget.update_commander_combo()
    
    def select_profile(self, item: QListWidgetItem):
        """Select a profile"""
        commander_name = item.text()
        # Find the main window
        widget = self
        while widget and not isinstance(widget, EliteDangerousApp):
            widget = widget.parent()
        
        if widget and hasattr(widget, 'select_commander'):
            widget.select_commander(commander_name)
            widget.stacked_widget.setCurrentIndex(0)  # Switch to Home


class MonitorScreen(QWidget):
    """Main monitoring screen"""
    
    def __init__(self, event_tracker: EventTracker, parent=None):
        super().__init__(parent)
        self.event_tracker = event_tracker
        self.build_ui()
        self.update_events()
    
    def build_ui(self):
        outer = QVBoxLayout()
        outer.setContentsMargins(0, 0, 0, 0)
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.Shape.NoFrame)
        scroll.setStyleSheet("QScrollArea { background: transparent; border: none; }")
        scroll_content = QWidget()
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
        self.events_list.setWordWrap(True)
        self.events_list.setMinimumHeight(150)
        self.events_list.setStyleSheet("""
            QListWidget {
                background-color: #1e1e1e;
                border: 1px solid #3c3c3c;
                border-radius: 4px;
            }
            QListWidget::item {
                padding: 6px 8px;
                border-bottom: 1px solid #2b2b2b;
            }
            QListWidget::item:selected {
                background-color: #0078d4;
            }
        """)
        self.events_list.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        layout.addWidget(self.events_list, 1)

        # No journal files widget (initially hidden)
        self.no_journal_widget = NoJournalFilesWidget()
        self.no_journal_widget.hide()
        layout.addWidget(self.no_journal_widget)

        scroll_content.setLayout(layout)
        scroll.setWidget(scroll_content)
        outer.addWidget(scroll, 1)
        self.setLayout(outer)
        
        # Check for journal files and show/hide widget
        self.check_journal_files()
    
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
    
    def check_journal_files(self):
        """Check if journal files exist and show/hide appropriate widgets"""
        if not has_journal_files():
            self.events_list.hide()
            self.no_journal_widget.show()
        else:
            self.events_list.show()
            self.no_journal_widget.hide()
    
    def update_events(self):
        """Update the events list only when events changed (newest first). Keeps app responsive."""
        if not has_journal_files():
            self.check_journal_files()
            return

        events = self.event_tracker.get_recent_events(limit=60)
        # Skip full rebuild if nothing changed
        event_sig = (len(events), events[-1].get("timestamp") if events else None)
        if getattr(self, "_last_events_sig", None) == event_sig:
            return
        self._last_events_sig = event_sig

        self.events_list.clear()
        if not events:
            item = QListWidgetItem("No events yet. Start playing Elite Dangerous to see events here.")
            item.setForeground(QBrush(QColor(136, 136, 136)))
            self.events_list.addItem(item)
        else:
            for event in reversed(events):
                text = self._format_event_verbose(event)
                item = QListWidgetItem(text)
                item.setToolTip(text)
                self.events_list.addItem(item)
            self.events_list.scrollToTop()
    
    def _format_event_verbose(self, event: Dict) -> str:
        """Format a single event as a verbose, human-readable line."""
        raw = event.get("raw_data") or {}
        event_type = event.get("event", "Unknown")
        ts = event.get("timestamp") or ""
        time_str = ts[:19].replace("T", " ") if ts else "No time"
        
        # Build verbose description per event type
        parts = []
        if event_type == "LoadGame":
            cmd = raw.get("Commander", "")
            ship = raw.get("Ship", "")
            system = raw.get("StarSystem", "")
            credits = raw.get("Credits")
            cred = f", Credits: {credits:,}" if credits is not None else ""
            parts.append(f"LoadGame — Commander: {cmd}, Ship: {ship}, System: {system}{cred}")
        elif event_type == "FSDJump":
            system = raw.get("StarSystem", "")
            dist = raw.get("JumpDist")
            dist_str = f", JumpDist: {dist:.2f} ly" if dist is not None else ""
            parts.append(f"FSDJump — Arrived at {system}{dist_str}")
        elif event_type == "Location":
            system = raw.get("StarSystem", "")
            body = raw.get("Body", "")
            if body:
                parts.append(f"Location — System: {system}, Body: {body}")
            else:
                parts.append(f"Location — System: {system}")
        elif event_type == "Docked":
            station = raw.get("StationName", "")
            system = raw.get("StarSystem", "")
            parts.append(f"Docked — Station: {station}, System: {system}")
        elif event_type == "Undocked":
            station = raw.get("StationName", "")
            parts.append(f"Undocked — Left {station}" if station else "Undocked")
        elif event_type == "Touchdown":
            body = raw.get("Body", "")
            parts.append(f"Touchdown — Landed on {body}" if body else "Touchdown — Landed")
        elif event_type == "Liftoff":
            body = raw.get("Body", "")
            parts.append(f"Liftoff — Left {body}" if body else "Liftoff")
        elif event_type == "Bounty":
            reward = raw.get("TotalReward", 0)
            victim = raw.get("VictimFaction", "")
            parts.append(f"Bounty — Reward: {reward:,} cr, Victim: {victim}" if victim else f"Bounty — Reward: {reward:,} cr")
        elif event_type == "FactionKillBond":
            reward = raw.get("Reward", 0)
            parts.append(f"Combat bond — Reward: {reward:,} cr")
        elif event_type == "Died":
            killer = raw.get("KillerName") or raw.get("Killers")
            if killer:
                k = killer[0].get("Name", "") if isinstance(killer, list) and killer else str(killer)
                parts.append(f"Died — Killed by {k}")
            else:
                parts.append("Died")
        elif event_type == "Scan":
            scan_type = raw.get("ScanType", "")
            body = raw.get("BodyType", "")
            parts.append(f"Scan — Type: {scan_type}, Body: {body}" if body else f"Scan — {scan_type}")
        elif event_type == "SellExplorationData":
            total = raw.get("TotalEarnings", 0)
            parts.append(f"SellExplorationData — Total earnings: {total:,} cr")
        elif event_type == "MarketBuy":
            item = raw.get("Type", "")
            count = raw.get("Count", 0)
            total = raw.get("TotalCost", 0)
            parts.append(f"MarketBuy — {count} x {item}, Total: {total:,} cr")
        elif event_type == "MarketSell":
            item = raw.get("Type", "")
            count = raw.get("Count", 0)
            total = raw.get("TotalSale", 0)
            parts.append(f"MarketSell — {count} x {item}, Sale: {total:,} cr")
        elif event_type == "MissionAccepted":
            name = raw.get("Name", "")
            parts.append(f"MissionAccepted — {name}" if name else "MissionAccepted")
        elif event_type == "MissionCompleted":
            name = raw.get("Name", "")
            reward = raw.get("Reward", 0)
            part = f"MissionCompleted — {name}, Reward: {reward:,} cr" if name else f"MissionCompleted — Reward: {reward:,} cr"
            # Add rep/influence summary from FactionEffects
            fe_list = raw.get("FactionEffects") or []
            rep_bits = []
            for fe in fe_list:
                if isinstance(fe, dict):
                    r = fe.get("Reputation", "")
                    rt = fe.get("ReputationTrend", "")
                    if r or rt:
                        rep_bits.append(f"{fe.get('Faction', '')}: {r} {rt}".strip())
            if rep_bits:
                part += " | Rep: " + "; ".join(rep_bits)
            # Add materials summary
            mats = raw.get("MaterialsReward") or []
            if mats:
                mat_strs = [f"{m.get('Count', 0)}× {m.get('Name_Localised') or m.get('Name', '')}" for m in mats if isinstance(m, dict)]
                part += " | Materials: " + ", ".join(mat_strs)
            parts.append(part)
        elif event_type == "MissionFailed":
            name = raw.get("Name", "")
            parts.append(f"MissionFailed — {name}" if name else "MissionFailed")
        elif event_type == "RefuelAll":
            cost = raw.get("Cost", 0)
            amount = raw.get("Amount", 0)
            parts.append(f"RefuelAll — Amount: {amount:.1f}, Cost: {cost:,} cr")
        elif event_type == "RepairAll":
            cost = raw.get("Cost", 0)
            parts.append(f"RepairAll — Cost: {cost:,} cr")
        elif event_type == "SupercruiseEntry":
            system = raw.get("StarSystem", "")
            parts.append(f"SupercruiseEntry — {system}" if system else "SupercruiseEntry")
        elif event_type == "SupercruiseExit":
            system = raw.get("StarSystem", "")
            body = raw.get("Body", "")
            parts.append(f"SupercruiseExit — {system}, {body}" if body else f"SupercruiseExit — {system}")
        elif event_type == "FileHeader":
            parts.append("FileHeader — Journal file start")
        elif event_type == "StartJump":
            dest = raw.get("StarSystem") or raw.get("JumpType", "Hyperspace")
            parts.append(f"StartJump — Destination: {dest}")
        elif event_type == "FuelScoop":
            total = raw.get("TotalScooped", 0)
            parts.append(f"FuelScoop — Scooped: {total:.2f} t")
        elif event_type == "Interdicted":
            by = raw.get("Interdictor", "")
            success = raw.get("IsPlayer", False)
            who = "Player" if success else by or "NPC"
            parts.append(f"Interdicted — By: {who}")
        elif event_type == "EscapeInterdiction":
            parts.append("EscapeInterdiction — Escaped")
        elif event_type == "Interdiction":
            victim = raw.get("Interdicted", "")
            success = raw.get("Success", False)
            parts.append(f"Interdiction — Target: {victim}, Success: {success}")
        elif event_type == "ApproachBody":
            body = raw.get("Body", "")
            parts.append(f"ApproachBody — Approaching {body}" if body else "ApproachBody")
        elif event_type == "LeaveBody":
            body = raw.get("Body", "")
            parts.append(f"LeaveBody — Left {body}" if body else "LeaveBody")
        elif event_type == "CodexEntry":
            entry = raw.get("EntryID", "")
            name = raw.get("Name", "")
            parts.append(f"CodexEntry — {name}" if name else f"CodexEntry — {entry}")
        elif event_type == "MaterialCollected":
            mat = raw.get("Name", "")
            category = raw.get("Category", "")
            count = raw.get("Count", 1)
            parts.append(f"MaterialCollected — {count} x {mat} ({category})" if mat else f"MaterialCollected — {count}")
        elif event_type == "MaterialDiscarded":
            mat = raw.get("Name", "")
            count = raw.get("Count", 1)
            parts.append(f"MaterialDiscarded — {count} x {mat}" if mat else "MaterialDiscarded")
        elif event_type == "CollectCargo":
            item = raw.get("Type", "")
            stolen = raw.get("Stolen", False)
            st = " (stolen)" if stolen else ""
            parts.append(f"CollectCargo — {item}{st}" if item else "CollectCargo")
        elif event_type == "EjectCargo":
            item = raw.get("Type", "")
            count = raw.get("Count", 1)
            parts.append(f"EjectCargo — {count} x {item}" if item else "EjectCargo")
        elif event_type == "LaunchSRV":
            parts.append("LaunchSRV — SRV deployed")
        elif event_type == "DockSRV":
            body = raw.get("Body", "")
            parts.append(f"DockSRV — Docked on {body}" if body else "DockSRV")
        elif event_type == "HeatDamage":
            parts.append("HeatDamage — Heat damage sustained")
        elif event_type == "HullDamage":
            health = raw.get("Health", 0)
            parts.append(f"HullDamage — Hull health: {health:.2f}" if health else "HullDamage")
        elif event_type == "ShieldState":
            state = raw.get("ShieldsUp", True)
            parts.append("ShieldState — Shields up" if state else "ShieldState — Shields down")
        elif event_type == "UnderAttack":
            target = raw.get("Target", "")
            parts.append(f"UnderAttack — Target: {target}" if target else "UnderAttack")
        elif event_type == "FSSDiscoveryScan":
            progress = raw.get("Progress", 0)
            bodies = raw.get("BodyCount", 0)
            parts.append(f"FSSDiscoveryScan — Progress: {progress:.2f}, Bodies: {bodies}")
        elif event_type == "SAAScanComplete":
            body = raw.get("BodyName", "")
            parts.append(f"SAAScanComplete — {body}" if body else "SAAScanComplete")
        elif event_type == "MissionAbandoned":
            name = raw.get("Name", "")
            parts.append(f"MissionAbandoned — {name}" if name else "MissionAbandoned")
        elif event_type == "PayBounties":
            amount = raw.get("Amount", 0)
            parts.append(f"PayBounties — Paid {amount:,} cr")
        elif event_type == "PayFines":
            amount = raw.get("Amount", 0)
            parts.append(f"PayFines — Paid {amount:,} cr")
        elif event_type == "RedeemVoucher":
            amount = raw.get("Amount", 0)
            vtype = raw.get("Type", "")
            parts.append(f"RedeemVoucher — {vtype}: {amount:,} cr" if vtype else f"RedeemVoucher — {amount:,} cr")
        elif event_type == "Resurrect":
            option = raw.get("Option", "")
            cost = raw.get("Cost", 0)
            parts.append(f"Resurrect — {option}, Cost: {cost:,} cr" if option else "Resurrect")
        elif event_type == "Shutdown":
            parts.append("Shutdown — Game session ended")
        elif event_type == "Music":
            track = raw.get("MusicTrack", "")
            parts.append(f"Music — {track}" if track else "Music")
        elif event_type == "Reputation":
            # Full verbose: all faction standings (flat or Factions array)
            bits = []
            factions = raw.get("Factions")
            if isinstance(factions, list):
                for fe in factions:
                    if isinstance(fe, dict):
                        n = fe.get("Name", "")
                        r = fe.get("Reputation", "")
                        bits.append(f"{n}: {r}")
            else:
                for k, v in raw.items():
                    if k not in ("event", "timestamp") and v is not None and v != "":
                        bits.append(f"{k}: {v}")
            parts.append(f"Reputation — {'; '.join(bits)}" if bits else "Reputation — (no data)")
        elif event_type == "Rank":
            # Combat, Trade, Explore, Federation, Empire, CQC, Mercenary, Exobiologist
            ranks = []
            for key in ("Combat", "Trade", "Explore", "Federation", "Empire", "CQC", "Mercenary", "Exobiologist"):
                v = raw.get(key)
                if v is not None:
                    ranks.append(f"{key}: {v}")
            parts.append(f"Rank — {', '.join(ranks)}" if ranks else "Rank")
        elif event_type == "Progress":
            # Rank progress (0-100) per category
            progs = []
            for key in ("Combat", "Trade", "Explore", "Empire", "Federation", "CQC", "Mercenary", "Exobiologist"):
                v = raw.get(key)
                if v is not None:
                    progs.append(f"{key}: {v}")
            parts.append(f"Progress — {', '.join(progs)}" if progs else "Progress")
        elif event_type == "PowerplayVoucher":
            power = raw.get("Power", "")
            systems = raw.get("Systems", [])
            amount = raw.get("Amount", 0)
            sys_str = ", ".join(systems) if systems else ""
            parts.append(f"PowerplayVoucher — {power}: {amount:,} cr" + (f" | Systems: {sys_str}" if sys_str else ""))
        elif event_type == "PowerplayCollect":
            power = raw.get("Power", "")
            ptype = raw.get("Type", "")
            count = raw.get("Count", 0)
            parts.append(f"PowerplayCollect — {power}: {count} x {ptype}")
        elif event_type == "PowerplayDeliver":
            power = raw.get("Power", "")
            ptype = raw.get("Type", "")
            count = raw.get("Count", 0)
            parts.append(f"PowerplayDeliver — {power}: {count} x {ptype}")
        elif event_type == "PowerplayJoin":
            power = raw.get("Power", "")
            parts.append(f"PowerplayJoin — Joined {power}" if power else "PowerplayJoin")
        elif event_type == "PowerplayLeave":
            power = raw.get("Power", "")
            parts.append(f"PowerplayLeave — Left {power}" if power else "PowerplayLeave")
        elif event_type == "PowerplayDefect":
            frm = raw.get("FromPower", "")
            to = raw.get("ToPower", "")
            parts.append(f"PowerplayDefect — {frm} → {to}" if frm or to else "PowerplayDefect")
        elif event_type == "PowerplaySalary":
            power = raw.get("Power", "")
            amount = raw.get("Amount", 0)
            parts.append(f"PowerplaySalary — {power}: {amount:,} cr" if power else f"PowerplaySalary — {amount:,} cr")
        elif event_type == "PowerplayVote":
            power = raw.get("Power", "")
            votes = raw.get("Votes", 0)
            system = raw.get("System", "")
            parts.append(f"PowerplayVote — {power}: {votes} votes for {system}" if system else f"PowerplayVote — {power}: {votes} votes")
        elif event_type == "PowerplayFastTrack":
            power = raw.get("Power", "")
            cost = raw.get("Cost", 0)
            parts.append(f"PowerplayFastTrack — {power}: {cost:,} cr" if power else f"PowerplayFastTrack — {cost:,} cr")
        elif event_type == "CommunityGoal":
            goals = raw.get("CurrentGoals", [])
            parts.append(f"CommunityGoal — {len(goals)} goal(s)" if goals else "CommunityGoal")
        elif event_type == "CommunityGoalJoin":
            name = raw.get("Name", "")
            cgid = raw.get("CGID", "")
            parts.append(f"CommunityGoalJoin — {name} (ID {cgid})" if name else "CommunityGoalJoin")
        elif event_type == "CommunityGoalReward":
            name = raw.get("Name", "")
            reward = raw.get("Reward", 0)
            parts.append(f"CommunityGoalReward — {name}: {reward:,} cr" if name else f"CommunityGoalReward — {reward:,} cr")
        else:
            # Generic: show everything logged so we don't miss data
            parts.append(self._format_event_generic(event_type, raw))
        
        return f"[{time_str}] {parts[0]}"

    def _format_event_generic(self, event_type: str, raw: Dict) -> str:
        """Format unknown event with all available fields (verbose)."""
        skip = {"event", "timestamp"}
        extra = []
        for key in sorted(raw.keys()):
            if key in skip:
                continue
            v = raw[key]
            if v is None or v == "":
                continue
            try:
                if isinstance(v, (list, dict)):
                    v_str = json.dumps(v, ensure_ascii=False, default=str)
                    if len(v_str) > 60:
                        v_str = v_str[:60] + "..."
                else:
                    v_str = str(v)
            except Exception:
                v_str = str(v)[:60]
            extra.append(f"{key}: {v_str}")
        return f"{event_type} — {', '.join(extra)}" if extra else event_type


class RevalidateLogsThread(QThread):
    """Thread for scanning new log files when commander is selected (only unprocessed files)."""
    progress = pyqtSignal(int, int)   # current, total (1-based)
    finished = pyqtSignal(bool)       # True = completed, False = cancelled/timed out

    def __init__(self, session_manager: SessionManager):
        super().__init__()
        self.session_manager = session_manager
        self._cancelled = False

    def run(self):
        self._cancelled = False
        try:
            # Only process new files (force_rescan=False); already-processed files are skipped (fast).
            self.session_manager.scan_all_logs(
                force_rescan=False,
                progress_callback=lambda c, t: self.progress.emit(c, t),
                is_cancelled=lambda: self._cancelled,
            )
            self.finished.emit(not self._cancelled)
        except Exception:
            self.finished.emit(False)

    def request_cancel(self):
        """Request cancellation (e.g. on timeout). Thread will exit after current file."""
        self._cancelled = True


# Rank title names for Home screen (faction rank grinding). Index = rank number (0 = first).
# Federation Navy (superpower progression). Journal 0 = None (no rank), 1 = Recruit, etc.
RANK_FEDERATION = (
    "None", "Recruit", "Cadet", "Midshipman", "Petty Officer", "Chief Petty Officer",
    "Warrant Officer", "Ensign", "Lieutenant", "Lieutenant Commander", "Post Commander",
    "Post Captain", "Rear Admiral", "Vice Admiral", "Admiral"
)
# Empire Navy (superpower progression). Journal uses 1-based: 0 = None, 1 = Outsider, 7 = Baron, 14 = King.
RANK_EMPIRE = (
    "None", "Outsider", "Serf", "Master", "Squire", "Knight", "Lord", "Baron",
    "Viscount", "Count", "Earl", "Marquis", "Duke", "Prince", "King"
)
# Combat (0–8)
RANK_COMBAT = (
    "Harmless", "Mostly Harmless", "Novice", "Competent", "Expert",
    "Master", "Dangerous", "Deadly", "Elite"
)
# Trade (0–8)
RANK_TRADE = (
    "Penniless", "Mostly Penniless", "Peddler", "Dealer", "Merchant",
    "Broker", "Entrepreneur", "Tycoon", "Elite"
)
# Exploration (0–8)
RANK_EXPLORATION = (
    "Aimless", "Mostly Aimless", "Scout", "Surveyor", "Trailblazer",
    "Pathfinder", "Ranger", "Pioneer", "Elite"
)
# CQC / Arena (0–8)
RANK_CQC = (
    "Helpless", "Mostly Helpless", "Amateur", "Semi-Professional", "Professional",
    "Champion", "Hero", "Legend", "Elite"
)
# Mercenary (Odyssey on-foot combat, 0–8)
RANK_MERCENARY = (
    "Defenceless", "Mostly Defenceless", "Rookie", "Soldier", "Gunslinger",
    "Warrior", "Gladiator", "Deadeye", "Elite"
)
# Exobiologist (Odyssey biological scanning, 0–8)
RANK_EXOBIOLOGIST = (
    "Directionless", "Mostly Directionless", "Compiler", "Collector", "Cataloguer",
    "Taxonomist", "Ecologist", "Geneticist", "Elite"
)
# Alliance: no formal rank structure (reputation only)


class HomeScreen(QWidget):
    """Home screen: welcome and commander startup snapshot (ranks, progress, powerplay) when a commander is selected."""

    def __init__(self, current_session_tracker: Optional[CurrentSessionTracker] = None, parent=None):
        super().__init__(parent)
        self.current_session_tracker = current_session_tracker
        self.current_commander: Optional[str] = None
        self._last_snapshot_key: Optional[str] = None  # avoid rebuild when data unchanged
        self.build_ui()

    def build_ui(self):
        layout = QVBoxLayout()
        layout.setSpacing(12)
        layout.setContentsMargins(15, 15, 15, 15)

        self.message_label = QLabel("Select a commander first")
        self.message_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.message_label.setStyleSheet("color: #888888; font-size: 16px; padding: 20px;")
        self.message_label.setWordWrap(True)
        layout.addWidget(self.message_label)

        self.startup_container = QWidget()
        self.startup_layout = QVBoxLayout()
        self.startup_layout.setSpacing(12)
        self.startup_container.setLayout(self.startup_layout)
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.Shape.NoFrame)
        scroll.setStyleSheet("QScrollArea { background: transparent; border: none; }")
        scroll.setWidget(self.startup_container)
        layout.addWidget(scroll, 1)
        self.setLayout(layout)

    def _rank_name(self, category: str, value: int) -> str:
        if value is None:
            return "—"
        v = int(value)
        if category == "Federation":
            return RANK_FEDERATION[v] if 0 <= v < len(RANK_FEDERATION) else str(v)
        if category == "Empire":
            return RANK_EMPIRE[v] if 0 <= v < len(RANK_EMPIRE) else str(v)
        if category == "Combat":
            return RANK_COMBAT[v] if 0 <= v < len(RANK_COMBAT) else str(v)
        if category == "Trade":
            return RANK_TRADE[v] if 0 <= v < len(RANK_TRADE) else str(v)
        if category == "Explore":
            return RANK_EXPLORATION[v] if 0 <= v < len(RANK_EXPLORATION) else str(v)
        if category == "CQC":
            return RANK_CQC[v] if 0 <= v < len(RANK_CQC) else str(v)
        if category == "Mercenary":
            return RANK_MERCENARY[v] if 0 <= v < len(RANK_MERCENARY) else str(v)
        if category == "Exobiologist":
            return RANK_EXOBIOLOGIST[v] if 0 <= v < len(RANK_EXOBIOLOGIST) else str(v)
        if category == "Alliance":
            return "Reputation only"
        return str(value)

    def _clear_startup_layout(self):
        while self.startup_layout.count():
            item = self.startup_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

    def update_commander(self, commander_name: Optional[str] = None):
        """Update welcome and startup snapshot display. Rebuilds only when commander or snapshot data changes."""
        self.current_commander = commander_name
        if not commander_name:
            self._last_snapshot_key = None
            self.message_label.setText("Select a commander first")
            self.message_label.setStyleSheet("color: #888888; font-size: 16px; padding: 20px;")
            self.message_label.show()
            if hasattr(self, "startup_layout"):
                self._clear_startup_layout()
            return

        self.message_label.setText(f"Welcome, Commander {commander_name}")
        self.message_label.setStyleSheet("color: #4ec9b0; font-size: 18px; padding: 12px 20px; font-weight: bold;")
        self.message_label.show()

        if not self.current_session_tracker:
            return
        stats = self.current_session_tracker.get_statistics()
        snap = stats.get("startup_snapshot") or {}
        # Only rebuild content when snapshot actually changed (so periodic refresh doesn't flicker)
        snapshot_key = f"{commander_name}|{json.dumps(snap, sort_keys=True)}"
        if snapshot_key == self._last_snapshot_key:
            return
        self._last_snapshot_key = snapshot_key
        self._clear_startup_layout()

        section_style = "QFrame { background-color: #2b2b2b; border: 1px solid #3c3c3c; border-radius: 6px; padding: 12px; }"
        title_style = "color: #4ec9b0; font-size: 13px; font-weight: bold;"
        label_style = "color: #cccccc; font-size: 11px;"

        # Load game (ship, credits, system)
        load_game = snap.get("load_game") or {}
        if load_game:
            f = QFrame()
            f.setStyleSheet(section_style)
            lay = QVBoxLayout()
            t = QLabel("Last session start")
            t.setStyleSheet(title_style)
            lay.addWidget(t)
            parts = []
            if load_game.get("Ship"):
                parts.append(f"Ship: {load_game.get('Ship')}")
            if load_game.get("Credits") is not None:
                parts.append(f"Credits: {load_game.get('Credits'):,}")
            if load_game.get("StarSystem"):
                parts.append(f"System: {load_game.get('StarSystem')}")
            if load_game.get("GameMode"):
                parts.append(f"Mode: {load_game.get('GameMode')}")
            if parts:
                lbl = QLabel(" • ".join(parts))
                lbl.setStyleSheet(label_style)
                lbl.setWordWrap(True)
                lay.addWidget(lbl)
            f.setLayout(lay)
            self.startup_layout.addWidget(f)

        # Ranks
        ranks = snap.get("ranks") or {}
        if ranks:
            f = QFrame()
            f.setStyleSheet(section_style)
            lay = QVBoxLayout()
            t = QLabel("Ranks (for faction grind)")
            t.setStyleSheet(title_style)
            lay.addWidget(t)
            grid = QGridLayout()
            row = 0
            for key in ("Combat", "Trade", "Explore", "Empire", "Federation", "CQC", "Mercenary", "Exobiologist"):
                v = ranks.get(key)
                if v is not None:
                    name = self._rank_name(key, v)
                    k_lbl = QLabel(key + ":")
                    v_lbl = QLabel(f"Rank {v} — {name}")
                    k_lbl.setStyleSheet(label_style)
                    v_lbl.setStyleSheet(label_style)
                    grid.addWidget(k_lbl, row, 0)
                    grid.addWidget(v_lbl, row, 1)
                    row += 1
            lay.addLayout(grid)
            f.setLayout(lay)
            self.startup_layout.addWidget(f)

        # Progress to next rank (%)
        progress = snap.get("progress") or {}
        if progress:
            f = QFrame()
            f.setStyleSheet(section_style)
            lay = QVBoxLayout()
            t = QLabel("Progress to next rank (%)")
            t.setStyleSheet(title_style)
            lay.addWidget(t)
            grid = QGridLayout()
            row = 0
            for key in ("Combat", "Trade", "Explore", "Empire", "Federation", "CQC", "Mercenary", "Exobiologist"):
                v = progress.get(key)
                if v is not None:
                    k_lbl = QLabel(key + ":")
                    v_lbl = QLabel(f"{v}%")
                    k_lbl.setStyleSheet(label_style)
                    v_lbl.setStyleSheet(label_style)
                    grid.addWidget(k_lbl, row, 0)
                    grid.addWidget(v_lbl, row, 1)
                    row += 1
            lay.addLayout(grid)
            f.setLayout(lay)
            self.startup_layout.addWidget(f)

        # Powerplay
        powerplay = snap.get("powerplay") or {}
        if powerplay and powerplay.get("Power"):
            f = QFrame()
            f.setStyleSheet(section_style)
            lay = QVBoxLayout()
            t = QLabel("Powerplay")
            t.setStyleSheet(title_style)
            lay.addWidget(t)
            parts = [f"Power: {powerplay.get('Power')}"]
            if powerplay.get("Rank") is not None:
                parts.append(f"Rank: {powerplay.get('Rank')}")
            if powerplay.get("Merits") is not None:
                parts.append(f"Merits: {powerplay.get('Merits')}")
            if powerplay.get("Votes") is not None:
                parts.append(f"Votes: {powerplay.get('Votes')}")
            if powerplay.get("TimePledged") is not None:
                days = powerplay.get("TimePledged", 0) // 86400
                parts.append(f"Pledged: {days} days")
            lbl = QLabel(" • ".join(parts))
            lbl.setStyleSheet(label_style)
            lbl.setWordWrap(True)
            lay.addWidget(lbl)
            f.setLayout(lay)
            self.startup_layout.addWidget(f)

        # Superpower reputation (startup -100 to +100)
        rep = snap.get("reputation") or {}
        if rep:
            f = QFrame()
            f.setStyleSheet(section_style)
            lay = QVBoxLayout()
            t = QLabel("Superpower reputation (at session start)")
            t.setStyleSheet(title_style)
            lay.addWidget(t)
            grid = QGridLayout()
            for row, key in enumerate(("Empire", "Federation", "Independent", "Alliance")):
                v = rep.get(key)
                if v is not None:
                    k_lbl = QLabel(key + ":")
                    v_lbl = QLabel(str(v))
                    k_lbl.setStyleSheet(label_style)
                    v_lbl.setStyleSheet(label_style)
                    grid.addWidget(k_lbl, row, 0)
                    grid.addWidget(v_lbl, row, 1)
            lay.addLayout(grid)
            f.setLayout(lay)
            self.startup_layout.addWidget(f)

        if not any([load_game, ranks, progress, powerplay, rep]):
            hint = QLabel("No startup data yet. Start Elite Dangerous and load in; the next time you select this commander, ranks and progress will appear here.")
            hint.setStyleSheet("color: #666666; font-size: 11px;")
            hint.setWordWrap(True)
            self.startup_layout.addWidget(hint)

        self.startup_layout.addStretch()


class EliteDangerousApp(QMainWindow):
    """Main application window"""
    
    def __init__(self):
        try:
            logger.info("Initializing EliteDangerousApp...")
            super().__init__()
            
            logger.info("Creating managers and trackers...")
            self.profile_manager = ProfileManager()
            self.event_tracker = EventTracker(self.profile_manager)
            self.session_manager = SessionManager()
            self.current_session_tracker = CurrentSessionTracker()
            self.log_monitor = LogMonitor(self.on_log_event)
            self.monitor_thread: Optional[LogMonitorThread] = None
            self.revalidate_thread: Optional[RevalidateLogsThread] = None
            self.is_monitoring = False
            self.current_commander = None
            
            logger.info("Setting up window...")
            self.setWindowTitle(f"{APP_NAME} v{APP_VERSION} - Elite Dangerous Log Analyzer © {APP_AUTHOR}")
            self.setGeometry(100, 100, 900, 700)
            self.setMinimumSize(500, 400)
            
            # Apply dark theme
            self.apply_dark_theme()
            logger.info("Dark theme applied")
        except Exception as e:
            logger.critical(f"Error during EliteDangerousApp initialization: {e}")
            logger.critical(traceback.format_exc())
            raise  # Re-raise so it gets caught by the global handler
        
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

        # Commander switching bar: label + combo + refresh
        commander_label = QLabel("Commander:")
        commander_label.setStyleSheet("color: white; font-weight: bold; font-size: 11pt;")
        nav_layout.addWidget(commander_label)

        self.commander_combo = QComboBox()
        self.commander_combo.setMinimumWidth(200)
        self.commander_combo.setStyleSheet("""
            QComboBox {
                background-color: #1e88e5;
                color: white;
                border: 2px solid white;
                padding: 6px 12px;
                border-radius: 4px;
                font-weight: bold;
                font-size: 11pt;
            }
            QComboBox:hover {
                background-color: #42a5f5;
            }
            QComboBox::drop-down {
                border: none;
            }
            QComboBox QAbstractItemView {
                background-color: #2b2b2b;
                color: white;
            }
        """)
        self.commander_combo.currentIndexChanged.connect(self._on_commander_combo_changed)
        nav_layout.addWidget(self.commander_combo)

        refresh_cmd_btn = QPushButton("🔄")
        refresh_cmd_btn.setToolTip("Refresh commander list from journal files")
        refresh_cmd_btn.setStyleSheet("""
            QPushButton {
                background-color: #1e88e5;
                color: white;
                border: 2px solid white;
                padding: 6px 10px;
                border-radius: 4px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #42a5f5;
            }
        """)
        refresh_cmd_btn.clicked.connect(self.refresh_commanders)
        nav_layout.addWidget(refresh_cmd_btn)

        nav_layout.addStretch()

        # Create stacked widget (expands to fill resizable window)
        self.stacked_widget = QStackedWidget()
        self.stacked_widget.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)

        # Create screens: Home, Monitor, Profiles, Dashboard, Missions & Reputation
        self.home_screen = HomeScreen(self.current_session_tracker)
        self.monitor_screen = MonitorScreen(self.event_tracker)
        self.profile_screen = ProfileScreen(self.profile_manager)
        self.dashboard_screen = DashboardScreen(self.session_manager, self.current_session_tracker)
        self.missions_reputation_screen = MissionsReputationScreen(self.current_session_tracker)

        self.stacked_widget.addWidget(self.home_screen)
        self.stacked_widget.addWidget(self.monitor_screen)
        self.stacked_widget.addWidget(self.profile_screen)
        self.stacked_widget.addWidget(self.dashboard_screen)
        self.stacked_widget.addWidget(self.missions_reputation_screen)

        # Navigation buttons (indices: Home=0, Monitor=1, Profiles=2, Dashboard=3, Missions=4)
        self.home_btn = QPushButton("Home")
        self.home_btn.clicked.connect(lambda: self.stacked_widget.setCurrentIndex(0))
        nav_layout.addWidget(self.home_btn)

        self.monitor_btn = QPushButton("Monitor")
        self.monitor_btn.clicked.connect(lambda: self.stacked_widget.setCurrentIndex(1))
        nav_layout.addWidget(self.monitor_btn)

        self.profiles_btn = QPushButton("Profiles")
        self.profiles_btn.clicked.connect(lambda: self.stacked_widget.setCurrentIndex(2))
        nav_layout.addWidget(self.profiles_btn)

        self.dashboard_btn = QPushButton("Dashboard")
        self.dashboard_btn.clicked.connect(lambda: self.stacked_widget.setCurrentIndex(3))
        nav_layout.addWidget(self.dashboard_btn)

        self.missions_btn = QPushButton("Missions")
        self.missions_btn.clicked.connect(lambda: self.stacked_widget.setCurrentIndex(4))
        nav_layout.addWidget(self.missions_btn)
        
        nav_bar.setLayout(nav_layout)
        main_layout.addWidget(nav_bar)

        # Connect stacked widget to update button styles when screen changes
        self.stacked_widget.currentChanged.connect(self.update_nav_button_styles)

        # Set initial screen to Home (index 0) and button style
        self.stacked_widget.setCurrentIndex(0)
        self.update_nav_button_styles(0)

        main_layout.addWidget(self.stacked_widget)
        # Content area takes all remaining space when window is resized
        main_layout.setStretchFactor(self.stacked_widget, 1)
        central_widget.setLayout(main_layout)

        # Status bar for revalidation message and progress
        self.status_bar = QStatusBar()
        self.revalidate_progress = QProgressBar()
        self.revalidate_progress.setMinimumWidth(120)
        self.revalidate_progress.setMaximumHeight(18)
        self.revalidate_progress.setVisible(False)
        self.status_bar.addPermanentWidget(self.revalidate_progress)
        self.setStatusBar(self.status_bar)

        # Timeout for log revalidation (health check)
        self.revalidate_timeout_timer = QTimer(self)
        self.revalidate_timeout_timer.setSingleShot(True)
        self.revalidate_timeout_timer.timeout.connect(self._on_revalidate_timeout)

        # Populate commander combo (no selection at start)
        self.update_commander_combo()
        
        # Add File and Help menus
        self.create_menus()
        
        # Refresh commander list from journals on startup (do not auto-select)
        self.refresh_commanders()

        # Start monitoring
        self.start_monitoring()
        
        # Set up timer for UI updates (2s to reduce CPU and avoid sluggishness)
        self.update_timer = QTimer()
        self.update_timer.timeout.connect(self.update_ui)
        self.update_timer.start(3000)  # Update every 3 seconds (responsive, less CPU)
        
        # Set up timer for checking new log files for sessions
        self.session_check_timer = QTimer()
        self.session_check_timer.timeout.connect(self.check_new_sessions)
        self.session_check_timer.start(30000)  # Check every 30 seconds
        
        # Initial scan of all logs (only processes new ones) - do this after UI is ready
        # Use a single-shot timer to do it after the window is shown
        QTimer.singleShot(1000, self.initial_session_scan)
    
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

        # Update styles based on active screen (Home=0, Monitor=1, Profiles=2, Dashboard=3, Missions=4)
        self.home_btn.setStyleSheet(active_style if index == 0 else inactive_style)
        self.monitor_btn.setStyleSheet(active_style if index == 1 else inactive_style)
        self.profiles_btn.setStyleSheet(active_style if index == 2 else inactive_style)
        self.dashboard_btn.setStyleSheet(active_style if index == 3 else inactive_style)
        self.missions_btn.setStyleSheet(active_style if index == 4 else inactive_style)
    
    def refresh_commanders(self):
        """Refresh commander list by scanning journal files"""
        self.profile_manager.refresh_from_journals()
        self.update_commander_combo()
        self.profile_screen.refresh_profile_list()

    def update_commander_combo(self):
        """Populate the commander combo box from profiles"""
        self.commander_combo.blockSignals(True)
        self.commander_combo.clear()
        profiles = self.profile_manager.list_profiles()
        self.commander_combo.addItem("")  # empty = "no selection"
        for profile_name in profiles:
            self.commander_combo.addItem(profile_name)
        # Restore selection to current commander if any
        if self.current_commander and self.current_commander in profiles:
            idx = profiles.index(self.current_commander) + 1  # +1 for empty item
            self.commander_combo.setCurrentIndex(idx)
        else:
            self.commander_combo.setCurrentIndex(0)
        self.commander_combo.blockSignals(False)

    def _on_commander_combo_changed(self, index: int):
        """Handle commander selection from combo box"""
        if index <= 0:
            return
        name = self.commander_combo.currentText()
        if name and name != self.current_commander:
            self.select_commander(name)

    def select_commander(self, commander_name: str):
        """Select a commander and revalidate all logs"""
        if not commander_name or "No profiles" in commander_name:
            return

        self.current_commander = commander_name
        self.event_tracker.set_current_commander(commander_name)
        self.monitor_screen.update_commander_display(commander_name)
        self.dashboard_screen.update_commander(commander_name)
        self.home_screen.update_commander(commander_name)
        self.update_commander_combo()

        # Only run revalidation if there are new log files to process; otherwise skip (instant).
        to_process = self.session_manager.get_log_files_to_process()
        if not to_process:
            self.status_bar.showMessage("Logs revalidated. (No new log files.)", 5000)
            snapshot = get_startup_snapshot(self.session_manager.log_dir)
            self.current_session_tracker.set_startup_snapshot(snapshot)
            self.home_screen.update_commander(commander_name)
            if self.stacked_widget.currentIndex() == 3:
                self.dashboard_screen.refresh_data()
            return

        # Show progress and run scan in background (only processes new files)
        self.status_bar.showMessage("Revalidating logs...")
        self.revalidate_progress.setVisible(True)
        self.revalidate_progress.setRange(0, 0)  # indeterminate until we get first progress
        self.revalidate_progress.setValue(0)
        self.revalidate_thread = RevalidateLogsThread(self.session_manager)
        self.revalidate_thread.progress.connect(self._on_revalidate_progress)
        self.revalidate_thread.finished.connect(self._on_revalidate_finished)
        self.revalidate_thread.start()
        self.revalidate_timeout_timer.start(REVALIDATE_TIMEOUT_MS)

    def _on_revalidate_progress(self, current: int, total: int):
        """Update progress bar during log revalidation"""
        if total > 0 and self.revalidate_progress.maximum() != total:
            self.revalidate_progress.setRange(0, total)
        self.revalidate_progress.setValue(min(current, total))

    def _on_revalidate_timeout(self):
        """Revalidation took too long; request cancel and notify user"""
        if self.revalidate_thread is None:
            return
        self.revalidate_thread.request_cancel()
        self.status_bar.showMessage("Log revalidation is taking too long; cancelling…")

    def _on_revalidate_finished(self, success: bool):
        """Called when log revalidation thread completes (success=True) or is cancelled/timed out (success=False)"""
        self.revalidate_timeout_timer.stop()
        self.revalidate_progress.setVisible(False)
        self.revalidate_progress.setRange(0, 100)
        self.revalidate_progress.setValue(0)
        self.revalidate_thread = None
        if success:
            self.status_bar.showMessage("Logs revalidated.", 5000)
            snapshot = get_startup_snapshot(self.session_manager.log_dir)
            self.current_session_tracker.set_startup_snapshot(snapshot)
            self.home_screen.update_commander(self.current_commander)
            if self.stacked_widget.currentIndex() == 3:
                self.dashboard_screen.refresh_data()
        else:
            self.status_bar.showMessage("Log revalidation was cancelled or timed out.", 8000)
            QMessageBox.warning(
                self,
                "Log revalidation",
                "Log revalidation did not complete. It may have been cancelled because it took too long, or an error occurred.\n\n"
                "You can try selecting the commander again, or check the journal folder and application logs if this persists.",
                QMessageBox.StandardButton.Ok,
            )
    
    def on_log_event(self, event_data: Dict):
        """Handle events from log monitor"""
        if self.current_commander:
            self.event_tracker.process_event(event_data)
        
        # Update current session tracker
        self.current_session_tracker.process_event(event_data)
    
    def start_monitoring(self):
        """Start monitoring log files"""
        if not self.is_monitoring:
            self.monitor_thread = LogMonitorThread(self.log_monitor)
            self.monitor_thread.start()
            self.is_monitoring = True
            self.monitor_screen.update_status(True)
    
    def stop_monitoring(self):
        """Stop monitoring log files (with timeout so shutdown does not hang)"""
        if self.is_monitoring and self.monitor_thread:
            self.monitor_thread.stop_monitoring()
            if not self.monitor_thread.wait(5000):
                logger.warning("Log monitor thread did not exit within 5 seconds")
            self.monitor_thread = None
            self.is_monitoring = False
            if self.monitor_screen:
                self.monitor_screen.update_status(False)
    
    def create_menus(self):
        """Create File and Help menus"""
        # File menu
        file_menu = self.menuBar().addMenu("&File")
        exit_action = QAction("E&xit", self)
        exit_action.setShortcut("Ctrl+Q")
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)
        # Help menu
        self.create_help_menu()

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
        """Periodically update the UI. Only refresh the visible tab to keep the app responsive."""
        try:
            idx = self.stacked_widget.currentIndex()
            if idx == 0:
                # Home: refresh from tracker so new Rank/log data is shown when logs are updated
                self.home_screen.update_commander(self.current_commander)
            elif idx == 1:
                self.monitor_screen.update_events()
            elif idx == 3:
                self.dashboard_screen.update_current_session()
            elif idx == 4:
                self.missions_reputation_screen.refresh_data()
        except Exception as e:
            logger.error(f"Error in update_ui: {e}")
            logger.error(traceback.format_exc())
    
    def initial_session_scan(self):
        """Perform initial scan of all logs after UI is ready"""
        try:
            logger.info("Starting initial session scan...")
            self.session_manager.scan_all_logs()
            logger.info("Initial session scan completed")
        except Exception as e:
            logger.error(f"Error during initial session scan: {e}")
            import traceback
            traceback.print_exc()
            # Continue anyway - sessions can be scanned later
    
    def check_new_sessions(self):
        """Check for new log files and process them for sessions"""
        try:
            # Scan for new log files (only processes unprocessed ones)
            self.session_manager.scan_all_logs()
            
            # Refresh dashboard if it's the current screen
            if self.stacked_widget.currentIndex() == 3:
                self.dashboard_screen.refresh_data()
        except Exception as e:
            logger.error(f"Error checking for new sessions: {e}")
    
    def closeEvent(self, event):
        """Handle window close: stop timers and threads, then quit gracefully."""
        # Stop timers so they don't keep the event loop alive
        if hasattr(self, "update_timer") and self.update_timer:
            self.update_timer.stop()
        if hasattr(self, "session_check_timer") and self.session_check_timer:
            self.session_check_timer.stop()
        if hasattr(self, "revalidate_timeout_timer") and self.revalidate_timeout_timer:
            self.revalidate_timeout_timer.stop()
        # Cancel revalidation if running and wait briefly
        if getattr(self, "revalidate_thread", None) is not None:
            self.revalidate_thread.request_cancel()
            self.revalidate_thread.wait(2000)
            self.revalidate_thread = None
        # Stop log monitoring (observer + thread, with timeouts)
        self.stop_monitoring()
        # Ensure application quits when this window closes
        app = QApplication.instance()
        if app:
            app.quit()
        event.accept()


def main():
    """Main entry point"""
    try:
        logger.info("="*80)
        logger.info(f"Starting {APP_NAME} v{APP_VERSION}")
        logger.info("="*80)

        app = QApplication.instance() or QApplication(sys.argv)
        app.setStyle('Fusion')  # Use Fusion style for better cross-platform look
        app.setQuitOnLastWindowClosed(True)  # Exit when main window is closed

        logger.info("Creating main window...")
        window = EliteDangerousApp()
        logger.info("Showing window...")
        window.show()
        logger.info("Application started successfully")
        
        sys.exit(app.exec())
    except Exception as e:
        logger.critical(f"Fatal error in main(): {e}")
        logger.critical(traceback.format_exc())
        
        # Try to show error to user if possible
        try:
            from PyQt6.QtWidgets import QMessageBox
            error_box = QMessageBox()
            error_box.setIcon(QMessageBox.Icon.Critical)
            error_box.setWindowTitle("Fatal Error")
            error_box.setText(f"Application crashed:\n\n{str(e)}\n\nCheck logs/app.log for details.")
            error_box.exec()
        except:
            # If we can't show a message box, at least print it
            print(f"Fatal error: {e}")
            print("Check logs/app.log for details")
        
        sys.exit(1)


if __name__ == "__main__":
    main()
