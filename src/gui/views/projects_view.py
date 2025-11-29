"""
Projects view for Project Management module.
"""
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QTableWidget, QTableWidgetItem,
    QPushButton, QLabel, QComboBox
)
from PyQt6.QtCore import Qt
from src.erp.project_service import ProjectService


class ProjectsView(QWidget):
    """View for managing projects."""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.project_service = ProjectService()
        self.init_ui()
        self.load_projects()
    
    def init_ui(self):
        """Initialize the UI."""
        layout = QVBoxLayout()
        
        # Header
        header_layout = QHBoxLayout()
        title = QLabel("Projects")
        title.setStyleSheet("font-size: 18px; font-weight: bold;")
        header_layout.addWidget(title)
        header_layout.addStretch()
        
        self.add_button = QPushButton("New Project")
        self.add_button.clicked.connect(self.add_project)
        header_layout.addWidget(self.add_button)
        
        self.edit_button = QPushButton("Edit")
        self.edit_button.clicked.connect(self.edit_project)
        header_layout.addWidget(self.edit_button)
        
        self.delete_button = QPushButton("Delete")
        self.delete_button.clicked.connect(self.delete_project)
        header_layout.addWidget(self.delete_button)
        
        self.refresh_button = QPushButton("Refresh")
        self.refresh_button.clicked.connect(self.load_projects)
        header_layout.addWidget(self.refresh_button)
        
        layout.addLayout(header_layout)
        
        # Table
        self.table = QTableWidget()
        self.table.setColumnCount(6)
        self.table.setHorizontalHeaderLabels([
            "Code", "Name", "Status", "Start Date", "End Date", "Budget"
        ])
        self.table.horizontalHeader().setStretchLastSection(True)
        self.table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        
        layout.addWidget(self.table)
        
        self.setLayout(layout)
    
    def load_projects(self):
        """Load projects into the table."""
        projects = self.project_service.get_projects()
        self.table.setRowCount(len(projects))
        
        for row, project in enumerate(projects):
            self.table.setItem(row, 0, QTableWidgetItem(project.project_code))
            self.table.setItem(row, 1, QTableWidgetItem(project.name))
            self.table.setItem(row, 2, QTableWidgetItem(project.status))
            start_date = project.start_date.strftime("%Y-%m-%d") if project.start_date else ""
            self.table.setItem(row, 3, QTableWidgetItem(start_date))
            end_date = project.end_date.strftime("%Y-%m-%d") if project.end_date else ""
            self.table.setItem(row, 4, QTableWidgetItem(end_date))
            self.table.setItem(row, 5, QTableWidgetItem(f"${project.budget:.2f}"))
        
        self.table.resizeColumnsToContents()
    
    def add_project(self):
        """Open dialog to add a new project."""
        from src.gui.dialogs.project_dialog import ProjectDialog
        dialog = ProjectDialog(self)
        if dialog.exec():
            self.load_projects()
    
    def edit_project(self):
        """Open dialog to edit selected project."""
        selected_rows = self.table.selectionModel().selectedRows()
        if not selected_rows:
            from PyQt6.QtWidgets import QMessageBox
            QMessageBox.warning(self, "No Selection", "Please select a project to edit.")
            return
        
        row = selected_rows[0].row()
        project_code = self.table.item(row, 0).text()
        projects = self.project_service.get_projects()
        project = next((p for p in projects if p.project_code == project_code), None)
        
        if project:
            from src.gui.dialogs.project_dialog import ProjectDialog
            dialog = ProjectDialog(self, project_id=project.id)
            if dialog.exec():
                self.load_projects()
    
    def delete_project(self):
        """Delete selected project."""
        selected_rows = self.table.selectionModel().selectedRows()
        if not selected_rows:
            from PyQt6.QtWidgets import QMessageBox
            QMessageBox.warning(self, "No Selection", "Please select a project to delete.")
            return
        
        from PyQt6.QtWidgets import QMessageBox
        reply = QMessageBox.question(
            self, "Confirm Delete", 
            "Are you sure you want to delete this project?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            row = selected_rows[0].row()
            project_code = self.table.item(row, 0).text()
            projects = self.project_service.get_projects()
            project = next((p for p in projects if p.project_code == project_code), None)
            
            if project:
                if self.project_service.delete_project(project.id):
                    self.load_projects()
                else:
                    QMessageBox.warning(self, "Error", "Failed to delete project.")

