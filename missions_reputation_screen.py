"""
Missions & Reputation view: track active missions, completed/failed this session, and reputation.
"""
import json
from typing import Optional
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QFrame, QScrollArea,
    QSizePolicy, QGridLayout
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont
from current_session_tracker import CurrentSessionTracker


# Style constants
SECTION_STYLE = "QFrame { background-color: #2b2b2b; border: 1px solid #3c3c3c; border-radius: 6px; padding: 12px; }"
TITLE_STYLE = "color: #4ec9b0; font-size: 13px; font-weight: bold;"
LABEL_STYLE = "color: #cccccc; font-size: 11px;"
MUTED_STYLE = "color: #666666; font-size: 11px;"
REWARD_STYLE = "color: #7bed9f; font-size: 11px;"
FAILED_STYLE = "color: #ff6b6b; font-size: 11px;"


class MissionsReputationScreen(QWidget):
    """Full-page view for missions and reputation tracking."""

    def __init__(self, current_session_tracker: CurrentSessionTracker, parent=None):
        super().__init__(parent)
        self.current_session_tracker = current_session_tracker
        self._last_refresh_snapshot: Optional[str] = None  # avoid full rebuild when data unchanged
        self.build_ui()

    def build_ui(self):
        layout = QVBoxLayout()
        layout.setSpacing(12)
        layout.setContentsMargins(15, 15, 15, 15)

        # Title
        title = QLabel("Missions & Reputation")
        title_font = QFont()
        title_font.setPointSize(18)
        title_font.setBold(True)
        title.setFont(title_font)
        title.setStyleSheet("color: white;")
        layout.addWidget(title)

        # Subtitle
        sub = QLabel("Tracks active missions, completed and failed this session, and faction reputation. Select a commander and play to see live updates.")
        sub.setStyleSheet(MUTED_STYLE)
        sub.setWordWrap(True)
        layout.addWidget(sub)

        # Reputation section — fixed at top, locked in frame (does not scroll)
        self.reputation_frame = QFrame()
        self.reputation_frame.setStyleSheet(SECTION_STYLE)
        self.reputation_frame.setSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Maximum)
        self.reputation_layout = QVBoxLayout()
        self.reputation_layout.setSpacing(6)
        rlab = QLabel("Superpower Reputation Checkpoint Progress")
        rlab.setStyleSheet(TITLE_STYLE)
        self.reputation_layout.addWidget(rlab)
        self.reputation_content = QGridLayout()  # columns: Faction | Reputation (and optional Level/Next)
        self.reputation_layout.addLayout(self.reputation_content)
        self.reputation_frame.setLayout(self.reputation_layout)
        layout.addWidget(self.reputation_frame)

        # Scroll area for missions only (reputation stays fixed above)
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.Shape.NoFrame)
        scroll.setStyleSheet("QScrollArea { background: transparent; border: none; }")
        scroll_content = QWidget()
        scroll_layout = QVBoxLayout()
        scroll_layout.setSpacing(12)

        # Active Missions section
        self.active_missions_frame = QFrame()
        self.active_missions_frame.setStyleSheet(SECTION_STYLE)
        self.active_missions_layout = QVBoxLayout()
        self.active_missions_layout.setSpacing(6)
        alab = QLabel("Completed Missions, Ready to Turn In")
        alab.setStyleSheet(TITLE_STYLE)
        self.active_missions_layout.addWidget(alab)
        self.active_missions_content = QVBoxLayout()
        self.active_missions_layout.addLayout(self.active_missions_content)
        self.active_missions_frame.setLayout(self.active_missions_layout)
        scroll_layout.addWidget(self.active_missions_frame)

        # Completed This Session section
        self.completed_frame = QFrame()
        self.completed_frame.setStyleSheet(SECTION_STYLE)
        self.completed_layout = QVBoxLayout()
        self.completed_layout.setSpacing(6)
        clab = QLabel("Completed This Session")
        clab.setStyleSheet(TITLE_STYLE)
        self.completed_layout.addWidget(clab)
        self.completed_content = QVBoxLayout()
        self.completed_layout.addLayout(self.completed_content)
        self.completed_frame.setLayout(self.completed_layout)
        scroll_layout.addWidget(self.completed_frame)

        # Failed This Session section
        self.failed_frame = QFrame()
        self.failed_frame.setStyleSheet(SECTION_STYLE)
        self.failed_layout = QVBoxLayout()
        self.failed_layout.setSpacing(6)
        flab = QLabel("Failed / Abandoned This Session")
        flab.setStyleSheet(TITLE_STYLE)
        self.failed_layout.addWidget(flab)
        self.failed_content = QVBoxLayout()
        self.failed_layout.addLayout(self.failed_content)
        self.failed_frame.setLayout(self.failed_layout)
        scroll_layout.addWidget(self.failed_frame)

        scroll_layout.addStretch()
        scroll_content.setLayout(scroll_layout)
        scroll.setWidget(scroll_content)
        layout.addWidget(scroll, 1)  # stretch so panel resizes and scrolls when content overflows

        self.setLayout(layout)

    def _rep_faction_display_name(self, key: str) -> str:
        """Clean faction key for display (e.g. $faction_Federation; -> Federation)."""
        if not key:
            return key
        s = key.strip()
        if s.startswith("$") and s.endswith(";"):
            s = s[1:-1]
            if "_" in s:
                s = s.split("_")[-1]
        return s.replace("_", " ").strip() or key

    def _clear_layout(self, layout):
        """Remove all widgets from a layout (works with QVBoxLayout or QGridLayout)."""
        while layout.count():
            item = layout.takeAt(0)
            if item and item.widget():
                item.widget().deleteLater()

    def _stats_snapshot(self, stats: dict) -> str:
        """Build a comparable snapshot so we only rebuild UI when data changed."""
        try:
            missions = stats.get("missions", {})
            rep = stats.get("reputation", {})
            return json.dumps({
                "has_session": self.current_session_tracker.has_active_session(),
                "active": missions.get("active", []),
                "completed_list": missions.get("completed_list", []),
                "failed_list": missions.get("failed_list", []),
                "reputation": rep,
            }, sort_keys=True, default=str)
        except Exception:
            return ""

    def refresh_data(self):
        """Refresh from current session tracker. Skips full rebuild if data unchanged (perf)."""
        stats = self.current_session_tracker.get_statistics()
        snapshot = self._stats_snapshot(stats)
        if snapshot == self._last_refresh_snapshot:
            return
        self._last_refresh_snapshot = snapshot

        self._clear_layout(self.active_missions_content)
        self._clear_layout(self.completed_content)
        self._clear_layout(self.failed_content)
        self._clear_layout(self.reputation_content)

        if not self.current_session_tracker.has_active_session():
            msg = QLabel("No active session. Select a commander and start Elite Dangerous to track missions and reputation.")
            msg.setStyleSheet(MUTED_STYLE)
            msg.setWordWrap(True)
            self.active_missions_content.addWidget(msg)
            rep_msg = QLabel("No active session.")
            rep_msg.setStyleSheet(MUTED_STYLE)
            self.reputation_content.addWidget(rep_msg, 0, 0, 1, 2)  # span both columns (grid)
            return

        missions = stats.get("missions", {})
        active = missions.get("active", [])
        completed_list = missions.get("completed_list", [])
        failed_list = missions.get("failed_list", [])
        rep = stats.get("reputation", {})

        # Active missions (most recent first)
        if active:
            for m in reversed(active):
                name = m.get("Name", "Unknown")
                faction = m.get("Faction", "")
                dest_sys = m.get("DestinationSystem", "")
                dest_sta = m.get("DestinationStation", "")
                dest = dest_sys or dest_sta or ""
                line = name
                if faction:
                    line += f" — {faction}"
                if dest:
                    line += f" → {dest}"
                lbl = QLabel(line)
                lbl.setStyleSheet(LABEL_STYLE)
                lbl.setWordWrap(True)
                self.active_missions_content.addWidget(lbl)
        else:
            lbl = QLabel("No completed missions ready to turn in.")
            lbl.setStyleSheet(MUTED_STYLE)
            self.active_missions_content.addWidget(lbl)

        # Completed this session (newest first)
        if completed_list:
            for m in reversed(completed_list):
                name = m.get("Name", "Unknown")
                faction = m.get("Faction", "")
                reward = m.get("Reward", 0)
                line = f"✓ {name}"
                if faction:
                    line += f" ({faction})"
                if reward:
                    line += f" — {reward:,} cr"
                lbl = QLabel(line)
                lbl.setStyleSheet(REWARD_STYLE)
                lbl.setWordWrap(True)
                self.completed_content.addWidget(lbl)

                # Reputation/Influence from FactionEffects
                effects = m.get("FactionEffects") or []
                if effects:
                    parts = []
                    for fe in effects:
                        fname = fe.get("Faction", "")
                        rep = fe.get("Reputation", "")
                        rep_trend = fe.get("ReputationTrend", "")
                        inf_list = fe.get("Influence") or []
                        if rep or rep_trend:
                            parts.append(f"{fname}: Rep {rep} {rep_trend}".strip())
                        for inf in inf_list:
                            if inf:
                                parts.append(f"{fname}: Inf {inf}".strip() if fname else f"Inf {inf}")
                    if parts:
                        sub = QLabel("   Rep/Influence: " + "; ".join(parts))
                        sub.setStyleSheet(LABEL_STYLE)
                        sub.setWordWrap(True)
                        self.completed_content.addWidget(sub)

                # Materials rewarded
                mats = m.get("MaterialsReward") or []
                if mats:
                    mat_strs = [f"{mat.get('Count', 0)}× {mat.get('Name', '') or mat.get('Category', '')}".strip() for mat in mats]
                    sub = QLabel("   Materials: " + ", ".join(mat_strs))
                    sub.setStyleSheet(LABEL_STYLE)
                    sub.setWordWrap(True)
                    self.completed_content.addWidget(sub)
        else:
            lbl = QLabel("None yet this session")
            lbl.setStyleSheet(MUTED_STYLE)
            self.completed_content.addWidget(lbl)

        # Failed this session (newest first)
        if failed_list:
            for m in reversed(failed_list):
                name = m.get("Name", "Unknown")
                faction = m.get("Faction", "")
                line = f"✗ {name}"
                if faction:
                    line += f" ({faction})"
                lbl = QLabel(line)
                lbl.setStyleSheet(FAILED_STYLE)
                lbl.setWordWrap(True)
                self.failed_content.addWidget(lbl)
        else:
            lbl = QLabel("None this session")
            lbl.setStyleSheet(MUTED_STYLE)
            self.failed_content.addWidget(lbl)

        # Reputation — columned layout (cap rows so pane doesn't overwhelm)
        skip = {"event", "timestamp"}
        rep_items = [(k, rep[k]) for k in sorted(rep.keys()) if k not in skip]
        max_rep_rows = 30
        if rep_items:
            header_faction = QLabel("Faction")
            header_value = QLabel("Reputation")
            header_faction.setStyleSheet(TITLE_STYLE)
            header_value.setStyleSheet(TITLE_STYLE)
            self.reputation_content.addWidget(header_faction, 0, 0)
            self.reputation_content.addWidget(header_value, 0, 1)
            for row, (faction_name, value) in enumerate(rep_items[:max_rep_rows], start=1):
                display_name = self._rep_faction_display_name(faction_name)
                try:
                    if isinstance(value, (int, float)):
                        if 0 <= value <= 1:
                            pct = f"{value * 100:.0f}%"
                        else:
                            pct = f"{value:.0f}"
                    else:
                        pct = str(value)
                except Exception:
                    pct = str(value)
                flbl = QLabel(display_name)
                vlbl = QLabel(pct)
                flbl.setStyleSheet(LABEL_STYLE)
                vlbl.setStyleSheet(LABEL_STYLE)
                self.reputation_content.addWidget(flbl, row, 0)
                self.reputation_content.addWidget(vlbl, row, 1)
            if len(rep_items) > max_rep_rows:
                more = QLabel(f"+ {len(rep_items) - max_rep_rows} more faction(s)")
                more.setStyleSheet(MUTED_STYLE)
                self.reputation_content.addWidget(more, max_rep_rows + 1, 0, 1, 2)
        else:
            lbl = QLabel(
                "No reputation data yet. The game sends a Reputation event when you dock or at certain "
                "events; data will appear here after that."
            )
            lbl.setStyleSheet(MUTED_STYLE)
            lbl.setWordWrap(True)
            self.reputation_content.addWidget(lbl, 0, 0, 1, 2)
