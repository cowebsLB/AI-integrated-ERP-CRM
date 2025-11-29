"""
Contact dialog for adding/editing contacts.
"""
from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QFormLayout,
    QLineEdit, QPushButton, QComboBox, QTextEdit, QLabel
)
from PyQt6.QtCore import Qt
from src.crm.contact_service import ContactService


class ContactDialog(QDialog):
    """Dialog for adding or editing a contact."""
    
    def __init__(self, parent=None, contact_id=None):
        super().__init__(parent)
        self.contact_service = ContactService()
        self.contact_id = contact_id
        self.init_ui()
        
        if contact_id:
            self.load_contact()
    
    def init_ui(self):
        """Initialize the UI."""
        self.setWindowTitle("Add Contact" if not self.contact_id else "Edit Contact")
        self.setMinimumWidth(400)
        
        layout = QVBoxLayout()
        
        # Form
        form = QFormLayout()
        
        self.first_name_input = QLineEdit()
        form.addRow("First Name:", self.first_name_input)
        
        self.last_name_input = QLineEdit()
        form.addRow("Last Name:", self.last_name_input)
        
        self.email_input = QLineEdit()
        form.addRow("Email:", self.email_input)
        
        self.phone_input = QLineEdit()
        form.addRow("Phone:", self.phone_input)
        
        self.company_input = QLineEdit()
        form.addRow("Company:", self.company_input)
        
        self.type_combo = QComboBox()
        self.type_combo.addItems(["customer", "lead", "vendor", "partner"])
        form.addRow("Type:", self.type_combo)
        
        self.notes_input = QTextEdit()
        self.notes_input.setMaximumHeight(100)
        form.addRow("Notes:", self.notes_input)
        
        layout.addLayout(form)
        
        # Buttons
        button_layout = QHBoxLayout()
        button_layout.addStretch()
        
        self.save_button = QPushButton("Save")
        self.save_button.clicked.connect(self.save_contact)
        button_layout.addWidget(self.save_button)
        
        self.cancel_button = QPushButton("Cancel")
        self.cancel_button.clicked.connect(self.reject)
        button_layout.addWidget(self.cancel_button)
        
        layout.addLayout(button_layout)
        
        self.setLayout(layout)
    
    def load_contact(self):
        """Load contact data into the form."""
        contact = self.contact_service.get_contact(self.contact_id)
        if contact:
            self.first_name_input.setText(contact.first_name)
            self.last_name_input.setText(contact.last_name)
            self.email_input.setText(contact.email or "")
            self.phone_input.setText(contact.phone or "")
            self.company_input.setText(contact.company or "")
            index = self.type_combo.findText(contact.contact_type)
            if index >= 0:
                self.type_combo.setCurrentIndex(index)
            self.notes_input.setPlainText(contact.notes or "")
    
    def save_contact(self):
        """Save the contact."""
        first_name = self.first_name_input.text().strip()
        last_name = self.last_name_input.text().strip()
        
        if not first_name or not last_name:
            from PyQt6.QtWidgets import QMessageBox
            QMessageBox.warning(self, "Validation Error", "First name and last name are required.")
            return
        
        if self.contact_id:
            # Update existing contact
            self.contact_service.update_contact(
                self.contact_id,
                first_name=first_name,
                last_name=last_name,
                email=self.email_input.text().strip() or None,
                phone=self.phone_input.text().strip() or None,
                company=self.company_input.text().strip() or None,
                contact_type=self.type_combo.currentText(),
                notes=self.notes_input.toPlainText() or None
            )
        else:
            # Create new contact
            self.contact_service.create_contact(
                first_name=first_name,
                last_name=last_name,
                email=self.email_input.text().strip() or None,
                phone=self.phone_input.text().strip() or None,
                company=self.company_input.text().strip() or None,
                contact_type=self.type_combo.currentText()
            )
        
        self.accept()

