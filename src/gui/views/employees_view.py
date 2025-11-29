"""
Employees view for HR module.
"""
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QTableWidget, QTableWidgetItem,
    QPushButton, QLabel
)
from PyQt6.QtCore import Qt
from src.erp.hr_service import HRService


class EmployeesView(QWidget):
    """View for managing employees."""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.hr_service = HRService()
        self.init_ui()
        self.load_employees()
    
    def init_ui(self):
        """Initialize the UI."""
        layout = QVBoxLayout()
        
        # Header
        header_layout = QHBoxLayout()
        title = QLabel("Employees")
        title.setStyleSheet("font-size: 18px; font-weight: bold;")
        header_layout.addWidget(title)
        header_layout.addStretch()
        
        self.add_button = QPushButton("Add Employee")
        self.add_button.clicked.connect(self.add_employee)
        header_layout.addWidget(self.add_button)
        
        self.edit_button = QPushButton("Edit")
        self.edit_button.clicked.connect(self.edit_employee)
        header_layout.addWidget(self.edit_button)
        
        self.delete_button = QPushButton("Delete")
        self.delete_button.clicked.connect(self.delete_employee)
        header_layout.addWidget(self.delete_button)
        
        self.refresh_button = QPushButton("Refresh")
        self.refresh_button.clicked.connect(self.load_employees)
        header_layout.addWidget(self.refresh_button)
        
        layout.addLayout(header_layout)
        
        # Table
        self.table = QTableWidget()
        self.table.setColumnCount(6)
        self.table.setHorizontalHeaderLabels([
            "ID", "Name", "Email", "Department", "Position", "Status"
        ])
        self.table.horizontalHeader().setStretchLastSection(True)
        self.table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        
        layout.addWidget(self.table)
        
        self.setLayout(layout)
    
    def load_employees(self):
        """Load employees into the table."""
        employees = self.hr_service.get_employees()
        self.table.setRowCount(len(employees))
        
        for row, emp in enumerate(employees):
            self.table.setItem(row, 0, QTableWidgetItem(emp.employee_id))
            self.table.setItem(row, 1, QTableWidgetItem(f"{emp.first_name} {emp.last_name}"))
            self.table.setItem(row, 2, QTableWidgetItem(emp.email or ""))
            self.table.setItem(row, 3, QTableWidgetItem(emp.department or ""))
            self.table.setItem(row, 4, QTableWidgetItem(emp.position or ""))
            status = "Active" if emp.is_active else "Inactive"
            self.table.setItem(row, 5, QTableWidgetItem(status))
        
        self.table.resizeColumnsToContents()
    
    def add_employee(self):
        """Open dialog to add a new employee."""
        from src.gui.dialogs.employee_dialog import EmployeeDialog
        dialog = EmployeeDialog(self)
        if dialog.exec():
            self.load_employees()
    
    def edit_employee(self):
        """Open dialog to edit selected employee."""
        selected_rows = self.table.selectionModel().selectedRows()
        if not selected_rows:
            from PyQt6.QtWidgets import QMessageBox
            QMessageBox.warning(self, "No Selection", "Please select an employee to edit.")
            return
        
        row = selected_rows[0].row()
        employee_id_text = self.table.item(row, 0).text()
        # Get employee by employee_id (not database id)
        employees = self.hr_service.get_employees()
        employee = next((e for e in employees if e.employee_id == employee_id_text), None)
        
        if employee:
            from src.gui.dialogs.employee_dialog import EmployeeDialog
            dialog = EmployeeDialog(self, employee_id=employee.id)
            if dialog.exec():
                self.load_employees()
    
    def delete_employee(self):
        """Delete selected employee."""
        selected_rows = self.table.selectionModel().selectedRows()
        if not selected_rows:
            from PyQt6.QtWidgets import QMessageBox
            QMessageBox.warning(self, "No Selection", "Please select an employee to delete.")
            return
        
        from PyQt6.QtWidgets import QMessageBox
        reply = QMessageBox.question(
            self, "Confirm Delete", 
            "Are you sure you want to delete this employee?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            row = selected_rows[0].row()
            employee_id_text = self.table.item(row, 0).text()
            employees = self.hr_service.get_employees()
            employee = next((e for e in employees if e.employee_id == employee_id_text), None)
            
            if employee:
                if self.hr_service.delete_employee(employee.id):
                    self.load_employees()
                else:
                    QMessageBox.warning(self, "Error", "Failed to delete employee.")

