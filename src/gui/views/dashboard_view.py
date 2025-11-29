"""
Dashboard view showing overview statistics.
"""
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QGridLayout, QGroupBox
)
from PyQt6.QtCore import Qt
from src.erp.financial_service import FinancialService
from src.erp.inventory_service import InventoryService
from src.crm.contact_service import ContactService
from src.crm.sales_service import SalesService


class DashboardView(QWidget):
    """Dashboard view with key metrics."""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.financial_service = FinancialService()
        self.inventory_service = InventoryService()
        self.contact_service = ContactService()
        self.sales_service = SalesService()
        self.init_ui()
        self.load_statistics()
    
    def init_ui(self):
        """Initialize the UI."""
        layout = QVBoxLayout()
        
        # Title
        title = QLabel("Dashboard")
        title.setStyleSheet("font-size: 24px; font-weight: bold; padding: 10px;")
        layout.addWidget(title)
        
        # Statistics grid
        grid = QGridLayout()
        
        # Financial metrics
        financial_group = QGroupBox("Financial")
        financial_layout = QVBoxLayout()
        self.total_invoices_label = QLabel("Total Invoices: 0")
        self.total_revenue_label = QLabel("Total Revenue: $0.00")
        financial_layout.addWidget(self.total_invoices_label)
        financial_layout.addWidget(self.total_revenue_label)
        financial_group.setLayout(financial_layout)
        grid.addWidget(financial_group, 0, 0)
        
        # CRM metrics
        crm_group = QGroupBox("CRM")
        crm_layout = QVBoxLayout()
        self.total_contacts_label = QLabel("Total Contacts: 0")
        self.total_opportunities_label = QLabel("Active Opportunities: 0")
        crm_layout.addWidget(self.total_contacts_label)
        crm_layout.addWidget(self.total_opportunities_label)
        crm_group.setLayout(crm_layout)
        grid.addWidget(crm_group, 0, 1)
        
        # Inventory metrics
        inventory_group = QGroupBox("Inventory")
        inventory_layout = QVBoxLayout()
        self.total_products_label = QLabel("Total Products: 0")
        self.low_stock_label = QLabel("Low Stock Items: 0")
        inventory_layout.addWidget(self.total_products_label)
        inventory_layout.addWidget(self.low_stock_label)
        inventory_group.setLayout(inventory_layout)
        grid.addWidget(inventory_group, 1, 0)
        
        # Sales metrics
        sales_group = QGroupBox("Sales")
        sales_layout = QVBoxLayout()
        self.pipeline_value_label = QLabel("Pipeline Value: $0.00")
        self.won_opportunities_label = QLabel("Won This Month: 0")
        sales_layout.addWidget(self.pipeline_value_label)
        sales_layout.addWidget(self.won_opportunities_label)
        sales_group.setLayout(sales_layout)
        grid.addWidget(sales_group, 1, 1)
        
        layout.addLayout(grid)
        layout.addStretch()
        
        self.setLayout(layout)
    
    def load_statistics(self):
        """Load and display statistics."""
        try:
            # Financial
            invoices = self.financial_service.get_invoices()
            total_revenue = sum(inv.total for inv in invoices if inv.status and inv.status.value == "paid")
            self.total_invoices_label.setText(f"Total Invoices: {len(invoices)}")
            self.total_revenue_label.setText(f"Total Revenue: ${total_revenue:.2f}")
            
            # CRM
            contacts = self.contact_service.get_contacts()
            opportunities = self.sales_service.get_opportunities()
            self.total_contacts_label.setText(f"Total Contacts: {len(contacts)}")
            self.total_opportunities_label.setText(f"Active Opportunities: {len(opportunities)}")
            
            # Inventory
            products = self.inventory_service.get_products()
            low_stock = self.inventory_service.get_low_stock_products()
            self.total_products_label.setText(f"Total Products: {len(products)}")
            self.low_stock_label.setText(f"Low Stock Items: {len(low_stock)}")
            
            # Sales
            pipeline_value = sum(opp.value * (opp.probability / 100) for opp in opportunities)
            self.pipeline_value_label.setText(f"Pipeline Value: ${pipeline_value:.2f}")
            self.won_opportunities_label.setText("Won This Month: 0")  # TODO: Calculate
            
        except Exception as e:
            print(f"Error loading statistics: {e}")

