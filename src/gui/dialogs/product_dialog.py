"""
Product dialog for adding/editing products.
"""
from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QFormLayout,
    QLineEdit, QPushButton, QDoubleSpinBox, QTextEdit, QMessageBox
)
from PyQt6.QtCore import Qt
from src.erp.inventory_service import InventoryService
from src.database.models.erp_models import Product


class ProductDialog(QDialog):
    """Dialog for adding or editing a product."""
    
    def __init__(self, parent=None, product_id=None):
        super().__init__(parent)
        self.inventory_service = InventoryService()
        self.product_id = product_id
        self.init_ui()
        
        if product_id:
            self.load_product()
    
    def init_ui(self):
        """Initialize the UI."""
        self.setWindowTitle("Add Product" if not self.product_id else "Edit Product")
        self.setMinimumWidth(400)
        
        layout = QVBoxLayout()
        
        # Form
        form = QFormLayout()
        
        self.sku_input = QLineEdit()
        form.addRow("SKU:", self.sku_input)
        
        self.name_input = QLineEdit()
        form.addRow("Name:", self.name_input)
        
        self.category_input = QLineEdit()
        form.addRow("Category:", self.category_input)
        
        self.unit_price_input = QDoubleSpinBox()
        self.unit_price_input.setMaximum(999999.99)
        self.unit_price_input.setDecimals(2)
        form.addRow("Unit Price:", self.unit_price_input)
        
        self.cost_price_input = QDoubleSpinBox()
        self.cost_price_input.setMaximum(999999.99)
        self.cost_price_input.setDecimals(2)
        form.addRow("Cost Price:", self.cost_price_input)
        
        self.stock_input = QDoubleSpinBox()
        self.stock_input.setMaximum(999999.99)
        self.stock_input.setDecimals(2)
        form.addRow("Stock Quantity:", self.stock_input)
        
        self.min_stock_input = QDoubleSpinBox()
        self.min_stock_input.setMaximum(999999.99)
        self.min_stock_input.setDecimals(2)
        form.addRow("Min Stock Level:", self.min_stock_input)
        
        self.description_input = QTextEdit()
        self.description_input.setMaximumHeight(100)
        form.addRow("Description:", self.description_input)
        
        layout.addLayout(form)
        
        # Buttons
        button_layout = QHBoxLayout()
        button_layout.addStretch()
        
        self.save_button = QPushButton("Save")
        self.save_button.clicked.connect(self.save_product)
        button_layout.addWidget(self.save_button)
        
        self.cancel_button = QPushButton("Cancel")
        self.cancel_button.clicked.connect(self.reject)
        button_layout.addWidget(self.cancel_button)
        
        layout.addLayout(button_layout)
        
        self.setLayout(layout)
    
    def load_product(self):
        """Load product data into the form."""
        product = self.inventory_service.db.query(Product).filter(Product.id == self.product_id).first()
        if product:
            self.sku_input.setText(product.sku)
            self.name_input.setText(product.name)
            self.category_input.setText(product.category or "")
            self.unit_price_input.setValue(product.unit_price)
            self.cost_price_input.setValue(product.cost_price)
            self.stock_input.setValue(product.stock_quantity)
            self.min_stock_input.setValue(product.min_stock_level)
            self.description_input.setPlainText(product.description or "")
    
    def save_product(self):
        """Save the product."""
        sku = self.sku_input.text().strip()
        name = self.name_input.text().strip()
        
        if not sku or not name:
            QMessageBox.warning(self, "Validation Error", "SKU and Name are required.")
            return
        
        try:
            if self.product_id:
                # Update existing product
                product = self.inventory_service.db.query(Product).filter(Product.id == self.product_id).first()
                if product:
                    product.sku = sku
                    product.name = name
                    product.category = self.category_input.text().strip() or None
                    product.unit_price = self.unit_price_input.value()
                    product.cost_price = self.cost_price_input.value()
                    product.stock_quantity = self.stock_input.value()
                    product.min_stock_level = self.min_stock_input.value()
                    product.description = self.description_input.toPlainText() or None
                    self.inventory_service.db.commit()
            else:
                # Create new product
                self.inventory_service.create_product(
                    sku=sku,
                    name=name,
                    category=self.category_input.text().strip() or None,
                    unit_price=self.unit_price_input.value(),
                    cost_price=self.cost_price_input.value(),
                    stock_quantity=self.stock_input.value(),
                    min_stock_level=self.min_stock_input.value(),
                    description=self.description_input.toPlainText() or None
                )
            
            self.accept()
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to save product: {str(e)}")

