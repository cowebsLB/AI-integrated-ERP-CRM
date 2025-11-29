"""
Invoices view for Financial module.
"""
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QTableWidget, QTableWidgetItem,
    QPushButton, QLabel, QHeaderView, QMessageBox
)
from PyQt6.QtCore import Qt
from src.erp.financial_service import FinancialService


class InvoicesView(QWidget):
    """View for managing invoices."""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.financial_service = FinancialService()
        self.init_ui()
        self.load_invoices()
    
    def init_ui(self):
        """Initialize the UI."""
        layout = QVBoxLayout()
        
        # Header
        header_layout = QHBoxLayout()
        title = QLabel("Invoices")
        title.setStyleSheet("font-size: 18px; font-weight: bold;")
        header_layout.addWidget(title)
        header_layout.addStretch()
        
        self.add_button = QPushButton("Create Invoice")
        self.add_button.clicked.connect(self.add_invoice)
        header_layout.addWidget(self.add_button)
        
        self.edit_button = QPushButton("Edit")
        self.edit_button.clicked.connect(self.edit_invoice)
        header_layout.addWidget(self.edit_button)
        
        self.delete_button = QPushButton("Delete")
        self.delete_button.clicked.connect(self.delete_invoice)
        header_layout.addWidget(self.delete_button)
        
        self.refresh_button = QPushButton("Refresh")
        self.refresh_button.clicked.connect(self.load_invoices)
        header_layout.addWidget(self.refresh_button)
        
        layout.addLayout(header_layout)
        
        # Table
        self.table = QTableWidget()
        self.table.setColumnCount(6)
        self.table.setHorizontalHeaderLabels([
            "Invoice #", "Customer", "Date", "Due Date", "Total", "Status"
        ])
        self.table.horizontalHeader().setStretchLastSection(True)
        self.table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        
        layout.addWidget(self.table)
        
        self.setLayout(layout)
    
    def load_invoices(self):
        """Load invoices into the table."""
        invoices = self.financial_service.get_invoices()
        self.table.setRowCount(len(invoices))
        
        for row, invoice in enumerate(invoices):
            self.table.setItem(row, 0, QTableWidgetItem(invoice.invoice_number))
            self.table.setItem(row, 1, QTableWidgetItem(str(invoice.customer_id) if invoice.customer_id else ""))
            self.table.setItem(row, 2, QTableWidgetItem(invoice.issue_date.strftime("%Y-%m-%d") if invoice.issue_date else ""))
            self.table.setItem(row, 3, QTableWidgetItem(invoice.due_date.strftime("%Y-%m-%d") if invoice.due_date else ""))
            self.table.setItem(row, 4, QTableWidgetItem(f"${invoice.total:.2f}"))
            self.table.setItem(row, 5, QTableWidgetItem(invoice.status.value if invoice.status else ""))
        
        self.table.resizeColumnsToContents()
    
    def add_invoice(self):
        """Open dialog to create a new invoice."""
        from src.gui.dialogs.invoice_dialog import InvoiceDialog
        dialog = InvoiceDialog(self)
        if dialog.exec():
            self.load_invoices()
    
    def edit_invoice(self):
        """Open dialog to edit selected invoice."""
        selected_rows = self.table.selectionModel().selectedRows()
        if not selected_rows:
            QMessageBox.warning(self, "No Selection", "Please select an invoice to edit.")
            return
        
        row = selected_rows[0].row()
        invoice_number = self.table.item(row, 0).text()
        invoices = self.financial_service.get_invoices()
        invoice = next((i for i in invoices if i.invoice_number == invoice_number), None)
        
        if invoice:
            # Note: Invoice editing might need a more complex dialog
            # For now, just show a message
            QMessageBox.information(self, "Edit Invoice", 
                                  "Invoice editing will be implemented in a future update.")
    
    def delete_invoice(self):
        """Delete selected invoice."""
        selected_rows = self.table.selectionModel().selectedRows()
        if not selected_rows:
            QMessageBox.warning(self, "No Selection", "Please select an invoice to delete.")
            return
        
        reply = QMessageBox.question(
            self, "Confirm Delete", 
            "Are you sure you want to delete this invoice?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            row = selected_rows[0].row()
            invoice_number = self.table.item(row, 0).text()
            invoices = self.financial_service.get_invoices()
            invoice = next((i for i in invoices if i.invoice_number == invoice_number), None)
            
            if invoice:
                if self.financial_service.delete_invoice(invoice.id):
                    self.load_invoices()
                else:
                    QMessageBox.warning(self, "Error", "Failed to delete invoice.")

