"""
Human Resources service.
"""
from typing import List, Optional
from sqlalchemy.orm import Session
from datetime import datetime
from src.database.base import SessionLocal
from src.database.models.erp_models import Employee, Attendance


class HRService:
    """Service for HR management operations."""
    
    def __init__(self):
        self.db: Session = SessionLocal()
    
    def create_employee(self, employee_id: str, first_name: str, last_name: str,
                       email: str = None, phone: str = None, department: str = None,
                       position: str = None, hire_date: datetime = None,
                       salary: float = None) -> Employee:
        """Create a new employee."""
        employee = Employee(
            employee_id=employee_id,
            first_name=first_name,
            last_name=last_name,
            email=email,
            phone=phone,
            department=department,
            position=position,
            hire_date=hire_date,
            salary=salary
        )
        self.db.add(employee)
        self.db.commit()
        self.db.refresh(employee)
        return employee
    
    def get_employees(self, department: Optional[str] = None) -> List[Employee]:
        """Get all employees, optionally filtered by department."""
        query = self.db.query(Employee).filter(Employee.is_active == True)
        if department:
            query = query.filter(Employee.department == department)
        return query.order_by(Employee.last_name).all()
    
    def get_employee(self, employee_id: int) -> Optional[Employee]:
        """Get an employee by ID."""
        return self.db.query(Employee).filter(Employee.id == employee_id).first()
    
    def record_attendance(self, employee_id: int, date: datetime,
                         check_in: datetime = None, check_out: datetime = None,
                         status: str = "present") -> Attendance:
        """Record attendance for an employee."""
        attendance = Attendance(
            employee_id=employee_id,
            date=date,
            check_in=check_in,
            check_out=check_out,
            status=status
        )
        
        # Calculate hours worked if both check-in and check-out are provided
        if check_in and check_out:
            delta = check_out - check_in
            attendance.hours_worked = delta.total_seconds() / 3600
        
        self.db.add(attendance)
        self.db.commit()
        self.db.refresh(attendance)
        return attendance
    
    def get_attendance(self, employee_id: Optional[int] = None,
                      start_date: Optional[datetime] = None,
                      end_date: Optional[datetime] = None) -> List[Attendance]:
        """Get attendance records."""
        query = self.db.query(Attendance)
        
        if employee_id:
            query = query.filter(Attendance.employee_id == employee_id)
        if start_date:
            query = query.filter(Attendance.date >= start_date)
        if end_date:
            query = query.filter(Attendance.date <= end_date)
        
        return query.order_by(Attendance.date.desc()).all()
    
    def update_employee(self, employee_id: int, **kwargs) -> Optional[Employee]:
        """Update employee fields."""
        employee = self.get_employee(employee_id)
        if employee:
            for key, value in kwargs.items():
                if hasattr(employee, key):
                    setattr(employee, key, value)
            self.db.commit()
            self.db.refresh(employee)
        return employee
    
    def delete_employee(self, employee_id: int) -> bool:
        """Soft delete an employee (deactivate)."""
        employee = self.get_employee(employee_id)
        if employee:
            employee.is_active = False
            self.db.commit()
            return True
        return False
    
    def update_attendance(self, attendance_id: int, **kwargs) -> Optional[Attendance]:
        """Update attendance record."""
        attendance = self.db.query(Attendance).filter(Attendance.id == attendance_id).first()
        if attendance:
            for key, value in kwargs.items():
                if hasattr(attendance, key):
                    setattr(attendance, key, value)
            # Recalculate hours if check-in/out changed
            if 'check_in' in kwargs or 'check_out' in kwargs:
                if attendance.check_in and attendance.check_out:
                    delta = attendance.check_out - attendance.check_in
                    attendance.hours_worked = delta.total_seconds() / 3600
            self.db.commit()
            self.db.refresh(attendance)
        return attendance
    
    def delete_attendance(self, attendance_id: int) -> bool:
        """Delete an attendance record."""
        attendance = self.db.query(Attendance).filter(Attendance.id == attendance_id).first()
        if attendance:
            self.db.delete(attendance)
            self.db.commit()
            return True
        return False
    
    def close(self):
        """Close the database session."""
        self.db.close()

