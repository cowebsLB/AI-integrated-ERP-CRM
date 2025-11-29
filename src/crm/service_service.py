"""
Customer service/ticket management service.
"""
from typing import List, Optional
from sqlalchemy.orm import Session
from datetime import datetime
from src.database.base import SessionLocal
from src.database.models.crm_models import Ticket, TicketResponse, TicketStatus, TicketPriority


class ServiceService:
    """Service for customer service/ticket management."""
    
    def __init__(self):
        self.db: Session = SessionLocal()
    
    def create_ticket(self, ticket_number: str, contact_id: int, subject: str,
                     description: str, priority: TicketPriority = TicketPriority.MEDIUM,
                     category: str = None, assigned_to: Optional[int] = None) -> Ticket:
        """Create a new support ticket."""
        ticket = Ticket(
            ticket_number=ticket_number,
            contact_id=contact_id,
            subject=subject,
            description=description,
            priority=priority,
            category=category,
            assigned_to=assigned_to
        )
        self.db.add(ticket)
        self.db.commit()
        self.db.refresh(ticket)
        return ticket
    
    def get_tickets(self, status: Optional[TicketStatus] = None,
                   assigned_to: Optional[int] = None) -> List[Ticket]:
        """Get tickets, optionally filtered by status or assignee."""
        query = self.db.query(Ticket)
        if status:
            query = query.filter(Ticket.status == status)
        if assigned_to:
            query = query.filter(Ticket.assigned_to == assigned_to)
        return query.order_by(Ticket.created_at.desc()).all()
    
    def add_ticket_response(self, ticket_id: int, response_text: str,
                           is_internal: bool = False,
                           created_by: Optional[int] = None) -> TicketResponse:
        """Add a response/comment to a ticket."""
        response = TicketResponse(
            ticket_id=ticket_id,
            response_text=response_text,
            is_internal=is_internal,
            created_by=created_by
        )
        self.db.add(response)
        self.db.commit()
        self.db.refresh(response)
        return response
    
    def update_ticket_status(self, ticket_id: int, status: TicketStatus) -> Optional[Ticket]:
        """Update ticket status."""
        ticket = self.db.query(Ticket).filter(Ticket.id == ticket_id).first()
        if ticket:
            ticket.status = status
            if status == TicketStatus.RESOLVED:
                ticket.resolved_at = datetime.utcnow()
            self.db.commit()
            self.db.refresh(ticket)
        return ticket
    
    def get_ticket_responses(self, ticket_id: int) -> List[TicketResponse]:
        """Get all responses for a ticket."""
        return self.db.query(TicketResponse).filter(
            TicketResponse.ticket_id == ticket_id
        ).order_by(TicketResponse.created_at).all()
    
    def get_ticket(self, ticket_id: int) -> Optional[Ticket]:
        """Get a ticket by ID."""
        return self.db.query(Ticket).filter(Ticket.id == ticket_id).first()
    
    def update_ticket(self, ticket_id: int, **kwargs) -> Optional[Ticket]:
        """Update ticket fields."""
        ticket = self.get_ticket(ticket_id)
        if ticket:
            for key, value in kwargs.items():
                if hasattr(ticket, key):
                    setattr(ticket, key, value)
            if 'status' in kwargs and kwargs['status'] == TicketStatus.RESOLVED:
                ticket.resolved_at = datetime.utcnow()
            self.db.commit()
            self.db.refresh(ticket)
        return ticket
    
    def delete_ticket(self, ticket_id: int) -> bool:
        """Delete a ticket."""
        ticket = self.get_ticket(ticket_id)
        if ticket:
            self.db.delete(ticket)
            self.db.commit()
            return True
        return False
    
    def update_ticket_response(self, response_id: int, **kwargs) -> Optional[TicketResponse]:
        """Update a ticket response."""
        response = self.db.query(TicketResponse).filter(TicketResponse.id == response_id).first()
        if response:
            for key, value in kwargs.items():
                if hasattr(response, key):
                    setattr(response, key, value)
            self.db.commit()
            self.db.refresh(response)
        return response
    
    def delete_ticket_response(self, response_id: int) -> bool:
        """Delete a ticket response."""
        response = self.db.query(TicketResponse).filter(TicketResponse.id == response_id).first()
        if response:
            self.db.delete(response)
            self.db.commit()
            return True
        return False
    
    def close(self):
        """Close the database session."""
        self.db.close()

