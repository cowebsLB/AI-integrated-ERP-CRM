"""
Ticket dialog for adding/editing support tickets.
"""
from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QFormLayout,
    QLineEdit, QPushButton, QTextEdit, QComboBox, QMessageBox, QLabel
)
from PyQt6.QtCore import Qt
from src.crm.service_service import ServiceService
from src.crm.contact_service import ContactService
from src.database.models.crm_models import TicketStatus, TicketPriority


class TicketDialog(QDialog):
    """Dialog for adding or editing a support ticket."""
    
    def __init__(self, parent=None, ticket_id=None):
        super().__init__(parent)
        self.service_service = ServiceService()
        self.contact_service = ContactService()
        self.ticket_id = ticket_id
        self.init_ui()
        
        if ticket_id:
            self.load_ticket()
    
    def init_ui(self):
        """Initialize the UI."""
        self.setWindowTitle("Add Ticket" if not self.ticket_id else "Edit Ticket")
        self.setMinimumWidth(500)
        
        layout = QVBoxLayout()
        
        # Form
        form = QFormLayout()
        
        self.ticket_number_input = QLineEdit()
        if not self.ticket_id:
            # Auto-generate ticket number for new tickets
            import random
            self.ticket_number_input.setText(f"TKT-{random.randint(1000, 9999)}")
        form.addRow("Ticket Number:", self.ticket_number_input)
        
        # Contact selection
        self.contact_combo = QComboBox()
        self.contact_combo.setEditable(False)
        self.load_contacts()
        form.addRow("Contact:", self.contact_combo)
        
        self.subject_input = QLineEdit()
        form.addRow("Subject:", self.subject_input)
        
        self.description_input = QTextEdit()
        self.description_input.setMinimumHeight(150)
        form.addRow("Description:", self.description_input)
        
        self.priority_combo = QComboBox()
        for priority in TicketPriority:
            self.priority_combo.addItem(priority.value.title(), priority)
        form.addRow("Priority:", self.priority_combo)
        
        self.status_combo = QComboBox()
        for status in TicketStatus:
            self.status_combo.addItem(status.value.replace("_", " ").title(), status)
        form.addRow("Status:", self.status_combo)
        
        self.category_input = QLineEdit()
        form.addRow("Category:", self.category_input)
        
        layout.addLayout(form)
        
        # Buttons
        button_layout = QHBoxLayout()
        button_layout.addStretch()
        
        self.save_button = QPushButton("Save")
        self.save_button.clicked.connect(self.save_ticket)
        button_layout.addWidget(self.save_button)
        
        self.cancel_button = QPushButton("Cancel")
        self.cancel_button.clicked.connect(self.reject)
        button_layout.addWidget(self.cancel_button)
        
        layout.addLayout(button_layout)
        
        self.setLayout(layout)
    
    def load_contacts(self):
        """Load contacts into the combo box."""
        contacts = self.contact_service.get_contacts()
        self.contact_combo.addItem("-- Select Contact --", None)
        for contact in contacts:
            display_name = f"{contact.first_name} {contact.last_name}"
            if contact.company:
                display_name += f" ({contact.company})"
            self.contact_combo.addItem(display_name, contact.id)
    
    def load_ticket(self):
        """Load ticket data into the form."""
        ticket = self.service_service.get_ticket(self.ticket_id)
        if ticket:
            self.ticket_number_input.setText(ticket.ticket_number)
            # Find contact in combo
            for i in range(self.contact_combo.count()):
                if self.contact_combo.itemData(i) == ticket.contact_id:
                    self.contact_combo.setCurrentIndex(i)
                    break
            self.subject_input.setText(ticket.subject)
            self.description_input.setPlainText(ticket.description or "")
            # Find priority
            for i in range(self.priority_combo.count()):
                if self.priority_combo.itemData(i) == ticket.priority:
                    self.priority_combo.setCurrentIndex(i)
                    break
            # Find status
            for i in range(self.status_combo.count()):
                if self.status_combo.itemData(i) == ticket.status:
                    self.status_combo.setCurrentIndex(i)
                    break
            self.category_input.setText(ticket.category or "")
    
    def save_ticket(self):
        """Save the ticket."""
        ticket_number = self.ticket_number_input.text().strip()
        subject = self.subject_input.text().strip()
        description = self.description_input.toPlainText().strip()
        contact_id = self.contact_combo.currentData()
        
        if not ticket_number or not subject or not description:
            QMessageBox.warning(self, "Validation Error", 
                              "Ticket Number, Subject, and Description are required.")
            return
        
        if not contact_id:
            QMessageBox.warning(self, "Validation Error", "Please select a contact.")
            return
        
        try:
            priority = self.priority_combo.currentData()
            status = self.status_combo.currentData()
            
            if self.ticket_id:
                # Update existing ticket
                self.service_service.update_ticket(
                    self.ticket_id,
                    ticket_number=ticket_number,
                    contact_id=contact_id,
                    subject=subject,
                    description=description,
                    priority=priority,
                    status=status,
                    category=self.category_input.text().strip() or None
                )
            else:
                # Create new ticket
                self.service_service.create_ticket(
                    ticket_number=ticket_number,
                    contact_id=contact_id,
                    subject=subject,
                    description=description,
                    priority=priority,
                    category=self.category_input.text().strip() or None
                )
            
            self.accept()
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to save ticket: {str(e)}")

