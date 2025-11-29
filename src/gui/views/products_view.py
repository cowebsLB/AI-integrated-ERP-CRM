"""
Products view for Inventory module.
"""
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QTableWidget, QTableWidgetItem,
    QPushButton, QLabel, QHeaderView, QMessageBox
)
from PyQt6.QtCore import Qt
from src.erp.inventory_service import InventoryService


class ProductsView(QWidget):
    """View for managing products."""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.inventory_service = InventoryService()
        self.init_ui()
        self.load_products()
    
    def init_ui(self):
        """Initialize the UI."""
        layout = QVBoxLayout()
        
        # Header
        header_layout = QHBoxLayout()
        title = QLabel("Products")
        title.setStyleSheet("font-size: 18px; font-weight: bold;")
        header_layout.addWidget(title)
        header_layout.addStretch()
        
        self.add_button = QPushButton("Add Product")
        self.add_button.clicked.connect(self.add_product)
        header_layout.addWidget(self.add_button)
        
        self.edit_button = QPushButton("Edit")
        self.edit_button.clicked.connect(self.edit_product)
        header_layout.addWidget(self.edit_button)
        
        self.delete_button = QPushButton("Delete")
        self.delete_button.clicked.connect(self.delete_product)
        header_layout.addWidget(self.delete_button)
        
        self.refresh_button = QPushButton("Refresh")
        self.refresh_button.clicked.connect(self.load_products)
        header_layout.addWidget(self.refresh_button)
        
        layout.addLayout(header_layout)
        
        # Table
        self.table = QTableWidget()
        self.table.setColumnCount(6)
        self.table.setHorizontalHeaderLabels([
            "SKU", "Name", "Category", "Price", "Stock", "Status"
        ])
        self.table.horizontalHeader().setStretchLastSection(True)
        self.table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        
        layout.addWidget(self.table)
        
        self.setLayout(layout)
    
    def load_products(self):
        """Load products into the table."""
        products = self.inventory_service.get_products()
        self.table.setRowCount(len(products))
        
        for row, product in enumerate(products):
            self.table.setItem(row, 0, QTableWidgetItem(product.sku))
            self.table.setItem(row, 1, QTableWidgetItem(product.name))
            self.table.setItem(row, 2, QTableWidgetItem(product.category or ""))
            self.table.setItem(row, 3, QTableWidgetItem(f"${product.unit_price:.2f}"))
            self.table.setItem(row, 4, QTableWidgetItem(f"{product.stock_quantity} {product.unit}"))
            status = "Active" if product.is_active else "Inactive"
            self.table.setItem(row, 5, QTableWidgetItem(status))
        
        self.table.resizeColumnsToContents()
    
    def add_product(self):
        """Open dialog to add a new product."""
        from src.gui.dialogs.product_dialog import ProductDialog
        dialog = ProductDialog(self)
        if dialog.exec():
            self.load_products()
    
    def edit_product(self):
        """Open dialog to edit selected product."""
        selected_rows = self.table.selectionModel().selectedRows()
        if not selected_rows:
            QMessageBox.warning(self, "No Selection", "Please select a product to edit.")
            return
        
        row = selected_rows[0].row()
        sku = self.table.item(row, 0).text()
        products = self.inventory_service.get_products()
        product = next((p for p in products if p.sku == sku), None)
        
        if product:
            from src.gui.dialogs.product_dialog import ProductDialog
            dialog = ProductDialog(self, product_id=product.id)
            if dialog.exec():
                self.load_products()
    
    def delete_product(self):
        """Delete selected product."""
        selected_rows = self.table.selectionModel().selectedRows()
        if not selected_rows:
            QMessageBox.warning(self, "No Selection", "Please select a product to delete.")
            return
        
        reply = QMessageBox.question(
            self, "Confirm Delete", 
            "Are you sure you want to delete this product?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            row = selected_rows[0].row()
            sku = self.table.item(row, 0).text()
            products = self.inventory_service.get_products()
            product = next((p for p in products if p.sku == sku), None)
            
            if product:
                if self.inventory_service.delete_product(product.id):
                    self.load_products()
                else:
                    QMessageBox.warning(self, "Error", "Failed to delete product.")

