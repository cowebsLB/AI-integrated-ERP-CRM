"""
Contact management service.
"""
from typing import List, Optional
from sqlalchemy.orm import Session
from src.database.base import SessionLocal
from src.database.models.crm_models import Contact, Communication


class ContactService:
    """Service for contact management operations."""
    
    def __init__(self):
        self.db: Session = SessionLocal()
    
    def create_contact(self, first_name: str, last_name: str, email: str = None,
                      phone: str = None, company: str = None,
                      contact_type: str = "customer") -> Contact:
        """Create a new contact."""
        contact = Contact(
            first_name=first_name,
            last_name=last_name,
            email=email,
            phone=phone,
            company=company,
            contact_type=contact_type
        )
        self.db.add(contact)
        self.db.commit()
        self.db.refresh(contact)
        return contact
    
    def get_contacts(self, contact_type: Optional[str] = None) -> List[Contact]:
        """Get all contacts, optionally filtered by type."""
        query = self.db.query(Contact)
        if contact_type:
            query = query.filter(Contact.contact_type == contact_type)
        return query.order_by(Contact.created_at.desc()).all()
    
    def search_contacts(self, search_term: str) -> List[Contact]:
        """Search contacts by name, email, or company."""
        search = f"%{search_term}%"
        return self.db.query(Contact).filter(
            (Contact.first_name.like(search)) |
            (Contact.last_name.like(search)) |
            (Contact.email.like(search)) |
            (Contact.company.like(search))
        ).all()
    
    def get_contact(self, contact_id: int) -> Optional[Contact]:
        """Get a contact by ID."""
        return self.db.query(Contact).filter(Contact.id == contact_id).first()
    
    def update_contact(self, contact_id: int, **kwargs) -> Optional[Contact]:
        """Update contact fields."""
        contact = self.get_contact(contact_id)
        if contact:
            for key, value in kwargs.items():
                if hasattr(contact, key):
                    setattr(contact, key, value)
            self.db.commit()
            self.db.refresh(contact)
        return contact
    
    def add_communication(self, contact_id: int, communication_type: str,
                         subject: str = None, content: str = None,
                         direction: str = "outbound") -> Communication:
        """Add a communication log."""
        communication = Communication(
            contact_id=contact_id,
            communication_type=communication_type,
            subject=subject,
            content=content,
            direction=direction
        )
        self.db.add(communication)
        self.db.commit()
        self.db.refresh(communication)
        return communication
    
    def get_communications(self, contact_id: int) -> List[Communication]:
        """Get all communications for a contact."""
        return self.db.query(Communication).filter(
            Communication.contact_id == contact_id
        ).order_by(Communication.date_time.desc()).all()
    
    def delete_contact(self, contact_id: int) -> bool:
        """Soft delete a contact (deactivate)."""
        contact = self.get_contact(contact_id)
        if contact:
            contact.is_active = False
            self.db.commit()
            return True
        return False
    
    def close(self):
        """Close the database session."""
        self.db.close()

