"""
Project management service.
"""
from typing import List, Optional
from sqlalchemy.orm import Session
from datetime import datetime
from src.database.base import SessionLocal
from src.database.models.erp_models import Project, Task


class ProjectService:
    """Service for project management operations."""
    
    def __init__(self):
        self.db: Session = SessionLocal()
    
    def create_project(self, project_code: str, name: str, description: str = None,
                      start_date: datetime = None, end_date: datetime = None,
                      budget: float = 0.0) -> Project:
        """Create a new project."""
        project = Project(
            project_code=project_code,
            name=name,
            description=description,
            start_date=start_date,
            end_date=end_date,
            budget=budget
        )
        self.db.add(project)
        self.db.commit()
        self.db.refresh(project)
        return project
    
    def get_projects(self, status: Optional[str] = None) -> List[Project]:
        """Get all projects, optionally filtered by status."""
        query = self.db.query(Project)
        if status:
            query = query.filter(Project.status == status)
        return query.order_by(Project.created_at.desc()).all()
    
    def create_task(self, project_id: int, title: str, description: str = None,
                   assigned_to: Optional[int] = None, due_date: datetime = None,
                   priority: str = "medium") -> Task:
        """Create a new task."""
        task = Task(
            project_id=project_id,
            title=title,
            description=description,
            assigned_to=assigned_to,
            due_date=due_date,
            priority=priority
        )
        self.db.add(task)
        self.db.commit()
        self.db.refresh(task)
        return task
    
    def get_tasks(self, project_id: Optional[int] = None,
                 status: Optional[str] = None) -> List[Task]:
        """Get tasks, optionally filtered by project or status."""
        query = self.db.query(Task)
        if project_id:
            query = query.filter(Task.project_id == project_id)
        if status:
            query = query.filter(Task.status == status)
        return query.order_by(Task.created_at.desc()).all()
    
    def update_task_status(self, task_id: int, status: str) -> Optional[Task]:
        """Update task status."""
        task = self.db.query(Task).filter(Task.id == task_id).first()
        if task:
            task.status = status
            if status == "done":
                task.completed_at = datetime.utcnow()
            self.db.commit()
            self.db.refresh(task)
        return task
    
    def get_project(self, project_id: int) -> Optional[Project]:
        """Get a project by ID."""
        return self.db.query(Project).filter(Project.id == project_id).first()
    
    def update_project(self, project_id: int, **kwargs) -> Optional[Project]:
        """Update project fields."""
        project = self.get_project(project_id)
        if project:
            for key, value in kwargs.items():
                if hasattr(project, key):
                    setattr(project, key, value)
            self.db.commit()
            self.db.refresh(project)
        return project
    
    def delete_project(self, project_id: int) -> bool:
        """Delete a project."""
        project = self.get_project(project_id)
        if project:
            self.db.delete(project)
            self.db.commit()
            return True
        return False
    
    def get_task(self, task_id: int) -> Optional[Task]:
        """Get a task by ID."""
        return self.db.query(Task).filter(Task.id == task_id).first()
    
    def update_task(self, task_id: int, **kwargs) -> Optional[Task]:
        """Update task fields."""
        task = self.get_task(task_id)
        if task:
            for key, value in kwargs.items():
                if hasattr(task, key):
                    setattr(task, key, value)
            if 'status' in kwargs and kwargs['status'] == "done":
                task.completed_at = datetime.utcnow()
            self.db.commit()
            self.db.refresh(task)
        return task
    
    def delete_task(self, task_id: int) -> bool:
        """Delete a task."""
        task = self.get_task(task_id)
        if task:
            self.db.delete(task)
            self.db.commit()
            return True
        return False
    
    def close(self):
        """Close the database session."""
        self.db.close()

