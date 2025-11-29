"""
Contacts view for CRM module.
"""
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QTableWidget, QTableWidgetItem,
    QPushButton, QLineEdit, QLabel, QHeaderView, QMessageBox
)
from PyQt6.QtCore import Qt
from src.crm.contact_service import ContactService


class ContactsView(QWidget):
    """View for managing contacts."""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.contact_service = ContactService()
        self.init_ui()
        self.load_contacts()
    
    def init_ui(self):
        """Initialize the UI."""
        layout = QVBoxLayout()
        
        # Header
        header_layout = QHBoxLayout()
        title = QLabel("Contacts")
        title.setStyleSheet("font-size: 18px; font-weight: bold;")
        header_layout.addWidget(title)
        header_layout.addStretch()
        
        # Search
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Search contacts...")
        self.search_input.textChanged.connect(self.search_contacts)
        header_layout.addWidget(self.search_input)
        
        # Buttons
        self.add_button = QPushButton("Add Contact")
        self.add_button.clicked.connect(self.add_contact)
        header_layout.addWidget(self.add_button)
        
        self.edit_button = QPushButton("Edit")
        self.edit_button.clicked.connect(self.edit_contact)
        header_layout.addWidget(self.edit_button)
        
        self.delete_button = QPushButton("Delete")
        self.delete_button.clicked.connect(self.delete_contact)
        header_layout.addWidget(self.delete_button)
        
        self.refresh_button = QPushButton("Refresh")
        self.refresh_button.clicked.connect(self.load_contacts)
        header_layout.addWidget(self.refresh_button)
        
        layout.addLayout(header_layout)
        
        # Table
        self.table = QTableWidget()
        self.table.setColumnCount(6)
        self.table.setHorizontalHeaderLabels([
            "ID", "Name", "Email", "Phone", "Company", "Type"
        ])
        self.table.horizontalHeader().setStretchLastSection(True)
        self.table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self.table.doubleClicked.connect(self.view_contact)
        
        layout.addWidget(self.table)
        
        self.setLayout(layout)
    
    def load_contacts(self):
        """Load contacts into the table."""
        contacts = self.contact_service.get_contacts()
        self.table.setRowCount(len(contacts))
        
        for row, contact in enumerate(contacts):
            self.table.setItem(row, 0, QTableWidgetItem(str(contact.id)))
            self.table.setItem(row, 1, QTableWidgetItem(f"{contact.first_name} {contact.last_name}"))
            self.table.setItem(row, 2, QTableWidgetItem(contact.email or ""))
            self.table.setItem(row, 3, QTableWidgetItem(contact.phone or ""))
            self.table.setItem(row, 4, QTableWidgetItem(contact.company or ""))
            self.table.setItem(row, 5, QTableWidgetItem(contact.contact_type or ""))
        
        self.table.resizeColumnsToContents()
    
    def search_contacts(self, text):
        """Search contacts."""
        if not text:
            self.load_contacts()
            return
        
        contacts = self.contact_service.search_contacts(text)
        self.table.setRowCount(len(contacts))
        
        for row, contact in enumerate(contacts):
            self.table.setItem(row, 0, QTableWidgetItem(str(contact.id)))
            self.table.setItem(row, 1, QTableWidgetItem(f"{contact.first_name} {contact.last_name}"))
            self.table.setItem(row, 2, QTableWidgetItem(contact.email or ""))
            self.table.setItem(row, 3, QTableWidgetItem(contact.phone or ""))
            self.table.setItem(row, 4, QTableWidgetItem(contact.company or ""))
            self.table.setItem(row, 5, QTableWidgetItem(contact.contact_type or ""))
    
    def add_contact(self):
        """Open dialog to add a new contact."""
        from src.gui.dialogs.contact_dialog import ContactDialog
        dialog = ContactDialog(self)
        if dialog.exec():
            self.load_contacts()
    
    def view_contact(self, index):
        """View/edit contact details."""
        self.edit_contact()
    
    def edit_contact(self):
        """Open dialog to edit selected contact."""
        selected_rows = self.table.selectionModel().selectedRows()
        if not selected_rows:
            QMessageBox.warning(self, "No Selection", "Please select a contact to edit.")
            return
        
        row = selected_rows[0].row()
        contact_id = int(self.table.item(row, 0).text())
        from src.gui.dialogs.contact_dialog import ContactDialog
        dialog = ContactDialog(self, contact_id=contact_id)
        if dialog.exec():
            self.load_contacts()
    
    def delete_contact(self):
        """Delete selected contact."""
        selected_rows = self.table.selectionModel().selectedRows()
        if not selected_rows:
            QMessageBox.warning(self, "No Selection", "Please select a contact to delete.")
            return
        
        reply = QMessageBox.question(
            self, "Confirm Delete", 
            "Are you sure you want to delete this contact?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            row = selected_rows[0].row()
            contact_id = int(self.table.item(row, 0).text())
            if self.contact_service.delete_contact(contact_id):
                self.load_contacts()
            else:
                QMessageBox.warning(self, "Error", "Failed to delete contact.")

