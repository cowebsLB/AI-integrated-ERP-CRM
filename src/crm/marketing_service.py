"""
Marketing service.
"""
from typing import List, Optional
from sqlalchemy.orm import Session
from datetime import datetime
from src.database.base import SessionLocal
from src.database.models.crm_models import Campaign, CampaignContact


class MarketingService:
    """Service for marketing operations."""
    
    def __init__(self):
        self.db: Session = SessionLocal()
    
    def create_campaign(self, name: str, campaign_type: str, start_date: datetime = None,
                       end_date: datetime = None, budget: float = 0.0,
                       description: str = None) -> Campaign:
        """Create a new marketing campaign."""
        campaign = Campaign(
            name=name,
            campaign_type=campaign_type,
            start_date=start_date,
            end_date=end_date,
            budget=budget,
            description=description
        )
        self.db.add(campaign)
        self.db.commit()
        self.db.refresh(campaign)
        return campaign
    
    def get_campaigns(self, status: Optional[str] = None) -> List[Campaign]:
        """Get all campaigns, optionally filtered by status."""
        query = self.db.query(Campaign)
        if status:
            query = query.filter(Campaign.status == status)
        return query.order_by(Campaign.created_at.desc()).all()
    
    def add_contact_to_campaign(self, campaign_id: int, contact_id: int) -> CampaignContact:
        """Add a contact to a campaign."""
        campaign_contact = CampaignContact(
            campaign_id=campaign_id,
            contact_id=contact_id
        )
        self.db.add(campaign_contact)
        self.db.commit()
        self.db.refresh(campaign_contact)
        return campaign_contact
    
    def get_campaign_contacts(self, campaign_id: int) -> List[CampaignContact]:
        """Get all contacts in a campaign."""
        return self.db.query(CampaignContact).filter(
            CampaignContact.campaign_id == campaign_id
        ).all()
    
    def get_campaign(self, campaign_id: int) -> Optional[Campaign]:
        """Get a campaign by ID."""
        return self.db.query(Campaign).filter(Campaign.id == campaign_id).first()
    
    def update_campaign(self, campaign_id: int, **kwargs) -> Optional[Campaign]:
        """Update campaign fields."""
        campaign = self.get_campaign(campaign_id)
        if campaign:
            for key, value in kwargs.items():
                if hasattr(campaign, key):
                    setattr(campaign, key, value)
            self.db.commit()
            self.db.refresh(campaign)
        return campaign
    
    def delete_campaign(self, campaign_id: int) -> bool:
        """Delete a campaign."""
        campaign = self.get_campaign(campaign_id)
        if campaign:
            self.db.delete(campaign)
            self.db.commit()
            return True
        return False
    
    def remove_contact_from_campaign(self, campaign_id: int, contact_id: int) -> bool:
        """Remove a contact from a campaign."""
        campaign_contact = self.db.query(CampaignContact).filter(
            CampaignContact.campaign_id == campaign_id,
            CampaignContact.contact_id == contact_id
        ).first()
        if campaign_contact:
            self.db.delete(campaign_contact)
            self.db.commit()
            return True
        return False
    
    def close(self):
        """Close the database session."""
        self.db.close()

