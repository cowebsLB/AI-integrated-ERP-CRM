"""
Update dialog for showing available updates.
"""
from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QTextEdit, QMessageBox
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QDesktopServices
from datetime import datetime
import config


class UpdateDialog(QDialog):
    """Dialog for displaying update information."""
    
    def __init__(self, update_info: dict, parent=None):
        super().__init__(parent)
        self.update_info = update_info
        self.init_ui()
    
    def init_ui(self):
        """Initialize the UI."""
        self.setWindowTitle("Update Available")
        self.setMinimumWidth(500)
        self.setMinimumHeight(400)
        
        layout = QVBoxLayout()
        
        # Title
        title = QLabel(f"Update Available: v{self.update_info.get('version', 'Unknown')}")
        title.setStyleSheet("font-size: 18px; font-weight: bold; padding: 10px;")
        layout.addWidget(title)
        
        # Current version info
        current_label = QLabel(f"Current version: {config.APP_VERSION}")
        current_label.setStyleSheet("color: gray; padding: 5px;")
        layout.addWidget(current_label)
        
        # Release name
        release_name = self.update_info.get("name", "")
        if release_name:
            name_label = QLabel(f"Release: {release_name}")
            name_label.setStyleSheet("font-weight: bold; padding: 5px;")
            layout.addWidget(name_label)
        
        # Release date
        published_at = self.update_info.get("published_at", "")
        if published_at:
            try:
                date_obj = datetime.fromisoformat(published_at.replace('Z', '+00:00'))
                date_str = date_obj.strftime("%B %d, %Y")
                date_label = QLabel(f"Published: {date_str}")
                date_label.setStyleSheet("color: gray; padding: 5px;")
                layout.addWidget(date_label)
            except:
                pass
        
        # Release notes
        notes_label = QLabel("Release Notes:")
        notes_label.setStyleSheet("font-weight: bold; padding-top: 10px;")
        layout.addWidget(notes_label)
        
        release_notes = QTextEdit()
        release_notes.setReadOnly(True)
        release_notes.setMaximumHeight(200)
        body = self.update_info.get("body", "No release notes available.")
        # Convert markdown-style formatting to plain text (basic)
        body = body.replace("##", "").replace("###", "").strip()
        release_notes.setPlainText(body)
        layout.addWidget(release_notes)
        
        # Prerelease warning
        if self.update_info.get("prerelease", False):
            warning = QLabel("⚠️ This is a pre-release version")
            warning.setStyleSheet("color: orange; font-weight: bold; padding: 5px;")
            layout.addWidget(warning)
        
        # Buttons
        button_layout = QHBoxLayout()
        button_layout.addStretch()
        
        download_button = QPushButton("Download Update")
        download_button.clicked.connect(self.download_update)
        button_layout.addWidget(download_button)
        
        later_button = QPushButton("Remind Me Later")
        later_button.clicked.connect(self.reject)
        button_layout.addWidget(later_button)
        
        skip_button = QPushButton("Skip This Version")
        skip_button.clicked.connect(self.skip_version)
        button_layout.addWidget(skip_button)
        
        layout.addLayout(button_layout)
        
        self.setLayout(layout)
    
    def download_update(self):
        """Open download URL in browser."""
        html_url = self.update_info.get("html_url", "")
        if html_url:
            QDesktopServices.openUrl(html_url)
            QMessageBox.information(
                self,
                "Download Started",
                "The update page has been opened in your browser.\n"
                "Please download and install the update manually."
            )
            self.accept()
        else:
            QMessageBox.warning(self, "Error", "Download URL not available.")
    
    def skip_version(self):
        """Skip this version (store in preferences)."""
        # TODO: Implement version skipping in preferences/config
        QMessageBox.information(
            self,
            "Version Skipped",
            "This version will be skipped in future update checks."
        )
        self.reject()

