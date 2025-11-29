"""
Campaign dialog for adding/editing marketing campaigns.
"""
from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QFormLayout,
    QLineEdit, QPushButton, QDoubleSpinBox, QDateEdit, QTextEdit, QComboBox, QMessageBox
)
from PyQt6.QtCore import Qt, QDate
from datetime import datetime
from src.crm.marketing_service import MarketingService


class CampaignDialog(QDialog):
    """Dialog for adding or editing a marketing campaign."""
    
    def __init__(self, parent=None, campaign_id=None):
        super().__init__(parent)
        self.marketing_service = MarketingService()
        self.campaign_id = campaign_id
        self.init_ui()
        
        if campaign_id:
            self.load_campaign()
    
    def init_ui(self):
        """Initialize the UI."""
        self.setWindowTitle("Add Campaign" if not self.campaign_id else "Edit Campaign")
        self.setMinimumWidth(400)
        
        layout = QVBoxLayout()
        
        # Form
        form = QFormLayout()
        
        self.name_input = QLineEdit()
        form.addRow("Campaign Name:", self.name_input)
        
        self.type_combo = QComboBox()
        self.type_combo.addItems(["email", "social_media", "print", "online", "event", "other"])
        form.addRow("Campaign Type:", self.type_combo)
        
        self.description_input = QTextEdit()
        self.description_input.setMaximumHeight(100)
        form.addRow("Description:", self.description_input)
        
        self.start_date_input = QDateEdit()
        self.start_date_input.setCalendarPopup(True)
        self.start_date_input.setDate(QDate.currentDate())
        form.addRow("Start Date:", self.start_date_input)
        
        self.end_date_input = QDateEdit()
        self.end_date_input.setCalendarPopup(True)
        self.end_date_input.setDate(QDate.currentDate())
        form.addRow("End Date:", self.end_date_input)
        
        self.budget_input = QDoubleSpinBox()
        self.budget_input.setMaximum(99999999.99)
        self.budget_input.setDecimals(2)
        form.addRow("Budget:", self.budget_input)
        
        layout.addLayout(form)
        
        # Buttons
        button_layout = QHBoxLayout()
        button_layout.addStretch()
        
        self.save_button = QPushButton("Save")
        self.save_button.clicked.connect(self.save_campaign)
        button_layout.addWidget(self.save_button)
        
        self.cancel_button = QPushButton("Cancel")
        self.cancel_button.clicked.connect(self.reject)
        button_layout.addWidget(self.cancel_button)
        
        layout.addLayout(button_layout)
        
        self.setLayout(layout)
    
    def load_campaign(self):
        """Load campaign data into the form."""
        campaign = self.marketing_service.get_campaign(self.campaign_id)
        if campaign:
            self.name_input.setText(campaign.name)
            index = self.type_combo.findText(campaign.campaign_type)
            if index >= 0:
                self.type_combo.setCurrentIndex(index)
            self.description_input.setPlainText(campaign.description or "")
            if campaign.start_date:
                self.start_date_input.setDate(QDate.fromString(
                    campaign.start_date.strftime("%Y-%m-%d"), "yyyy-MM-dd"
                ))
            if campaign.end_date:
                self.end_date_input.setDate(QDate.fromString(
                    campaign.end_date.strftime("%Y-%m-%d"), "yyyy-MM-dd"
                ))
            self.budget_input.setValue(campaign.budget)
    
    def save_campaign(self):
        """Save the campaign."""
        name = self.name_input.text().strip()
        
        if not name:
            QMessageBox.warning(self, "Validation Error", "Campaign Name is required.")
            return
        
        try:
            start_date = self.start_date_input.date().toPyDate()
            start_datetime = datetime.combine(start_date, datetime.min.time())
            
            end_date = self.end_date_input.date().toPyDate()
            end_datetime = datetime.combine(end_date, datetime.min.time())
            
            if self.campaign_id:
                # Update existing campaign
                self.marketing_service.update_campaign(
                    self.campaign_id,
                    name=name,
                    campaign_type=self.type_combo.currentText(),
                    description=self.description_input.toPlainText().strip() or None,
                    start_date=start_datetime,
                    end_date=end_datetime,
                    budget=self.budget_input.value()
                )
            else:
                # Create new campaign
                self.marketing_service.create_campaign(
                    name=name,
                    campaign_type=self.type_combo.currentText(),
                    description=self.description_input.toPlainText().strip() or None,
                    start_date=start_datetime,
                    end_date=end_datetime,
                    budget=self.budget_input.value()
                )
            
            self.accept()
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to save campaign: {str(e)}")

