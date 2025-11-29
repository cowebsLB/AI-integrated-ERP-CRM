"""
Sales management service.
"""
from typing import List, Optional
from sqlalchemy.orm import Session
from datetime import datetime
from src.database.base import SessionLocal
from src.database.models.crm_models import Lead, Opportunity, Quote, QuoteItem, LeadStatus, OpportunityStage


class SalesService:
    """Service for sales management operations."""
    
    def __init__(self):
        self.db: Session = SessionLocal()
    
    def create_lead(self, contact_id: int, source: str = None,
                   estimated_value: float = 0.0) -> Lead:
        """Create a new lead."""
        lead = Lead(
            contact_id=contact_id,
            source=source,
            estimated_value=estimated_value
        )
        self.db.add(lead)
        self.db.commit()
        self.db.refresh(lead)
        return lead
    
    def get_leads(self, status: Optional[LeadStatus] = None) -> List[Lead]:
        """Get all leads, optionally filtered by status."""
        query = self.db.query(Lead)
        if status:
            query = query.filter(Lead.status == status)
        return query.order_by(Lead.created_at.desc()).all()
    
    def update_lead_status(self, lead_id: int, status: LeadStatus) -> Optional[Lead]:
        """Update lead status."""
        lead = self.db.query(Lead).filter(Lead.id == lead_id).first()
        if lead:
            lead.status = status
            self.db.commit()
            self.db.refresh(lead)
        return lead
    
    def create_opportunity(self, contact_id: int, name: str, value: float,
                          expected_close_date: datetime = None) -> Opportunity:
        """Create a new opportunity."""
        opportunity = Opportunity(
            contact_id=contact_id,
            name=name,
            value=value,
            expected_close_date=expected_close_date
        )
        self.db.add(opportunity)
        self.db.commit()
        self.db.refresh(opportunity)
        return opportunity
    
    def get_opportunities(self, stage: Optional[OpportunityStage] = None) -> List[Opportunity]:
        """Get all opportunities, optionally filtered by stage."""
        query = self.db.query(Opportunity)
        if stage:
            query = query.filter(Opportunity.stage == stage)
        return query.order_by(Opportunity.created_at.desc()).all()
    
    def update_opportunity_stage(self, opportunity_id: int, stage: OpportunityStage,
                                probability: int = None) -> Optional[Opportunity]:
        """Update opportunity stage and probability."""
        opportunity = self.db.query(Opportunity).filter(Opportunity.id == opportunity_id).first()
        if opportunity:
            opportunity.stage = stage
            if probability is not None:
                opportunity.probability = probability
            self.db.commit()
            self.db.refresh(opportunity)
        return opportunity
    
    def create_quote(self, quote_number: str, contact_id: int,
                    items: List[dict], expiry_date: datetime = None,
                    opportunity_id: Optional[int] = None) -> Quote:
        """Create a new quote."""
        quote = Quote(
            quote_number=quote_number,
            contact_id=contact_id,
            opportunity_id=opportunity_id,
            expiry_date=expiry_date
        )
        self.db.add(quote)
        self.db.flush()
        
        subtotal = 0.0
        for item_data in items:
            item = QuoteItem(
                quote_id=quote.id,
                description=item_data['description'],
                quantity=item_data.get('quantity', 1.0),
                unit_price=item_data['unit_price'],
                total=item_data.get('quantity', 1.0) * item_data['unit_price']
            )
            subtotal += item.total
            self.db.add(item)
        
        quote.subtotal = subtotal
        quote.tax = subtotal * 0.1  # 10% tax
        quote.total = quote.subtotal + quote.tax
        
        self.db.commit()
        self.db.refresh(quote)
        return quote
    
    def get_quotes(self, contact_id: Optional[int] = None) -> List[Quote]:
        """Get all quotes, optionally filtered by contact."""
        query = self.db.query(Quote)
        if contact_id:
            query = query.filter(Quote.contact_id == contact_id)
        return query.order_by(Quote.created_at.desc()).all()
    
    def get_lead(self, lead_id: int) -> Optional[Lead]:
        """Get a lead by ID."""
        return self.db.query(Lead).filter(Lead.id == lead_id).first()
    
    def update_lead(self, lead_id: int, **kwargs) -> Optional[Lead]:
        """Update lead fields."""
        lead = self.get_lead(lead_id)
        if lead:
            for key, value in kwargs.items():
                if hasattr(lead, key):
                    setattr(lead, key, value)
            self.db.commit()
            self.db.refresh(lead)
        return lead
    
    def delete_lead(self, lead_id: int) -> bool:
        """Delete a lead."""
        lead = self.get_lead(lead_id)
        if lead:
            self.db.delete(lead)
            self.db.commit()
            return True
        return False
    
    def get_opportunity(self, opportunity_id: int) -> Optional[Opportunity]:
        """Get an opportunity by ID."""
        return self.db.query(Opportunity).filter(Opportunity.id == opportunity_id).first()
    
    def update_opportunity(self, opportunity_id: int, **kwargs) -> Optional[Opportunity]:
        """Update opportunity fields."""
        opportunity = self.get_opportunity(opportunity_id)
        if opportunity:
            for key, value in kwargs.items():
                if hasattr(opportunity, key):
                    setattr(opportunity, key, value)
            self.db.commit()
            self.db.refresh(opportunity)
        return opportunity
    
    def delete_opportunity(self, opportunity_id: int) -> bool:
        """Delete an opportunity."""
        opportunity = self.get_opportunity(opportunity_id)
        if opportunity:
            self.db.delete(opportunity)
            self.db.commit()
            return True
        return False
    
    def get_quote(self, quote_id: int) -> Optional[Quote]:
        """Get a quote by ID."""
        return self.db.query(Quote).filter(Quote.id == quote_id).first()
    
    def update_quote(self, quote_id: int, **kwargs) -> Optional[Quote]:
        """Update quote fields."""
        quote = self.get_quote(quote_id)
        if quote:
            for key, value in kwargs.items():
                if hasattr(quote, key):
                    setattr(quote, key, value)
            self.db.commit()
            self.db.refresh(quote)
        return quote
    
    def delete_quote(self, quote_id: int) -> bool:
        """Delete a quote."""
        quote = self.get_quote(quote_id)
        if quote:
            self.db.delete(quote)
            self.db.commit()
            return True
        return False
    
    def close(self):
        """Close the database session."""
        self.db.close()

