"""
Project dialog for adding/editing projects.
"""
from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QFormLayout,
    QLineEdit, QPushButton, QDoubleSpinBox, QDateEdit, QTextEdit, QMessageBox
)
from PyQt6.QtCore import Qt, QDate
from datetime import datetime
from src.erp.project_service import ProjectService


class ProjectDialog(QDialog):
    """Dialog for adding or editing a project."""
    
    def __init__(self, parent=None, project_id=None):
        super().__init__(parent)
        self.project_service = ProjectService()
        self.project_id = project_id
        self.init_ui()
        
        if project_id:
            self.load_project()
    
    def init_ui(self):
        """Initialize the UI."""
        self.setWindowTitle("Add Project" if not self.project_id else "Edit Project")
        self.setMinimumWidth(400)
        
        layout = QVBoxLayout()
        
        # Form
        form = QFormLayout()
        
        self.project_code_input = QLineEdit()
        form.addRow("Project Code:", self.project_code_input)
        
        self.name_input = QLineEdit()
        form.addRow("Name:", self.name_input)
        
        self.description_input = QTextEdit()
        self.description_input.setMaximumHeight(100)
        form.addRow("Description:", self.description_input)
        
        self.start_date_input = QDateEdit()
        self.start_date_input.setCalendarPopup(True)
        self.start_date_input.setDate(QDate.currentDate())
        form.addRow("Start Date:", self.start_date_input)
        
        self.end_date_input = QDateEdit()
        self.end_date_input.setCalendarPopup(True)
        self.end_date_input.setDate(QDate.currentDate())
        form.addRow("End Date:", self.end_date_input)
        
        self.budget_input = QDoubleSpinBox()
        self.budget_input.setMaximum(99999999.99)
        self.budget_input.setDecimals(2)
        form.addRow("Budget:", self.budget_input)
        
        layout.addLayout(form)
        
        # Buttons
        button_layout = QHBoxLayout()
        button_layout.addStretch()
        
        self.save_button = QPushButton("Save")
        self.save_button.clicked.connect(self.save_project)
        button_layout.addWidget(self.save_button)
        
        self.cancel_button = QPushButton("Cancel")
        self.cancel_button.clicked.connect(self.reject)
        button_layout.addWidget(self.cancel_button)
        
        layout.addLayout(button_layout)
        
        self.setLayout(layout)
    
    def load_project(self):
        """Load project data into the form."""
        project = self.project_service.get_project(self.project_id)
        if project:
            self.project_code_input.setText(project.project_code)
            self.name_input.setText(project.name)
            self.description_input.setPlainText(project.description or "")
            if project.start_date:
                self.start_date_input.setDate(QDate.fromString(
                    project.start_date.strftime("%Y-%m-%d"), "yyyy-MM-dd"
                ))
            if project.end_date:
                self.end_date_input.setDate(QDate.fromString(
                    project.end_date.strftime("%Y-%m-%d"), "yyyy-MM-dd"
                ))
            self.budget_input.setValue(project.budget)
    
    def save_project(self):
        """Save the project."""
        project_code = self.project_code_input.text().strip()
        name = self.name_input.text().strip()
        
        if not project_code or not name:
            QMessageBox.warning(self, "Validation Error", 
                              "Project Code and Name are required.")
            return
        
        try:
            start_date = self.start_date_input.date().toPyDate()
            start_datetime = datetime.combine(start_date, datetime.min.time())
            
            end_date = self.end_date_input.date().toPyDate()
            end_datetime = datetime.combine(end_date, datetime.min.time())
            
            if self.project_id:
                # Update existing project
                self.project_service.update_project(
                    self.project_id,
                    project_code=project_code,
                    name=name,
                    description=self.description_input.toPlainText().strip() or None,
                    start_date=start_datetime,
                    end_date=end_datetime,
                    budget=self.budget_input.value()
                )
            else:
                # Create new project
                self.project_service.create_project(
                    project_code=project_code,
                    name=name,
                    description=self.description_input.toPlainText().strip() or None,
                    start_date=start_datetime,
                    end_date=end_datetime,
                    budget=self.budget_input.value()
                )
            
            self.accept()
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to save project: {str(e)}")

