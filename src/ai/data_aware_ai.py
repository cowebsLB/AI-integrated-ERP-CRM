"""
Data-aware AI service that can query the ERP-CRM database.
"""
import logging
from typing import Optional, List, Dict, Any
from src.ai.ai_service import AIService
from src.crm.contact_service import ContactService
from src.crm.sales_service import SalesService
from src.erp.financial_service import FinancialService
from src.erp.inventory_service import InventoryService
from src.erp.hr_service import HRService
from src.erp.project_service import ProjectService

logger = logging.getLogger(__name__)


class DataAwareAI:
    """AI service that can access and analyze ERP-CRM data."""
    
    def __init__(self):
        self.ai_service = AIService()
        self.contact_service = ContactService()
        self.sales_service = SalesService()
        self.financial_service = FinancialService()
        self.inventory_service = InventoryService()
        self.hr_service = HRService()
        self.project_service = ProjectService()
    
    def get_data_summary(self) -> Dict[str, Any]:
        """Get summary of all data in the system."""
        try:
            contacts = self.contact_service.get_contacts()
            customers = [c for c in contacts if c.contact_type == "customer"]
            leads = self.sales_service.get_leads()
            opportunities = self.sales_service.get_opportunities()
            invoices = self.financial_service.get_invoices()
            products = self.inventory_service.get_products()
            employees = self.hr_service.get_employees()
            projects = self.project_service.get_projects()
            
            return {
                "total_contacts": len(contacts),
                "total_customers": len(customers),
                "total_leads": len(leads),
                "total_opportunities": len(opportunities),
                "total_invoices": len(invoices),
                "total_products": len(products),
                "total_employees": len(employees),
                "total_projects": len(projects),
                "total_revenue": sum(inv.total for inv in invoices if inv.status and inv.status.value == "paid"),
                "pipeline_value": sum(opp.value * (opp.probability / 100) for opp in opportunities),
            }
        except Exception as e:
            logger.error(f"Error getting data summary: {e}")
            return {}
    
    def answer_question(self, question: str, conversation_history: Optional[List[dict]] = None) -> str:
        """Answer a question using both AI and database data."""
        question_lower = question.lower()
        
        # Get current data summary
        data = self.get_data_summary()
        
        # Check for specific data queries
        if any(word in question_lower for word in ["how many", "count", "number of", "total"]):
            if "customer" in question_lower:
                count = data.get("total_customers", 0)
                return f"You have {count} customer(s)."
            
            elif "contact" in question_lower:
                count = data.get("total_contacts", 0)
                return f"You have {count} contact(s)."
            
            elif "lead" in question_lower:
                count = data.get("total_leads", 0)
                return f"You have {count} lead(s)."
            
            elif "opportunity" in question_lower or "opportunities" in question_lower:
                count = data.get("total_opportunities", 0)
                return f"You have {count} opportunity/opportunities."
            
            elif "invoice" in question_lower:
                count = data.get("total_invoices", 0)
                return f"You have {count} invoice(s)."
            
            elif "product" in question_lower:
                count = data.get("total_products", 0)
                return f"You have {count} product(s)."
            
            elif "employee" in question_lower:
                count = data.get("total_employees", 0)
                return f"You have {count} employee(s)."
            
            elif "project" in question_lower:
                count = data.get("total_projects", 0)
                return f"You have {count} project(s)."
        
        # Revenue/money queries
        if any(word in question_lower for word in ["revenue", "income", "money", "earned", "paid"]):
            revenue = data.get("total_revenue", 0)
            return f"Total revenue: ${revenue:,.2f}"
        
        if "pipeline" in question_lower:
            pipeline = data.get("pipeline_value", 0)
            return f"Sales pipeline value: ${pipeline:,.2f}"
        
        # Build context for AI
        context = f"""You are an AI assistant for an ERP-CRM system. Here's the current data:

- Customers: {data.get('total_customers', 0)}
- Contacts: {data.get('total_contacts', 0)}
- Leads: {data.get('total_leads', 0)}
- Opportunities: {data.get('total_opportunities', 0)}
- Invoices: {data.get('total_invoices', 0)}
- Products: {data.get('total_products', 0)}
- Employees: {data.get('total_employees', 0)}
- Projects: {data.get('total_projects', 0)}
- Total Revenue: ${data.get('total_revenue', 0):,.2f}
- Pipeline Value: ${data.get('pipeline_value', 0):,.2f}

Answer questions concisely and factually. Use the data above when relevant. Keep responses brief and to the point."""
        
        # Use AI for more complex questions
        try:
            response = self.ai_service.chat(
                f"{context}\n\nUser question: {question}",
                conversation_history
            )
            return response
        except Exception as e:
            logger.error(f"Error getting AI response: {e}")
            return "I'm having trouble processing that. Please try again."

