"""
Employee dialog for adding/editing employees.
"""
from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QFormLayout,
    QLineEdit, QPushButton, QDoubleSpinBox, QDateEdit, QMessageBox
)
from PyQt6.QtCore import Qt, QDate
from datetime import datetime
from src.erp.hr_service import HRService


class EmployeeDialog(QDialog):
    """Dialog for adding or editing an employee."""
    
    def __init__(self, parent=None, employee_id=None):
        super().__init__(parent)
        self.hr_service = HRService()
        self.employee_id = employee_id
        self.init_ui()
        
        if employee_id:
            self.load_employee()
    
    def init_ui(self):
        """Initialize the UI."""
        self.setWindowTitle("Add Employee" if not self.employee_id else "Edit Employee")
        self.setMinimumWidth(400)
        
        layout = QVBoxLayout()
        
        # Form
        form = QFormLayout()
        
        self.employee_id_input = QLineEdit()
        form.addRow("Employee ID:", self.employee_id_input)
        
        self.first_name_input = QLineEdit()
        form.addRow("First Name:", self.first_name_input)
        
        self.last_name_input = QLineEdit()
        form.addRow("Last Name:", self.last_name_input)
        
        self.email_input = QLineEdit()
        form.addRow("Email:", self.email_input)
        
        self.phone_input = QLineEdit()
        form.addRow("Phone:", self.phone_input)
        
        self.department_input = QLineEdit()
        form.addRow("Department:", self.department_input)
        
        self.position_input = QLineEdit()
        form.addRow("Position:", self.position_input)
        
        self.hire_date_input = QDateEdit()
        self.hire_date_input.setCalendarPopup(True)
        self.hire_date_input.setDate(QDate.currentDate())
        form.addRow("Hire Date:", self.hire_date_input)
        
        self.salary_input = QDoubleSpinBox()
        self.salary_input.setMaximum(9999999.99)
        self.salary_input.setDecimals(2)
        form.addRow("Salary:", self.salary_input)
        
        layout.addLayout(form)
        
        # Buttons
        button_layout = QHBoxLayout()
        button_layout.addStretch()
        
        self.save_button = QPushButton("Save")
        self.save_button.clicked.connect(self.save_employee)
        button_layout.addWidget(self.save_button)
        
        self.cancel_button = QPushButton("Cancel")
        self.cancel_button.clicked.connect(self.reject)
        button_layout.addWidget(self.cancel_button)
        
        layout.addLayout(button_layout)
        
        self.setLayout(layout)
    
    def load_employee(self):
        """Load employee data into the form."""
        employee = self.hr_service.get_employee(self.employee_id)
        if employee:
            self.employee_id_input.setText(employee.employee_id)
            self.first_name_input.setText(employee.first_name)
            self.last_name_input.setText(employee.last_name)
            self.email_input.setText(employee.email or "")
            self.phone_input.setText(employee.phone or "")
            self.department_input.setText(employee.department or "")
            self.position_input.setText(employee.position or "")
            if employee.hire_date:
                self.hire_date_input.setDate(QDate.fromString(
                    employee.hire_date.strftime("%Y-%m-%d"), "yyyy-MM-dd"
                ))
            if employee.salary:
                self.salary_input.setValue(employee.salary)
    
    def save_employee(self):
        """Save the employee."""
        employee_id = self.employee_id_input.text().strip()
        first_name = self.first_name_input.text().strip()
        last_name = self.last_name_input.text().strip()
        
        if not employee_id or not first_name or not last_name:
            QMessageBox.warning(self, "Validation Error", 
                              "Employee ID, First Name, and Last Name are required.")
            return
        
        try:
            hire_date = self.hire_date_input.date().toPyDate()
            hire_datetime = datetime.combine(hire_date, datetime.min.time())
            
            if self.employee_id:
                # Update existing employee
                self.hr_service.update_employee(
                    self.employee_id,
                    employee_id=employee_id,
                    first_name=first_name,
                    last_name=last_name,
                    email=self.email_input.text().strip() or None,
                    phone=self.phone_input.text().strip() or None,
                    department=self.department_input.text().strip() or None,
                    position=self.position_input.text().strip() or None,
                    hire_date=hire_datetime,
                    salary=self.salary_input.value() if self.salary_input.value() > 0 else None
                )
            else:
                # Create new employee
                self.hr_service.create_employee(
                    employee_id=employee_id,
                    first_name=first_name,
                    last_name=last_name,
                    email=self.email_input.text().strip() or None,
                    phone=self.phone_input.text().strip() or None,
                    department=self.department_input.text().strip() or None,
                    position=self.position_input.text().strip() or None,
                    hire_date=hire_datetime,
                    salary=self.salary_input.value() if self.salary_input.value() > 0 else None
                )
            
            self.accept()
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to save employee: {str(e)}")

