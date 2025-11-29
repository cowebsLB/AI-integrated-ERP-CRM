"""
Opportunities view for Sales module.
"""
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QTableWidget, QTableWidgetItem,
    QPushButton, QLabel, QComboBox, QMessageBox
)
from PyQt6.QtCore import Qt
from src.crm.sales_service import SalesService
from src.database.models.crm_models import OpportunityStage


class OpportunitiesView(QWidget):
    """View for managing sales opportunities."""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.sales_service = SalesService()
        self.init_ui()
        self.load_opportunities()
    
    def init_ui(self):
        """Initialize the UI."""
        layout = QVBoxLayout()
        
        # Header
        header_layout = QHBoxLayout()
        title = QLabel("Sales Opportunities")
        title.setStyleSheet("font-size: 18px; font-weight: bold;")
        header_layout.addWidget(title)
        header_layout.addStretch()
        
        # Stage filter
        self.stage_filter = QComboBox()
        self.stage_filter.addItem("All Stages", None)
        for stage in OpportunityStage:
            self.stage_filter.addItem(stage.value.replace("_", " ").title(), stage)
        self.stage_filter.currentIndexChanged.connect(self.load_opportunities)
        header_layout.addWidget(QLabel("Filter:"))
        header_layout.addWidget(self.stage_filter)
        
        self.add_button = QPushButton("New Opportunity")
        self.add_button.clicked.connect(self.add_opportunity)
        header_layout.addWidget(self.add_button)
        
        self.edit_button = QPushButton("Edit")
        self.edit_button.clicked.connect(self.edit_opportunity)
        header_layout.addWidget(self.edit_button)
        
        self.delete_button = QPushButton("Delete")
        self.delete_button.clicked.connect(self.delete_opportunity)
        header_layout.addWidget(self.delete_button)
        
        self.refresh_button = QPushButton("Refresh")
        self.refresh_button.clicked.connect(self.load_opportunities)
        header_layout.addWidget(self.refresh_button)
        
        layout.addLayout(header_layout)
        
        # Table
        self.table = QTableWidget()
        self.table.setColumnCount(6)
        self.table.setHorizontalHeaderLabels([
            "Name", "Contact", "Stage", "Value", "Probability", "Expected Close"
        ])
        self.table.horizontalHeader().setStretchLastSection(True)
        self.table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        
        layout.addWidget(self.table)
        
        self.setLayout(layout)
    
    def load_opportunities(self):
        """Load opportunities into the table."""
        stage = self.stage_filter.currentData()
        opportunities = self.sales_service.get_opportunities(stage=stage)
        self.table.setRowCount(len(opportunities))
        
        for row, opp in enumerate(opportunities):
            self.table.setItem(row, 0, QTableWidgetItem(opp.name))
            contact_name = f"{opp.contact.first_name} {opp.contact.last_name}" if opp.contact else ""
            self.table.setItem(row, 1, QTableWidgetItem(contact_name))
            self.table.setItem(row, 2, QTableWidgetItem(opp.stage.value.replace("_", " ").title()))
            self.table.setItem(row, 3, QTableWidgetItem(f"${opp.value:.2f}"))
            self.table.setItem(row, 4, QTableWidgetItem(f"{opp.probability}%"))
            close_date = opp.expected_close_date.strftime("%Y-%m-%d") if opp.expected_close_date else ""
            self.table.setItem(row, 5, QTableWidgetItem(close_date))
        
        self.table.resizeColumnsToContents()
    
    def add_opportunity(self):
        """Open dialog to add a new opportunity."""
        QMessageBox.information(self, "New Opportunity", 
                              "Opportunity dialog will be implemented in a future update.")
    
    def edit_opportunity(self):
        """Open dialog to edit selected opportunity."""
        selected_rows = self.table.selectionModel().selectedRows()
        if not selected_rows:
            QMessageBox.warning(self, "No Selection", "Please select an opportunity to edit.")
            return
        
        QMessageBox.information(self, "Edit Opportunity", 
                              "Opportunity editing will be implemented in a future update.")
    
    def delete_opportunity(self):
        """Delete selected opportunity."""
        selected_rows = self.table.selectionModel().selectedRows()
        if not selected_rows:
            QMessageBox.warning(self, "No Selection", "Please select an opportunity to delete.")
            return
        
        reply = QMessageBox.question(
            self, "Confirm Delete", 
            "Are you sure you want to delete this opportunity?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            row = selected_rows[0].row()
            opportunity_name = self.table.item(row, 0).text()
            opportunities = self.sales_service.get_opportunities()
            opportunity = next((o for o in opportunities if o.name == opportunity_name), None)
            
            if opportunity:
                if self.sales_service.delete_opportunity(opportunity.id):
                    self.load_opportunities()
                else:
                    QMessageBox.warning(self, "Error", "Failed to delete opportunity.")

