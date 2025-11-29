"""
Invoice dialog for creating/editing invoices.
"""
from datetime import datetime, timedelta
from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QFormLayout,
    QLineEdit, QPushButton, QDateEdit, QTableWidget, QTableWidgetItem,
    QDoubleSpinBox, QComboBox, QMessageBox, QHeaderView, QLabel
)
from PyQt6.QtCore import Qt, QDate
from src.erp.financial_service import FinancialService
from src.crm.contact_service import ContactService


class InvoiceDialog(QDialog):
    """Dialog for creating or editing an invoice."""
    
    def __init__(self, parent=None, invoice_id=None):
        super().__init__(parent)
        self.financial_service = FinancialService()
        self.contact_service = ContactService()
        self.invoice_id = invoice_id
        self.items = []
        self.init_ui()
        
        if invoice_id:
            self.load_invoice()
    
    def init_ui(self):
        """Initialize the UI."""
        self.setWindowTitle("Create Invoice" if not self.invoice_id else "Edit Invoice")
        self.setMinimumWidth(600)
        
        layout = QVBoxLayout()
        
        # Form
        form = QFormLayout()
        
        self.invoice_number_input = QLineEdit()
        if not self.invoice_id:
            self.invoice_number_input.setText(f"INV-{datetime.now().strftime('%Y%m%d-%H%M%S')}")
        form.addRow("Invoice Number:", self.invoice_number_input)
        
        # Customer selection
        self.customer_combo = QComboBox()
        contacts = self.contact_service.get_contacts(contact_type="customer")
        self.customer_combo.addItem("", None)
        for contact in contacts:
            self.customer_combo.addItem(f"{contact.first_name} {contact.last_name} ({contact.company or 'No Company'})", contact.id)
        form.addRow("Customer:", self.customer_combo)
        
        self.issue_date_input = QDateEdit()
        self.issue_date_input.setDate(QDate.currentDate())
        form.addRow("Issue Date:", self.issue_date_input)
        
        self.due_date_input = QDateEdit()
        self.due_date_input.setDate(QDate.currentDate().addDays(30))
        form.addRow("Due Date:", self.due_date_input)
        
        layout.addLayout(form)
        
        # Items table
        items_label = QLabel("Invoice Items:")
        items_label.setStyleSheet("font-weight: bold;")
        layout.addWidget(items_label)
        
        self.items_table = QTableWidget()
        self.items_table.setColumnCount(4)
        self.items_table.setHorizontalHeaderLabels(["Description", "Quantity", "Unit Price", "Total"])
        self.items_table.horizontalHeader().setStretchLastSection(True)
        self.items_table.setMinimumHeight(200)
        layout.addWidget(self.items_table)
        
        # Add item button
        add_item_btn = QPushButton("Add Item")
        add_item_btn.clicked.connect(self.add_item_row)
        layout.addWidget(add_item_btn)
        
        # Totals
        totals_layout = QHBoxLayout()
        totals_layout.addStretch()
        
        subtotal_label = QLabel("Subtotal: $0.00")
        subtotal_label.setStyleSheet("font-weight: bold;")
        self.subtotal_label = subtotal_label
        totals_layout.addWidget(subtotal_label)
        
        tax_label = QLabel("Tax (10%): $0.00")
        self.tax_label = tax_label
        totals_layout.addWidget(tax_label)
        
        total_label = QLabel("Total: $0.00")
        total_label.setStyleSheet("font-size: 14px; font-weight: bold;")
        self.total_label = total_label
        totals_layout.addWidget(total_label)
        
        layout.addLayout(totals_layout)
        
        # Buttons
        button_layout = QHBoxLayout()
        button_layout.addStretch()
        
        self.save_button = QPushButton("Save Invoice")
        self.save_button.clicked.connect(self.save_invoice)
        button_layout.addWidget(self.save_button)
        
        self.cancel_button = QPushButton("Cancel")
        self.cancel_button.clicked.connect(self.reject)
        button_layout.addWidget(self.cancel_button)
        
        layout.addLayout(button_layout)
        
        self.setLayout(layout)
        
        # Connect table changes to update totals
        self.items_table.cellChanged.connect(self.update_totals)
    
    def add_item_row(self):
        """Add a new row to the items table."""
        row = self.items_table.rowCount()
        self.items_table.insertRow(row)
        
        desc_item = QTableWidgetItem()
        self.items_table.setItem(row, 0, desc_item)
        
        qty_item = QTableWidgetItem("1")
        self.items_table.setItem(row, 1, qty_item)
        
        price_item = QTableWidgetItem("0.00")
        self.items_table.setItem(row, 2, price_item)
        
        total_item = QTableWidgetItem("0.00")
        total_item.setFlags(total_item.flags() & ~Qt.ItemFlag.ItemIsEditable)
        self.items_table.setItem(row, 3, total_item)
    
    def update_totals(self, row, column):
        """Update item total and invoice totals."""
        if column in [1, 2]:  # Quantity or Unit Price changed
            qty_item = self.items_table.item(row, 1)
            price_item = self.items_table.item(row, 2)
            
            if qty_item and price_item:
                try:
                    qty = float(qty_item.text() or 0)
                    price = float(price_item.text() or 0)
                    total = qty * price
                    
                    total_item = self.items_table.item(row, 3)
                    if not total_item:
                        total_item = QTableWidgetItem()
                        total_item.setFlags(total_item.flags() & ~Qt.ItemFlag.ItemIsEditable)
                        self.items_table.setItem(row, 3, total_item)
                    total_item.setText(f"{total:.2f}")
                except ValueError:
                    pass
        
        # Calculate invoice totals
        subtotal = 0.0
        for row in range(self.items_table.rowCount()):
            total_item = self.items_table.item(row, 3)
            if total_item:
                try:
                    subtotal += float(total_item.text() or 0)
                except ValueError:
                    pass
        
        tax = subtotal * 0.1
        total = subtotal + tax
        
        self.subtotal_label.setText(f"Subtotal: ${subtotal:.2f}")
        self.tax_label.setText(f"Tax (10%): ${tax:.2f}")
        self.total_label.setText(f"Total: ${total:.2f}")
    
    def load_invoice(self):
        """Load invoice data into the form."""
        # TODO: Implement invoice loading
        pass
    
    def save_invoice(self):
        """Save the invoice."""
        invoice_number = self.invoice_number_input.text().strip()
        if not invoice_number:
            QMessageBox.warning(self, "Validation Error", "Invoice number is required.")
            return
        
        # Collect items
        items = []
        for row in range(self.items_table.rowCount()):
            desc_item = self.items_table.item(row, 0)
            qty_item = self.items_table.item(row, 1)
            price_item = self.items_table.item(row, 2)
            
            if desc_item and desc_item.text().strip():
                try:
                    items.append({
                        'description': desc_item.text().strip(),
                        'quantity': float(qty_item.text() or 1) if qty_item else 1.0,
                        'unit_price': float(price_item.text() or 0) if price_item else 0.0
                    })
                except ValueError:
                    QMessageBox.warning(self, "Validation Error", f"Invalid quantity or price in row {row + 1}")
                    return
        
        if not items:
            QMessageBox.warning(self, "Validation Error", "At least one invoice item is required.")
            return
        
        try:
            customer_id = self.customer_combo.currentData()
            due_date = self.due_date_input.date().toPyDate()
            due_date = datetime.combine(due_date, datetime.min.time())
            
            self.financial_service.create_invoice(
                invoice_number=invoice_number,
                customer_id=customer_id,
                due_date=due_date,
                items=items
            )
            
            self.accept()
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to save invoice: {str(e)}")

