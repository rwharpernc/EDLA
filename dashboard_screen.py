"""
Dashboard screen for displaying session statistics and history
"""
from typing import Optional
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QListWidget, QListWidgetItem,
    QFrame, QPushButton, QScrollArea, QGridLayout, QTabWidget, QTextEdit, QStackedWidget
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont, QBrush, QColor
from datetime import datetime
from session_manager import SessionManager
from current_session_tracker import CurrentSessionTracker
from no_journal_widget import NoJournalFilesWidget, has_journal_files


class DashboardScreen(QWidget):
    """Dashboard screen showing session statistics and history"""
    
    def __init__(self, session_manager: SessionManager, current_session_tracker: CurrentSessionTracker, parent=None):
        super().__init__(parent)
        self.session_manager = session_manager
        self.current_session_tracker = current_session_tracker
        self.current_commander: Optional[str] = None
        self.view_mode = "current"  # "current" or "historical"
        self.build_ui()
        try:
            self.refresh_data()
        except Exception as e:
            print(f"Error refreshing dashboard data on init: {e}")
            import traceback
            traceback.print_exc()
    
    def build_ui(self):
        """Build the dashboard UI"""
        layout = QVBoxLayout()
        layout.setSpacing(10)
        layout.setContentsMargins(15, 15, 15, 15)
        
        # Title
        title = QLabel("Session Dashboard")
        title_font = QFont()
        title_font.setPointSize(18)
        title_font.setBold(True)
        title.setFont(title_font)
        layout.addWidget(title)
        
        # Commander display
        self.commander_label = QLabel("No commander selected")
        self.commander_label.setStyleSheet("color: #888888; font-size: 12px;")
        layout.addWidget(self.commander_label)
        
        # View mode toggle and refresh button
        button_layout = QHBoxLayout()
        
        # View mode toggle
        self.current_session_btn = QPushButton("Current Session")
        self.current_session_btn.setCheckable(True)
        self.current_session_btn.setChecked(True)
        self.current_session_btn.clicked.connect(lambda: self.set_view_mode("current"))
        self.current_session_btn.setStyleSheet("""
            QPushButton {
                background-color: #0078d4;
                color: white;
                border: none;
                padding: 8px 16px;
                border-radius: 4px;
                font-weight: bold;
            }
            QPushButton:checked {
                background-color: #4ec9b0;
            }
            QPushButton:hover {
                background-color: #106ebe;
            }
        """)
        button_layout.addWidget(self.current_session_btn)
        
        self.historical_btn = QPushButton("Historical")
        self.historical_btn.setCheckable(True)
        self.historical_btn.clicked.connect(lambda: self.set_view_mode("historical"))
        self.historical_btn.setStyleSheet("""
            QPushButton {
                background-color: #2b2b2b;
                color: white;
                border: 1px solid #3c3c3c;
                padding: 8px 16px;
                border-radius: 4px;
                font-weight: bold;
            }
            QPushButton:checked {
                background-color: #4ec9b0;
            }
            QPushButton:hover {
                background-color: #3c3c3c;
            }
        """)
        button_layout.addWidget(self.historical_btn)
        
        button_layout.addStretch()
        
        refresh_btn = QPushButton("🔄 Refresh Sessions")
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
        refresh_btn.clicked.connect(self.refresh_sessions)
        button_layout.addWidget(refresh_btn)
        layout.addLayout(button_layout)
        
        # Statistics section with tabs
        self.stats_label = QLabel("Current Session Statistics")
        stats_font = QFont()
        stats_font.setPointSize(12)
        stats_font.setBold(True)
        self.stats_label.setFont(stats_font)
        layout.addWidget(self.stats_label)
        
        # Create stacked widget for current vs historical views
        self.view_stack = QStackedWidget()
        
        # Current session view
        self.current_session_widget = QWidget()
        self.current_session_layout = QVBoxLayout()
        self.current_session_widget.setLayout(self.current_session_layout)
        
        # Historical view (existing stats tabs)
        self.historical_widget = QWidget()
        self.historical_layout = QVBoxLayout()
        self.historical_widget.setLayout(self.historical_layout)
        
        # Current session stats frame
        self.current_stats_frame = QFrame()
        self.current_stats_frame.setStyleSheet("QFrame { background-color: #2b2b2b; border-radius: 5px; padding: 10px; }")
        self.current_stats_layout = QGridLayout()
        self.current_stats_layout.setSpacing(10)
        self.current_stats_frame.setLayout(self.current_stats_layout)
        self.current_session_layout.addWidget(self.current_stats_frame)
        
        # Historical view - Create tab widget for different stat categories
        self.stats_tabs = QTabWidget()
        self.stats_tabs.setStyleSheet("""
            QTabWidget::pane {
                border: 1px solid #3c3c3c;
                background-color: #2b2b2b;
                border-radius: 5px;
            }
            QTabBar::tab {
                background-color: #1e1e1e;
                color: #888888;
                padding: 8px 16px;
                border: 1px solid #3c3c3c;
                border-bottom: none;
                border-top-left-radius: 4px;
                border-top-right-radius: 4px;
            }
            QTabBar::tab:selected {
                background-color: #2b2b2b;
                color: #4ec9b0;
            }
        """)
        
        # Overview tab
        self.overview_frame = QFrame()
        self.overview_frame.setStyleSheet("QFrame { background-color: #2b2b2b; border-radius: 5px; padding: 10px; }")
        self.overview_layout = QGridLayout()
        self.overview_layout.setSpacing(10)
        self.overview_frame.setLayout(self.overview_layout)
        self.stats_tabs.addTab(self.overview_frame, "Overview")
        
        # Combat tab
        self.combat_frame = QFrame()
        self.combat_frame.setStyleSheet("QFrame { background-color: #2b2b2b; border-radius: 5px; padding: 10px; }")
        self.combat_layout = QGridLayout()
        self.combat_layout.setSpacing(10)
        self.combat_frame.setLayout(self.combat_layout)
        self.stats_tabs.addTab(self.combat_frame, "Combat")
        
        # Exploration tab
        self.exploration_frame = QFrame()
        self.exploration_frame.setStyleSheet("QFrame { background-color: #2b2b2b; border-radius: 5px; padding: 10px; }")
        self.exploration_layout = QGridLayout()
        self.exploration_layout.setSpacing(10)
        self.exploration_frame.setLayout(self.exploration_layout)
        self.stats_tabs.addTab(self.exploration_frame, "Exploration")
        
        # Trading tab
        self.trading_frame = QFrame()
        self.trading_frame.setStyleSheet("QFrame { background-color: #2b2b2b; border-radius: 5px; padding: 10px; }")
        self.trading_layout = QGridLayout()
        self.trading_layout.setSpacing(10)
        self.trading_frame.setLayout(self.trading_layout)
        self.stats_tabs.addTab(self.trading_frame, "Trading")
        
        # Missions tab
        self.missions_frame = QFrame()
        self.missions_frame.setStyleSheet("QFrame { background-color: #2b2b2b; border-radius: 5px; padding: 10px; }")
        self.missions_layout = QGridLayout()
        self.missions_layout.setSpacing(10)
        self.missions_frame.setLayout(self.missions_layout)
        self.stats_tabs.addTab(self.missions_frame, "Missions")
        
        self.historical_layout.addWidget(self.stats_tabs)
        
        # Add both views to stack
        self.view_stack.addWidget(self.current_session_widget)
        self.view_stack.addWidget(self.historical_widget)
        self.view_stack.setCurrentIndex(0)  # Start with current session
        
        layout.addWidget(self.view_stack)
        
        # Sessions list section
        sessions_label = QLabel("Session History")
        sessions_font = QFont()
        sessions_font.setPointSize(12)
        sessions_font.setBold(True)
        sessions_label.setFont(sessions_font)
        layout.addWidget(sessions_label)
        
        # Session list
        self.sessions_list = QListWidget()
        self.sessions_list.setStyleSheet("""
            QListWidget {
                background-color: #1e1e1e;
                border: 1px solid #3c3c3c;
                border-radius: 4px;
            }
            QListWidget::item {
                padding: 8px;
                border-bottom: 1px solid #2b2b2b;
            }
            QListWidget::item:selected {
                background-color: #0078d4;
            }
        """)
        self.sessions_list.itemDoubleClicked.connect(self.show_session_details)
        layout.addWidget(self.sessions_list)
        
        # No journal files widget (initially hidden)
        self.no_journal_widget = NoJournalFilesWidget()
        self.no_journal_widget.hide()
        layout.addWidget(self.no_journal_widget)
        
        self.setLayout(layout)
    
    def update_commander(self, commander_name: Optional[str] = None):
        """Update the current commander"""
        self.current_commander = commander_name
        
        # Reset current session tracker if commander changed
        if commander_name and self.current_session_tracker.commander != commander_name:
            self.current_session_tracker.reset()
        
        if commander_name:
            self.commander_label.setText(f"Commander: {commander_name}")
            self.commander_label.setStyleSheet("color: #4ec9b0; font-size: 12px; font-weight: bold;")
        else:
            self.commander_label.setText("No commander selected")
            self.commander_label.setStyleSheet("color: #888888; font-size: 12px;")
            # Reset tracker if no commander selected
            self.current_session_tracker.reset()
        
        self.refresh_data()
    
    def refresh_sessions(self):
        """Refresh sessions by scanning log files"""
        self.session_manager.scan_all_logs()
        self.refresh_data()
    
    def set_view_mode(self, mode: str):
        """Switch between current session and historical views"""
        self.view_mode = mode
        if mode == "current":
            self.view_stack.setCurrentIndex(0)
            self.current_session_btn.setChecked(True)
            self.historical_btn.setChecked(False)
            self.stats_label.setText("Current Session Statistics")
            self.update_current_session()
        else:
            self.view_stack.setCurrentIndex(1)
            self.current_session_btn.setChecked(False)
            self.historical_btn.setChecked(True)
            self.stats_label.setText("Historical Statistics")
            self.update_statistics()
        
        # Update sessions list visibility
        self.update_sessions_list()
    
    def refresh_data(self):
        """Refresh all dashboard data"""
        try:
            if self.view_mode == "current":
                self.update_current_session()
            else:
                self.update_statistics()
            self.update_sessions_list()
        except Exception as e:
            print(f"Error refreshing dashboard data: {e}")
            import traceback
            traceback.print_exc()
    
    def update_current_session(self):
        """Update current session statistics display"""
        try:
            self._clear_layout(self.current_stats_layout)
            
            if not self.current_session_tracker.has_active_session():
                no_session_label = QLabel("No active session. Start Elite Dangerous to begin tracking.")
                no_session_label.setStyleSheet("color: #888888; font-size: 12px; padding: 20px;")
                self.current_stats_layout.addWidget(no_session_label, 0, 0, 1, 2)
                return
            
            stats = self.current_session_tracker.get_statistics()
            
            # Credits section
            credits = stats.get("credits", {})
            credits_stats = [
                ("Current Credits", f"{credits.get('current', 0):,}" if credits.get('current') is not None else "N/A"),
                ("Credits Change", f"{credits.get('change', 0):+,}" if credits.get('change') is not None else "0"),
                ("Money Earned", f"{credits.get('earned', 0):,}"),
                ("Money Spent", f"{credits.get('spent', 0):,}"),
            ]
            self._add_stat_cards(self.current_stats_layout, credits_stats, start_row=0)
            
            # Travel section
            travel = stats.get("travel", {})
            travel_stats = [
                ("Light Years Traveled", f"{travel.get('light_years', 0):,.2f}"),
                ("Jumps", str(travel.get("jumps", 0))),
                ("Systems Visited", str(travel.get("systems_visited", 0))),
                ("Stations Visited", str(travel.get("stations_visited", 0))),
                ("Planets Landed", str(travel.get("planets_landed", 0))),
            ]
            self._add_stat_cards(self.current_stats_layout, travel_stats, start_row=2)
            
            # Combat section
            combat = stats.get("combat", {})
            combat_stats = [
                ("Kills", str(combat.get("kills", 0))),
                ("Deaths", str(combat.get("deaths", 0))),
                ("Bounties Earned", f"{combat.get('bounties_earned', 0):,}"),
                ("Combat Bonds", f"{combat.get('combat_bonds', 0):,}"),
            ]
            self._add_stat_cards(self.current_stats_layout, combat_stats, start_row=5)
            
            # Additional info
            info_text = f"Current System: {stats.get('current_system', 'Unknown')} | Current Ship: {stats.get('current_ship', 'Unknown')}"
            info_label = QLabel(info_text)
            info_label.setStyleSheet("color: #666666; font-size: 10px; padding: 5px;")
            self.current_stats_layout.addWidget(info_label, 7, 0, 1, 2)
        except Exception as e:
            print(f"Error updating current session: {e}")
            import traceback
            traceback.print_exc()
    
    def _add_stat_cards(self, layout, stat_items, start_row=0):
        """Add statistic cards to a layout"""
        row = start_row
        col = 0
        for label_text, value_text in stat_items:
            stat_frame = QFrame()
            stat_frame.setStyleSheet("""
                QFrame {
                    background-color: #1e1e1e;
                    border: 1px solid #3c3c3c;
                    border-radius: 4px;
                    padding: 10px;
                }
            """)
            stat_layout = QVBoxLayout()
            stat_layout.setSpacing(5)
            
            value_label = QLabel(value_text)
            value_font = QFont()
            value_font.setPointSize(16)
            value_font.setBold(True)
            value_label.setFont(value_font)
            value_label.setStyleSheet("color: #4ec9b0;")
            stat_layout.addWidget(value_label)
            
            label = QLabel(label_text)
            label.setStyleSheet("color: #888888; font-size: 10px;")
            stat_layout.addWidget(label)
            
            stat_frame.setLayout(stat_layout)
            layout.addWidget(stat_frame, row, col)
            
            col += 1
            if col >= 2:
                col = 0
                row += 1
    
    def update_statistics(self):
        """Update the statistics display"""
        # Check for journal files first
        if not has_journal_files():
            # Show no journal files message in all tabs
            for layout in [self.overview_layout, self.combat_layout, self.exploration_layout, 
                          self.trading_layout, self.missions_layout]:
                self._clear_layout(layout)
                no_files_label = QLabel("No journal files found. Please see the informational message below.")
                no_files_label.setStyleSheet("color: #888888; font-size: 12px; padding: 20px;")
                no_files_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
                layout.addWidget(no_files_label, 0, 0, 1, 2)
            return
        
        stats = self.session_manager.get_session_statistics(self.current_commander)
        
        # Clear and update Overview tab
        self._clear_layout(self.overview_layout)
        overview_stats = [
            ("Total Sessions", str(stats.get("total_sessions", 0))),
            ("Total Jumps", str(stats.get("total_jumps", 0))),
            ("Light Years Traveled", f"{stats.get('total_light_years', 0):,.2f}"),
            ("Total Dockings", str(stats.get("total_docked", 0))),
            ("Planets Landed", str(stats.get("total_planets_landed", 0))),
            ("Total Events", str(stats.get("total_events", 0))),
            ("Systems Visited", str(stats.get("total_systems_visited", 0))),
            ("Stations Visited", str(stats.get("total_stations_visited", 0))),
        ]
        self._add_stat_cards(self.overview_layout, overview_stats)
        
        # Clear and update Combat tab
        self._clear_layout(self.combat_layout)
        credits_change = stats.get("total_credits_change", 0)
        credits_text = f"{credits_change:+,}" if credits_change != 0 else "0"
        combat_stats = [
            ("Credits Change", credits_text),
            ("Kills", str(stats.get("total_kills", 0))),
            ("Deaths", str(stats.get("total_deaths", 0))),
            ("Bounties Earned", f"{stats.get('total_bounties', 0):,}"),
            ("Combat Bonds", f"{stats.get('total_combat_bonds', 0):,}"),
        ]
        self._add_stat_cards(self.combat_layout, combat_stats)
        
        # Clear and update Exploration tab
        self._clear_layout(self.exploration_layout)
        exploration_stats = [
            ("Exploration Value", f"{stats.get('total_exploration_value', 0):,}"),
            ("Scans", str(stats.get("total_scans", 0))),
            ("FSS Scans", str(stats.get("total_fss_scans", 0))),
            ("DSS Scans", str(stats.get("total_dss_scans", 0))),
            ("Codex Entries", str(stats.get("total_codex_entries", 0))),
        ]
        self._add_stat_cards(self.exploration_layout, exploration_stats)
        
        # Clear and update Trading tab
        self._clear_layout(self.trading_layout)
        trading_stats = [
            ("Trade Profit", f"{stats.get('total_trade_profit', 0):,}"),
        ]
        self._add_stat_cards(self.trading_layout, trading_stats)
        
        # Clear and update Missions tab
        self._clear_layout(self.missions_layout)
        missions_stats = [
            ("Missions Accepted", str(stats.get("total_missions_accepted", 0))),
            ("Missions Completed", str(stats.get("total_missions_completed", 0))),
            ("Missions Failed", str(stats.get("total_missions_failed", 0))),
            ("Mission Rewards", f"{stats.get('total_mission_rewards', 0):,}"),
        ]
        self._add_stat_cards(self.missions_layout, missions_stats)
    
    def _clear_layout(self, layout):
        """Clear all widgets from a layout"""
        while layout.count():
            child = layout.takeAt(0)
            if child.widget():
                child.widget().deleteLater()
    
    def update_sessions_list(self):
        """Update the sessions list"""
        self.sessions_list.clear()
        
        # Check for journal files first
        if not has_journal_files():
            self.sessions_list.hide()
            self.no_journal_widget.show()
            return
        
        self.sessions_list.show()
        self.no_journal_widget.hide()
        
        sessions = self.session_manager.get_sessions_for_commander(
            self.current_commander
        ) if self.current_commander else self.session_manager.get_all_sessions(limit=50)
        
        if not sessions:
            # No sessions but journal files exist
            item = QListWidgetItem("No sessions found. Play Elite Dangerous to generate session data.")
            item.setForeground(QBrush(QColor(136, 136, 136)))  # #888888 color
            self.sessions_list.addItem(item)
            return
        
        for session in sessions:
            start_time = session.get("start_time", "Unknown")
            commander = session.get("commander", "Unknown")
            jumps = session.get("jumps", 0)
            events = session.get("total_events", 0)
            
            # Format timestamp
            try:
                if start_time and start_time != "Unknown":
                    dt = datetime.fromisoformat(start_time.replace('Z', '+00:00'))
                    time_str = dt.strftime('%Y-%m-%d %H:%M')
                else:
                    time_str = "Unknown"
            except:
                time_str = str(start_time)[:19] if start_time else "Unknown"
            
            # Get additional info
            credits_change = session.get("credits_change", 0)
            systems = len(session.get("systems_visited", []))
            credits_text = f"{credits_change:+,}" if credits_change != 0 else "0"
            
            # Create display text with more info
            display_text = f"[{time_str}] {commander} | {jumps} jumps | {systems} systems | {credits_text} credits | {events} events"
            
            item = QListWidgetItem(display_text)
            item.setData(Qt.ItemDataRole.UserRole, session)
            self.sessions_list.addItem(item)
    
    def show_session_details(self, item: QListWidgetItem):
        """Show detailed information about a session"""
        session = item.data(Qt.ItemDataRole.UserRole)
        if not session:
            return
        
        # Create a simple details dialog
        from PyQt6.QtWidgets import QMessageBox
        
        details = QMessageBox(self)
        details.setWindowTitle("Session Details")
        
        # Format session details
        start_time = session.get("start_time", "Unknown")
        end_time = session.get("end_time", "Unknown")
        commander = session.get("commander", "Unknown")
        
        try:
            if start_time and start_time != "Unknown":
                start_dt = datetime.fromisoformat(start_time.replace('Z', '+00:00'))
                start_str = start_dt.strftime('%Y-%m-%d %H:%M:%S')
            else:
                start_str = "Unknown"
        except:
            start_str = str(start_time)[:19] if start_time else "Unknown"
        
        try:
            if end_time and end_time != "Unknown":
                end_dt = datetime.fromisoformat(end_time.replace('Z', '+00:00'))
                end_str = end_dt.strftime('%Y-%m-%d %H:%M:%S')
            else:
                end_str = "Unknown"
        except:
            end_str = str(end_time)[:19] if end_time else "Unknown"
        
        # Calculate duration if possible
        duration_str = "Unknown"
        try:
            if start_time and end_time and start_time != "Unknown" and end_time != "Unknown":
                start_dt = datetime.fromisoformat(start_time.replace('Z', '+00:00'))
                end_dt = datetime.fromisoformat(end_time.replace('Z', '+00:00'))
                duration = end_dt - start_dt
                hours = duration.total_seconds() / 3600
                duration_str = f"{hours:.2f} hours"
        except:
            pass
        
        # Format credits
        first_credits = session.get('first_credits', 0)
        last_credits = session.get('last_credits', 0)
        credits_change = session.get('credits_change', 0)
        credits_change_text = f"{credits_change:+,}" if credits_change != 0 else "0"
        
        # Format other stats
        systems_visited = len(session.get('systems_visited', []))
        stations_visited = len(session.get('stations_visited', []))
        unique_ships = len(session.get('unique_ships', []))
        
        details_text = f"""
        <h3>Session Details</h3>
        <h4>General Information</h4>
        <p><b>Commander:</b> {commander}</p>
        <p><b>Start Time:</b> {start_str}</p>
        <p><b>End Time:</b> {end_str}</p>
        <p><b>Duration:</b> {duration_str}</p>
        <p><b>Total Events:</b> {session.get('total_events', 0)}</p>
        
        <h4>Travel</h4>
        <p><b>Light Years Traveled:</b> {session.get('light_years_traveled', 0):,.2f}</p>
        <p><b>Jumps:</b> {session.get('jumps', 0)}</p>
        <p><b>Systems Visited:</b> {systems_visited}</p>
        <p><b>Stations Visited:</b> {stations_visited}</p>
        <p><b>Planets Landed:</b> {session.get('planets_landed', 0)}</p>
        <p><b>Dockings:</b> {session.get('docked_count', 0)}</p>
        <p><b>First System:</b> {session.get('first_system', 'Unknown')}</p>
        <p><b>Last System:</b> {session.get('last_system', 'Unknown')}</p>
        
        <h4>Ships</h4>
        <p><b>First Ship:</b> {session.get('first_ship', 'Unknown')}</p>
        <p><b>Last Ship:</b> {session.get('last_ship', 'Unknown')}</p>
        <p><b>Unique Ships Used:</b> {unique_ships}</p>
        
        <h4>Credits</h4>
        <p><b>Starting Credits:</b> {first_credits:,}</p>
        <p><b>Ending Credits:</b> {last_credits:,}</p>
        <p><b>Credits Change:</b> {credits_change_text}</p>
        
        <h4>Combat</h4>
        <p><b>Kills:</b> {session.get('kills', 0)}</p>
        <p><b>Deaths:</b> {session.get('deaths', 0)}</p>
        <p><b>Bounties Earned:</b> {session.get('bounties_earned', 0):,}</p>
        <p><b>Bounty Count:</b> {session.get('bounty_count', 0)}</p>
        <p><b>Combat Bonds:</b> {session.get('combat_bonds', 0):,}</p>
        <p><b>Died:</b> {'Yes' if session.get('died', False) else 'No'}</p>
        
        <h4>Exploration</h4>
        <p><b>Scans:</b> {session.get('scans', 0)}</p>
        <p><b>FSS Scans:</b> {session.get('fss_scans', 0)}</p>
        <p><b>DSS Scans:</b> {session.get('dss_scans', 0)}</p>
        <p><b>Codex Entries:</b> {session.get('codex_entries', 0)}</p>
        <p><b>Exploration Value:</b> {session.get('exploration_value', 0):,}</p>
        
        <h4>Trading</h4>
        <p><b>Market Buys:</b> {session.get('market_buys', 0)}</p>
        <p><b>Market Sells:</b> {session.get('market_sells', 0)}</p>
        <p><b>Trade Profit:</b> {session.get('trade_profit', 0):,}</p>
        
        <h4>Missions</h4>
        <p><b>Accepted:</b> {session.get('missions_accepted', 0)}</p>
        <p><b>Completed:</b> {session.get('missions_completed', 0)}</p>
        <p><b>Failed:</b> {session.get('missions_failed', 0)}</p>
        <p><b>Rewards:</b> {session.get('mission_rewards', 0):,}</p>
        """
        
        details.setTextFormat(Qt.TextFormat.RichText)
        details.setText(details_text)
        details.exec()

