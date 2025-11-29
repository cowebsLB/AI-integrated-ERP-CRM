"""
AI Insights view with charts and analytics for all modules.
"""
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QTabWidget, QLabel, QGroupBox, QGridLayout
)
from PyQt6.QtCore import Qt
import pyqtgraph as pg
from datetime import datetime, timedelta
from collections import defaultdict

from src.erp.financial_service import FinancialService
from src.erp.inventory_service import InventoryService
from src.erp.hr_service import HRService
from src.erp.project_service import ProjectService
from src.crm.contact_service import ContactService
from src.crm.sales_service import SalesService
from src.crm.marketing_service import MarketingService
from src.crm.service_service import ServiceService


class AIInsightsView(QWidget):
    """View for AI-powered insights and analytics with charts."""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.financial_service = FinancialService()
        self.inventory_service = InventoryService()
        self.hr_service = HRService()
        self.project_service = ProjectService()
        self.contact_service = ContactService()
        self.sales_service = SalesService()
        self.marketing_service = MarketingService()
        self.service_service = ServiceService()
        
        self.init_ui()
        self.load_all_charts()
    
    def init_ui(self):
        """Initialize the UI."""
        layout = QVBoxLayout()
        
        # Title
        title = QLabel("AI Insights & Analytics")
        title.setStyleSheet("font-size: 24px; font-weight: bold; padding: 10px;")
        layout.addWidget(title)
        
        # Tab widget for different modules
        self.tabs = QTabWidget()
        
        # Financial tab
        self.financial_tab = QWidget()
        self.financial_layout = QVBoxLayout()
        self.financial_tab.setLayout(self.financial_layout)
        self.tabs.addTab(self.financial_tab, "Financial")
        
        # Inventory tab
        self.inventory_tab = QWidget()
        self.inventory_layout = QVBoxLayout()
        self.inventory_tab.setLayout(self.inventory_layout)
        self.tabs.addTab(self.inventory_tab, "Inventory")
        
        # Sales tab
        self.sales_tab = QWidget()
        self.sales_layout = QVBoxLayout()
        self.sales_tab.setLayout(self.sales_layout)
        self.tabs.addTab(self.sales_tab, "Sales")
        
        # HR tab
        self.hr_tab = QWidget()
        self.hr_layout = QVBoxLayout()
        self.hr_tab.setLayout(self.hr_layout)
        self.tabs.addTab(self.hr_tab, "Human Resources")
        
        # Projects tab
        self.projects_tab = QWidget()
        self.projects_layout = QVBoxLayout()
        self.projects_tab.setLayout(self.projects_layout)
        self.tabs.addTab(self.projects_tab, "Projects")
        
        # CRM tab
        self.crm_tab = QWidget()
        self.crm_layout = QVBoxLayout()
        self.crm_tab.setLayout(self.crm_layout)
        self.tabs.addTab(self.crm_tab, "CRM")
        
        layout.addWidget(self.tabs)
        self.setLayout(layout)
    
    def load_all_charts(self):
        """Load charts for all modules."""
        self.load_financial_charts()
        self.load_inventory_charts()
        self.load_sales_charts()
        self.load_hr_charts()
        self.load_projects_charts()
        self.load_crm_charts()
    
    def load_financial_charts(self):
        """Load financial analytics charts."""
        invoices = self.financial_service.get_invoices()
        
        # Revenue by status
        status_revenue = defaultdict(float)
        for inv in invoices:
            status = inv.status.value if inv.status else "unknown"
            status_revenue[status] += inv.total
        
        if status_revenue:
            widget = pg.GraphicsLayoutWidget()
            plot = widget.addPlot(title="Revenue by Invoice Status")
            x = list(range(len(status_revenue)))
            y = list(status_revenue.values())
            plot.setLabel('left', 'Revenue ($)')
            plot.setLabel('bottom', 'Status')
            plot.getAxis('bottom').setTicks([[(i, status) for i, status in enumerate(status_revenue.keys())]])
            bg = pg.BarGraphItem(x=x, height=y, width=0.6, brush='b')
            plot.addItem(bg)
            
            group = QGroupBox("Revenue by Invoice Status")
            group_layout = QVBoxLayout()
            group_layout.addWidget(widget)
            group.setLayout(group_layout)
            self.financial_layout.addWidget(group)
        
        # Monthly revenue trend
        monthly_revenue = defaultdict(float)
        for inv in invoices:
            if inv.issue_date:
                month_key = inv.issue_date.strftime("%Y-%m")
                if inv.status and inv.status.value == "paid":
                    monthly_revenue[month_key] += inv.total
        
        if monthly_revenue:
            widget = pg.GraphicsLayoutWidget()
            plot = widget.addPlot(title="Monthly Revenue Trend")
            months = sorted(monthly_revenue.keys())
            revenue = [monthly_revenue[m] for m in months]
            plot.plot(months, revenue, pen='g', symbol='o', symbolBrush='g')
            plot.setLabel('left', 'Revenue ($)')
            plot.setLabel('bottom', 'Month')
            
            group = QGroupBox("Monthly Revenue Trend")
            group_layout = QVBoxLayout()
            group_layout.addWidget(widget)
            group.setLayout(group_layout)
            self.financial_layout.addWidget(group)
        
        self.financial_layout.addStretch()
    
    def load_inventory_charts(self):
        """Load inventory analytics charts."""
        products = self.inventory_service.get_products()
        low_stock = self.inventory_service.get_low_stock_products()
        
        # Stock levels
        if products:
            widget = pg.GraphicsLayoutWidget()
            plot = widget.addPlot(title="Product Stock Levels")
            product_names = [p.name[:20] for p in products[:10]]  # Top 10
            stock_levels = [p.stock_quantity for p in products[:10]]
            x = list(range(len(product_names)))
            bg = pg.BarGraphItem(x=x, height=stock_levels, width=0.6, brush='c')
            plot.addItem(bg)
            plot.setLabel('left', 'Stock Quantity')
            plot.setLabel('bottom', 'Products')
            plot.getAxis('bottom').setTicks([[(i, name) for i, name in enumerate(product_names)]])
            
            group = QGroupBox("Top 10 Products by Stock")
            group_layout = QVBoxLayout()
            group_layout.addWidget(widget)
            group.setLayout(group_layout)
            self.inventory_layout.addWidget(group)
        
        # Low stock alert
        if low_stock:
            widget = pg.GraphicsLayoutWidget()
            plot = widget.addPlot(title="Low Stock Products")
            product_names = [p.name[:20] for p in low_stock[:10]]
            stock_levels = [p.stock_quantity for p in low_stock[:10]]
            x = list(range(len(product_names)))
            bg = pg.BarGraphItem(x=x, height=stock_levels, width=0.6, brush='r')
            plot.addItem(bg)
            plot.setLabel('left', 'Stock Quantity')
            plot.setLabel('bottom', 'Products')
            plot.getAxis('bottom').setTicks([[(i, name) for i, name in enumerate(product_names)]])
            
            group = QGroupBox("Low Stock Alert")
            group_layout = QVBoxLayout()
            group_layout.addWidget(widget)
            group.setLayout(group_layout)
            self.inventory_layout.addWidget(group)
        
        self.inventory_layout.addStretch()
    
    def load_sales_charts(self):
        """Load sales analytics charts."""
        opportunities = self.sales_service.get_opportunities()
        leads = self.sales_service.get_leads()
        
        # Opportunities by stage
        stage_counts = defaultdict(int)
        for opp in opportunities:
            stage = opp.stage.value.replace("_", " ").title()
            stage_counts[stage] += 1
        
        if stage_counts:
            widget = pg.GraphicsLayoutWidget()
            plot = widget.addPlot(title="Opportunities by Stage")
            x = list(range(len(stage_counts)))
            y = list(stage_counts.values())
            bg = pg.BarGraphItem(x=x, height=y, width=0.6, brush='m')
            plot.addItem(bg)
            plot.setLabel('left', 'Count')
            plot.setLabel('bottom', 'Stage')
            plot.getAxis('bottom').setTicks([[(i, stage) for i, stage in enumerate(stage_counts.keys())]])
            
            group = QGroupBox("Sales Pipeline")
            group_layout = QVBoxLayout()
            group_layout.addWidget(widget)
            group.setLayout(group_layout)
            self.sales_layout.addWidget(group)
        
        # Pipeline value by stage
        stage_value = defaultdict(float)
        for opp in opportunities:
            stage = opp.stage.value.replace("_", " ").title()
            stage_value[stage] += opp.value * (opp.probability / 100)
        
        if stage_value:
            widget = pg.GraphicsLayoutWidget()
            plot = widget.addPlot(title="Pipeline Value by Stage")
            x = list(range(len(stage_value)))
            y = list(stage_value.values())
            bg = pg.BarGraphItem(x=x, height=y, width=0.6, brush='y')
            plot.addItem(bg)
            plot.setLabel('left', 'Value ($)')
            plot.setLabel('bottom', 'Stage')
            plot.getAxis('bottom').setTicks([[(i, stage) for i, stage in enumerate(stage_value.keys())]])
            
            group = QGroupBox("Pipeline Value")
            group_layout = QVBoxLayout()
            group_layout.addWidget(widget)
            group.setLayout(group_layout)
            self.sales_layout.addWidget(group)
        
        # Leads by status
        lead_status = defaultdict(int)
        for lead in leads:
            status = lead.status.value if lead.status else "unknown"
            lead_status[status] += 1
        
        if lead_status:
            widget = pg.GraphicsLayoutWidget()
            plot = widget.addPlot(title="Leads by Status")
            x = list(range(len(lead_status)))
            y = list(lead_status.values())
            bg = pg.BarGraphItem(x=x, height=y, width=0.6, brush='g')
            plot.addItem(bg)
            plot.setLabel('left', 'Count')
            plot.setLabel('bottom', 'Status')
            plot.getAxis('bottom').setTicks([[(i, status) for i, status in enumerate(lead_status.keys())]])
            
            group = QGroupBox("Lead Status Distribution")
            group_layout = QVBoxLayout()
            group_layout.addWidget(widget)
            group.setLayout(group_layout)
            self.sales_layout.addWidget(group)
        
        self.sales_layout.addStretch()
    
    def load_hr_charts(self):
        """Load HR analytics charts."""
        employees = self.hr_service.get_employees()
        attendance = self.hr_service.get_attendance()
        
        # Employees by department
        dept_counts = defaultdict(int)
        for emp in employees:
            dept = emp.department or "Unassigned"
            dept_counts[dept] += 1
        
        if dept_counts:
            widget = pg.GraphicsLayoutWidget()
            plot = widget.addPlot(title="Employees by Department")
            x = list(range(len(dept_counts)))
            y = list(dept_counts.values())
            bg = pg.BarGraphItem(x=x, height=y, width=0.6, brush='b')
            plot.addItem(bg)
            plot.setLabel('left', 'Count')
            plot.setLabel('bottom', 'Department')
            plot.getAxis('bottom').setTicks([[(i, dept) for i, dept in enumerate(dept_counts.keys())]])
            
            group = QGroupBox("Department Distribution")
            group_layout = QVBoxLayout()
            group_layout.addWidget(widget)
            group.setLayout(group_layout)
            self.hr_layout.addWidget(group)
        
        # Attendance by status
        if attendance:
            att_status = defaultdict(int)
            for att in attendance:
                status = att.status or "unknown"
                att_status[status] += 1
            
            if att_status:
                widget = pg.GraphicsLayoutWidget()
                plot = widget.addPlot(title="Attendance Status")
                x = list(range(len(att_status)))
                y = list(att_status.values())
                bg = pg.BarGraphItem(x=x, height=y, width=0.6, brush='c')
                plot.addItem(bg)
                plot.setLabel('left', 'Count')
                plot.setLabel('bottom', 'Status')
                plot.getAxis('bottom').setTicks([[(i, status) for i, status in enumerate(att_status.keys())]])
                
                group = QGroupBox("Attendance Overview")
                group_layout = QVBoxLayout()
                group_layout.addWidget(widget)
                group.setLayout(group_layout)
                self.hr_layout.addWidget(group)
        
        self.hr_layout.addStretch()
    
    def load_projects_charts(self):
        """Load project analytics charts."""
        projects = self.project_service.get_projects()
        tasks = self.project_service.get_tasks()
        
        # Projects by status
        status_counts = defaultdict(int)
        for proj in projects:
            status = proj.status or "unknown"
            status_counts[status] += 1
        
        if status_counts:
            widget = pg.GraphicsLayoutWidget()
            plot = widget.addPlot(title="Projects by Status")
            x = list(range(len(status_counts)))
            y = list(status_counts.values())
            bg = pg.BarGraphItem(x=x, height=y, width=0.6, brush='r')
            plot.addItem(bg)
            plot.setLabel('left', 'Count')
            plot.setLabel('bottom', 'Status')
            plot.getAxis('bottom').setTicks([[(i, status) for i, status in enumerate(status_counts.keys())]])
            
            group = QGroupBox("Project Status")
            group_layout = QVBoxLayout()
            group_layout.addWidget(widget)
            group.setLayout(group_layout)
            self.projects_layout.addWidget(group)
        
        # Tasks by status
        if tasks:
            task_status = defaultdict(int)
            for task in tasks:
                status = task.status or "unknown"
                task_status[status] += 1
            
            if task_status:
                widget = pg.GraphicsLayoutWidget()
                plot = widget.addPlot(title="Tasks by Status")
                x = list(range(len(task_status)))
                y = list(task_status.values())
                bg = pg.BarGraphItem(x=x, height=y, width=0.6, brush='g')
                plot.addItem(bg)
                plot.setLabel('left', 'Count')
                plot.setLabel('bottom', 'Status')
                plot.getAxis('bottom').setTicks([[(i, status) for i, status in enumerate(task_status.keys())]])
                
                group = QGroupBox("Task Status")
                group_layout = QVBoxLayout()
                group_layout.addWidget(widget)
                group.setLayout(group_layout)
                self.projects_layout.addWidget(group)
        
        self.projects_layout.addStretch()
    
    def load_crm_charts(self):
        """Load CRM analytics charts."""
        contacts = self.contact_service.get_contacts()
        tickets = self.service_service.get_tickets()
        campaigns = self.marketing_service.get_campaigns()
        
        # Contacts by type
        type_counts = defaultdict(int)
        for contact in contacts:
            ctype = contact.contact_type or "unknown"
            type_counts[ctype] += 1
        
        if type_counts:
            widget = pg.GraphicsLayoutWidget()
            plot = widget.addPlot(title="Contacts by Type")
            x = list(range(len(type_counts)))
            y = list(type_counts.values())
            bg = pg.BarGraphItem(x=x, height=y, width=0.6, brush='b')
            plot.addItem(bg)
            plot.setLabel('left', 'Count')
            plot.setLabel('bottom', 'Type')
            plot.getAxis('bottom').setTicks([[(i, ctype) for i, ctype in enumerate(type_counts.keys())]])
            
            group = QGroupBox("Contact Distribution")
            group_layout = QVBoxLayout()
            group_layout.addWidget(widget)
            group.setLayout(group_layout)
            self.crm_layout.addWidget(group)
        
        # Tickets by status
        if tickets:
            ticket_status = defaultdict(int)
            for ticket in tickets:
                status = ticket.status.value if ticket.status else "unknown"
                ticket_status[status] += 1
            
            if ticket_status:
                widget = pg.GraphicsLayoutWidget()
                plot = widget.addPlot(title="Support Tickets by Status")
                x = list(range(len(ticket_status)))
                y = list(ticket_status.values())
                bg = pg.BarGraphItem(x=x, height=y, width=0.6, brush='r')
                plot.addItem(bg)
                plot.setLabel('left', 'Count')
                plot.setLabel('bottom', 'Status')
                plot.getAxis('bottom').setTicks([[(i, status) for i, status in enumerate(ticket_status.keys())]])
                
                group = QGroupBox("Ticket Status")
                group_layout = QVBoxLayout()
                group_layout.addWidget(widget)
                group.setLayout(group_layout)
                self.crm_layout.addWidget(group)
        
        # Campaigns by status
        if campaigns:
            campaign_status = defaultdict(int)
            for campaign in campaigns:
                status = campaign.status or "unknown"
                campaign_status[status] += 1
            
            if campaign_status:
                widget = pg.GraphicsLayoutWidget()
                plot = widget.addPlot(title="Campaigns by Status")
                x = list(range(len(campaign_status)))
                y = list(campaign_status.values())
                bg = pg.BarGraphItem(x=x, height=y, width=0.6, brush='m')
                plot.addItem(bg)
                plot.setLabel('left', 'Count')
                plot.setLabel('bottom', 'Status')
                plot.getAxis('bottom').setTicks([[(i, status) for i, status in enumerate(campaign_status.keys())]])
                
                group = QGroupBox("Campaign Status")
                group_layout = QVBoxLayout()
                group_layout.addWidget(widget)
                group.setLayout(group_layout)
                self.crm_layout.addWidget(group)
        
        self.crm_layout.addStretch()

