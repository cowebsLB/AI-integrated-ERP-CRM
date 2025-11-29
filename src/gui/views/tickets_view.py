"""
Tickets view for Customer Service module.
"""
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QTableWidget, QTableWidgetItem,
    QPushButton, QLabel, QComboBox, QMessageBox
)
from PyQt6.QtCore import Qt
from src.crm.service_service import ServiceService
from src.database.models.crm_models import TicketStatus


class TicketsView(QWidget):
    """View for managing support tickets."""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.service_service = ServiceService()
        self.init_ui()
        self.load_tickets()
    
    def init_ui(self):
        """Initialize the UI."""
        layout = QVBoxLayout()
        
        # Header
        header_layout = QHBoxLayout()
        title = QLabel("Support Tickets")
        title.setStyleSheet("font-size: 18px; font-weight: bold;")
        header_layout.addWidget(title)
        header_layout.addStretch()
        
        # Status filter
        self.status_filter = QComboBox()
        self.status_filter.addItem("All Statuses", None)
        for status in TicketStatus:
            self.status_filter.addItem(status.value.replace("_", " ").title(), status)
        self.status_filter.currentIndexChanged.connect(self.load_tickets)
        header_layout.addWidget(QLabel("Filter:"))
        header_layout.addWidget(self.status_filter)
        
        self.add_button = QPushButton("New Ticket")
        self.add_button.clicked.connect(self.add_ticket)
        header_layout.addWidget(self.add_button)
        
        self.edit_button = QPushButton("Edit")
        self.edit_button.clicked.connect(self.edit_ticket)
        header_layout.addWidget(self.edit_button)
        
        self.delete_button = QPushButton("Delete")
        self.delete_button.clicked.connect(self.delete_ticket)
        header_layout.addWidget(self.delete_button)
        
        self.refresh_button = QPushButton("Refresh")
        self.refresh_button.clicked.connect(self.load_tickets)
        header_layout.addWidget(self.refresh_button)
        
        layout.addLayout(header_layout)
        
        # Table
        self.table = QTableWidget()
        self.table.setColumnCount(6)
        self.table.setHorizontalHeaderLabels([
            "Ticket #", "Subject", "Contact", "Status", "Priority", "Created"
        ])
        self.table.horizontalHeader().setStretchLastSection(True)
        self.table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        
        layout.addWidget(self.table)
        
        self.setLayout(layout)
    
    def load_tickets(self):
        """Load tickets into the table."""
        status = self.status_filter.currentData()
        tickets = self.service_service.get_tickets(status=status)
        self.table.setRowCount(len(tickets))
        
        for row, ticket in enumerate(tickets):
            self.table.setItem(row, 0, QTableWidgetItem(ticket.ticket_number))
            self.table.setItem(row, 1, QTableWidgetItem(ticket.subject))
            contact_name = f"{ticket.contact.first_name} {ticket.contact.last_name}" if ticket.contact else ""
            self.table.setItem(row, 2, QTableWidgetItem(contact_name))
            self.table.setItem(row, 3, QTableWidgetItem(ticket.status.value.replace("_", " ").title()))
            self.table.setItem(row, 4, QTableWidgetItem(ticket.priority.value.title()))
            created = ticket.created_at.strftime("%Y-%m-%d") if ticket.created_at else ""
            self.table.setItem(row, 5, QTableWidgetItem(created))
        
        self.table.resizeColumnsToContents()
    
    def add_ticket(self):
        """Open dialog to add a new ticket."""
        from src.gui.dialogs.ticket_dialog import TicketDialog
        dialog = TicketDialog(self)
        if dialog.exec():
            self.load_tickets()
    
    def edit_ticket(self):
        """Open dialog to edit selected ticket."""
        selected_rows = self.table.selectionModel().selectedRows()
        if not selected_rows:
            QMessageBox.warning(self, "No Selection", "Please select a ticket to edit.")
            return
        
        row = selected_rows[0].row()
        ticket_number = self.table.item(row, 0).text()
        tickets = self.service_service.get_tickets()
        ticket = next((t for t in tickets if t.ticket_number == ticket_number), None)
        
        if ticket:
            from src.gui.dialogs.ticket_dialog import TicketDialog
            dialog = TicketDialog(self, ticket_id=ticket.id)
            if dialog.exec():
                self.load_tickets()
    
    def delete_ticket(self):
        """Delete selected ticket."""
        selected_rows = self.table.selectionModel().selectedRows()
        if not selected_rows:
            QMessageBox.warning(self, "No Selection", "Please select a ticket to delete.")
            return
        
        reply = QMessageBox.question(
            self, "Confirm Delete", 
            "Are you sure you want to delete this ticket?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            row = selected_rows[0].row()
            ticket_number = self.table.item(row, 0).text()
            tickets = self.service_service.get_tickets()
            ticket = next((t for t in tickets if t.ticket_number == ticket_number), None)
            
            if ticket:
                if self.service_service.delete_ticket(ticket.id):
                    self.load_tickets()
                else:
                    QMessageBox.warning(self, "Error", "Failed to delete ticket.")

