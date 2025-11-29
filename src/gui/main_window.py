"""
Main application window.
"""
from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QMenuBar, QStatusBar, QToolBar, QLabel, QPushButton, QStackedWidget
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QAction
import config

class MainWindow(QMainWindow):
    """Main application window."""
    
    def __init__(self):
        super().__init__()
        self.sync_manager = None
        self.stacked_widget = None
        self.update_service = None
        self.init_ui()
        self.init_update_service()
    
    def set_sync_manager(self, sync_manager):
        """Set the sync manager instance."""
        self.sync_manager = sync_manager
        if sync_manager:
            sync_manager.sync_status_changed.connect(self.on_sync_status_changed)
    
    def on_sync_status_changed(self, status: dict):
        """Handle sync status updates."""
        if status.get("enabled"):
            pending = status.get("pending", 0)
            if pending > 0:
                self.statusBar().showMessage(f"Sync: {pending} pending changes", 5000)
            else:
                self.statusBar().showMessage("All changes synced", 3000)
        
    def init_ui(self):
        """Initialize the user interface."""
        self.setWindowTitle(f"{config.APP_NAME} v{config.APP_VERSION}")
        self.setGeometry(100, 100, config.WINDOW_WIDTH, config.WINDOW_HEIGHT)
        
        # Create stacked widget for views
        self.stacked_widget = QStackedWidget()
        self.setCentralWidget(self.stacked_widget)
        
        # Create welcome/dashboard view
        welcome_widget = QWidget()
        welcome_layout = QVBoxLayout()
        welcome_label = QLabel("Welcome to AI-Integrated ERP-CRM")
        welcome_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        welcome_label.setStyleSheet("font-size: 24px; font-weight: bold; padding: 20px;")
        welcome_layout.addWidget(welcome_label)
        
        placeholder = QLabel("Select a module from the menu to get started")
        placeholder.setAlignment(Qt.AlignmentFlag.AlignCenter)
        welcome_layout.addWidget(placeholder)
        welcome_widget.setLayout(welcome_layout)
        
        self.stacked_widget.addWidget(welcome_widget)
        
        # Create menu bar
        self.create_menu_bar()
        
        # Create toolbar
        self.create_toolbar()
        
        # Create status bar
        self.statusBar().showMessage("Ready")
        
        # Check for updates on startup if enabled
        if config.CHECK_UPDATES_ON_STARTUP:
            # Delay update check slightly to not block startup
            from PyQt6.QtCore import QTimer
            QTimer.singleShot(2000, self.check_for_updates_silent)
        
    def create_menu_bar(self):
        """Create the application menu bar."""
        menubar = self.menuBar()
        
        # File menu
        file_menu = menubar.addMenu("File")
        
        exit_action = QAction("Exit", self)
        exit_action.setShortcut("Ctrl+Q")
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)
        
        # ERP menu
        erp_menu = menubar.addMenu("ERP")
        
        invoices_action = QAction("Invoices", self)
        invoices_action.triggered.connect(lambda: self.show_view("invoices"))
        erp_menu.addAction(invoices_action)
        
        products_action = QAction("Products", self)
        products_action.triggered.connect(lambda: self.show_view("products"))
        erp_menu.addAction(products_action)
        
        employees_action = QAction("Employees", self)
        employees_action.triggered.connect(lambda: self.show_view("employees"))
        erp_menu.addAction(employees_action)
        
        projects_action = QAction("Projects", self)
        projects_action.triggered.connect(lambda: self.show_view("projects"))
        erp_menu.addAction(projects_action)
        
        # CRM menu
        crm_menu = menubar.addMenu("CRM")
        contacts_action = QAction("Contacts", self)
        contacts_action.triggered.connect(lambda: self.show_view("contacts"))
        crm_menu.addAction(contacts_action)
        
        sales_action = QAction("Sales", self)
        sales_action.triggered.connect(lambda: self.show_view("sales"))
        crm_menu.addAction(sales_action)
        
        campaigns_action = QAction("Campaigns", self)
        campaigns_action.triggered.connect(lambda: self.show_view("campaigns"))
        crm_menu.addAction(campaigns_action)
        
        tickets_action = QAction("Support Tickets", self)
        tickets_action.triggered.connect(lambda: self.show_view("tickets"))
        crm_menu.addAction(tickets_action)
        
        # AI menu
        ai_menu = menubar.addMenu("AI Assistant")
        chat_action = QAction("Open Chat", self)
        chat_action.triggered.connect(lambda: self.show_view("ai_chat"))
        ai_menu.addAction(chat_action)
        
        insights_action = QAction("AI Insights", self)
        insights_action.triggered.connect(lambda: self.show_view("ai_insights"))
        ai_menu.addAction(insights_action)
        
        # Sync menu
        sync_menu = menubar.addMenu("Sync")
        sync_now_action = QAction("Sync Now", self)
        sync_now_action.triggered.connect(self.sync_now)
        sync_menu.addAction(sync_now_action)
        sync_menu.addSeparator()
        sync_status_action = QAction("Sync Status", self)
        sync_status_action.triggered.connect(self.show_sync_status)
        sync_menu.addAction(sync_status_action)
        
        # Help menu
        help_menu = menubar.addMenu("Help")
        check_updates_action = QAction("Check for Updates", self)
        check_updates_action.triggered.connect(self.check_for_updates)
        help_menu.addAction(check_updates_action)
        help_menu.addSeparator()
        about_action = QAction("About", self)
        about_action.triggered.connect(self.show_about)
        help_menu.addAction(about_action)
    
    def sync_now(self):
        """Trigger immediate sync."""
        if self.sync_manager:
            self.sync_manager.sync_now()
            self.statusBar().showMessage("Sync started...", 2000)
    
    def show_sync_status(self):
        """Show sync status dialog."""
        if self.sync_manager:
            status = self.sync_manager.get_status()
            from PyQt6.QtWidgets import QMessageBox
            msg = QMessageBox(self)
            msg.setWindowTitle("Sync Status")
            if status.get("enabled"):
                msg.setText(f"""
                Sync Status:
                Pending: {status.get('pending', 0)}
                Syncing: {status.get('syncing', 0)}
                Failed: {status.get('failed', 0)}
                Synced: {status.get('synced', 0)}
                """)
            else:
                msg.setText("Sync is disabled. Configure Supabase in .env file to enable.")
            msg.exec()
    
    def show_view(self, view_name: str):
        """Show a specific view."""
        # Check if view already exists
        for i in range(self.stacked_widget.count()):
            widget = self.stacked_widget.widget(i)
            if hasattr(widget, 'view_name') and widget.view_name == view_name:
                self.stacked_widget.setCurrentIndex(i)
                return
        
        # Create new view
        view = None
        if view_name == "contacts":
            from src.gui.views.contacts_view import ContactsView
            view = ContactsView()
            view.view_name = "contacts"
        elif view_name == "invoices":
            from src.gui.views.invoices_view import InvoicesView
            view = InvoicesView()
            view.view_name = "invoices"
        elif view_name == "products":
            from src.gui.views.products_view import ProductsView
            view = ProductsView()
            view.view_name = "products"
        elif view_name == "sales":
            from src.gui.views.opportunities_view import OpportunitiesView
            view = OpportunitiesView()
            view.view_name = "sales"
        elif view_name == "dashboard":
            from src.gui.views.dashboard_view import DashboardView
            view = DashboardView()
            view.view_name = "dashboard"
        elif view_name == "employees":
            from src.gui.views.employees_view import EmployeesView
            view = EmployeesView()
            view.view_name = "employees"
        elif view_name == "projects":
            from src.gui.views.projects_view import ProjectsView
            view = ProjectsView()
            view.view_name = "projects"
        elif view_name == "campaigns":
            from src.gui.views.campaigns_view import CampaignsView
            view = CampaignsView()
            view.view_name = "campaigns"
        elif view_name == "tickets":
            from src.gui.views.tickets_view import TicketsView
            view = TicketsView()
            view.view_name = "tickets"
        elif view_name == "ai_chat":
            from src.gui.views.ai_chat_view import AIChatView
            view = AIChatView()
            view.view_name = "ai_chat"
        elif view_name == "ai_insights":
            from src.gui.views.ai_insights_view import AIInsightsView
            view = AIInsightsView()
            view.view_name = "ai_insights"
        
        if view:
            self.stacked_widget.addWidget(view)
            self.stacked_widget.setCurrentWidget(view)
        
    def create_toolbar(self):
        """Create the application toolbar."""
        toolbar = QToolBar()
        toolbar.setToolButtonStyle(Qt.ToolButtonStyle.ToolButtonTextUnderIcon)
        self.addToolBar(toolbar)
        
        # Dashboard
        dashboard_action = QAction("Dashboard", self)
        dashboard_action.triggered.connect(lambda: self.show_view("dashboard"))
        toolbar.addAction(dashboard_action)
        
        toolbar.addSeparator()
        
        # ERP Modules
        invoices_action = QAction("Invoices", self)
        invoices_action.triggered.connect(lambda: self.show_view("invoices"))
        toolbar.addAction(invoices_action)
        
        products_action = QAction("Products", self)
        products_action.triggered.connect(lambda: self.show_view("products"))
        toolbar.addAction(products_action)
        
        employees_action = QAction("Employees", self)
        employees_action.triggered.connect(lambda: self.show_view("employees"))
        toolbar.addAction(employees_action)
        
        projects_action = QAction("Projects", self)
        projects_action.triggered.connect(lambda: self.show_view("projects"))
        toolbar.addAction(projects_action)
        
        toolbar.addSeparator()
        
        # CRM Modules
        contacts_action = QAction("Contacts", self)
        contacts_action.triggered.connect(lambda: self.show_view("contacts"))
        toolbar.addAction(contacts_action)
        
        sales_action = QAction("Sales", self)
        sales_action.triggered.connect(lambda: self.show_view("sales"))
        toolbar.addAction(sales_action)
        
        campaigns_action = QAction("Campaigns", self)
        campaigns_action.triggered.connect(lambda: self.show_view("campaigns"))
        toolbar.addAction(campaigns_action)
        
        tickets_action = QAction("Tickets", self)
        tickets_action.triggered.connect(lambda: self.show_view("tickets"))
        toolbar.addAction(tickets_action)
        
        toolbar.addSeparator()
        
        # AI Assistant
        ai_chat_action = QAction("AI Chat", self)
        ai_chat_action.triggered.connect(lambda: self.show_view("ai_chat"))
        toolbar.addAction(ai_chat_action)
        
        ai_insights_action = QAction("AI Insights", self)
        ai_insights_action.triggered.connect(lambda: self.show_view("ai_insights"))
        toolbar.addAction(ai_insights_action)
    
    def init_update_service(self):
        """Initialize the update service."""
        from src.services.update_service import UpdateService
        self.update_service = UpdateService()
    
    def check_for_updates(self, silent=False):
        """Check for updates manually."""
        if not self.update_service:
            self.init_update_service()
        
        if not self.update_service.repo_owner or not self.update_service.repo_name:
            if not silent:
                from PyQt6.QtWidgets import QMessageBox
                QMessageBox.information(
                    self,
                    "Update Check",
                    "GitHub repository not configured.\n\n"
                    "Please set GITHUB_REPO_OWNER and GITHUB_REPO_NAME in your .env file or config.py"
                )
            return
        
        # Show checking message
        if not silent:
            self.statusBar().showMessage("Checking for updates...", 3000)
        
        # Check for updates asynchronously
        self.update_service.check_for_updates_async(
            on_update_available=self.on_update_available,
            on_check_complete=self.on_update_check_complete,
            on_error=self.on_update_check_error
        )
    
    def check_for_updates_silent(self):
        """Check for updates silently (on startup)."""
        self.check_for_updates(silent=True)
    
    def on_update_available(self, update_info: dict):
        """Handle when an update is available."""
        from src.gui.dialogs.update_dialog import UpdateDialog
        dialog = UpdateDialog(update_info, self)
        dialog.exec()
    
    def on_update_check_complete(self, update_available: bool):
        """Handle update check completion."""
        if not update_available:
            # Only show message if manually checking
            self.statusBar().showMessage("You are using the latest version.", 3000)
    
    def on_update_check_error(self, error_message: str):
        """Handle update check error."""
        from PyQt6.QtWidgets import QMessageBox
        QMessageBox.warning(
            self,
            "Update Check Failed",
            f"Failed to check for updates:\n{error_message}"
        )
        self.statusBar().showMessage("Update check failed", 3000)
    
    def show_about(self):
        """Show about dialog."""
        from PyQt6.QtWidgets import QMessageBox
        msg = QMessageBox(self)
        msg.setWindowTitle("About")
        msg.setText(f"""
        <h2>{config.APP_NAME}</h2>
        <p>Version: {config.APP_VERSION}</p>
        <p>A comprehensive Enterprise Resource Planning (ERP) and Customer Relationship Management (CRM) system enhanced with AI capabilities.</p>
        <p>&copy; 2025</p>
        """)
        msg.exec()

