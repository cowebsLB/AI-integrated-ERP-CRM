"""
Campaigns view for Marketing module.
"""
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QTableWidget, QTableWidgetItem,
    QPushButton, QLabel
)
from PyQt6.QtCore import Qt
from src.crm.marketing_service import MarketingService


class CampaignsView(QWidget):
    """View for managing marketing campaigns."""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.marketing_service = MarketingService()
        self.init_ui()
        self.load_campaigns()
    
    def init_ui(self):
        """Initialize the UI."""
        layout = QVBoxLayout()
        
        # Header
        header_layout = QHBoxLayout()
        title = QLabel("Marketing Campaigns")
        title.setStyleSheet("font-size: 18px; font-weight: bold;")
        header_layout.addWidget(title)
        header_layout.addStretch()
        
        self.add_button = QPushButton("New Campaign")
        self.add_button.clicked.connect(self.add_campaign)
        header_layout.addWidget(self.add_button)
        
        self.edit_button = QPushButton("Edit")
        self.edit_button.clicked.connect(self.edit_campaign)
        header_layout.addWidget(self.edit_button)
        
        self.delete_button = QPushButton("Delete")
        self.delete_button.clicked.connect(self.delete_campaign)
        header_layout.addWidget(self.delete_button)
        
        self.refresh_button = QPushButton("Refresh")
        self.refresh_button.clicked.connect(self.load_campaigns)
        header_layout.addWidget(self.refresh_button)
        
        layout.addLayout(header_layout)
        
        # Table
        self.table = QTableWidget()
        self.table.setColumnCount(6)
        self.table.setHorizontalHeaderLabels([
            "Name", "Type", "Status", "Start Date", "End Date", "Budget"
        ])
        self.table.horizontalHeader().setStretchLastSection(True)
        self.table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        
        layout.addWidget(self.table)
        
        self.setLayout(layout)
    
    def load_campaigns(self):
        """Load campaigns into the table."""
        campaigns = self.marketing_service.get_campaigns()
        self.table.setRowCount(len(campaigns))
        
        for row, campaign in enumerate(campaigns):
            self.table.setItem(row, 0, QTableWidgetItem(campaign.name))
            self.table.setItem(row, 1, QTableWidgetItem(campaign.campaign_type or ""))
            self.table.setItem(row, 2, QTableWidgetItem(campaign.status))
            start_date = campaign.start_date.strftime("%Y-%m-%d") if campaign.start_date else ""
            self.table.setItem(row, 3, QTableWidgetItem(start_date))
            end_date = campaign.end_date.strftime("%Y-%m-%d") if campaign.end_date else ""
            self.table.setItem(row, 4, QTableWidgetItem(end_date))
            self.table.setItem(row, 5, QTableWidgetItem(f"${campaign.budget:.2f}"))
        
        self.table.resizeColumnsToContents()
    
    def add_campaign(self):
        """Open dialog to add a new campaign."""
        from src.gui.dialogs.campaign_dialog import CampaignDialog
        dialog = CampaignDialog(self)
        if dialog.exec():
            self.load_campaigns()
    
    def edit_campaign(self):
        """Open dialog to edit selected campaign."""
        selected_rows = self.table.selectionModel().selectedRows()
        if not selected_rows:
            from PyQt6.QtWidgets import QMessageBox
            QMessageBox.warning(self, "No Selection", "Please select a campaign to edit.")
            return
        
        row = selected_rows[0].row()
        campaign_name = self.table.item(row, 0).text()
        campaigns = self.marketing_service.get_campaigns()
        campaign = next((c for c in campaigns if c.name == campaign_name), None)
        
        if campaign:
            from src.gui.dialogs.campaign_dialog import CampaignDialog
            dialog = CampaignDialog(self, campaign_id=campaign.id)
            if dialog.exec():
                self.load_campaigns()
    
    def delete_campaign(self):
        """Delete selected campaign."""
        selected_rows = self.table.selectionModel().selectedRows()
        if not selected_rows:
            from PyQt6.QtWidgets import QMessageBox
            QMessageBox.warning(self, "No Selection", "Please select a campaign to delete.")
            return
        
        from PyQt6.QtWidgets import QMessageBox
        reply = QMessageBox.question(
            self, "Confirm Delete", 
            "Are you sure you want to delete this campaign?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            row = selected_rows[0].row()
            campaign_name = self.table.item(row, 0).text()
            campaigns = self.marketing_service.get_campaigns()
            campaign = next((c for c in campaigns if c.name == campaign_name), None)
            
            if campaign:
                if self.marketing_service.delete_campaign(campaign.id):
                    self.load_campaigns()
                else:
                    QMessageBox.warning(self, "Error", "Failed to delete campaign.")

