"""
Document processing service with AI-powered PDF parsing and extraction.
"""
import logging
from typing import Dict, List, Any, Optional
from pathlib import Path
import pdfplumber
from PyPDF2 import PdfReader
from src.ai.ai_service import AIService

logger = logging.getLogger(__name__)


class DocumentProcessor:
    """Service for processing documents with AI assistance."""
    
    def __init__(self):
        self.ai_service = AIService()
    
    def extract_text_from_pdf(self, pdf_path: str) -> str:
        """Extract text from PDF file."""
        try:
            text_content = []
            
            # Try pdfplumber first (better for complex layouts)
            try:
                with pdfplumber.open(pdf_path) as pdf:
                    for page in pdf.pages:
                        text = page.extract_text()
                        if text:
                            text_content.append(text)
            except Exception as e:
                logger.warning(f"pdfplumber failed, trying PyPDF2: {e}")
                # Fallback to PyPDF2
                reader = PdfReader(pdf_path)
                for page in reader.pages:
                    text = page.extract_text()
                    if text:
                        text_content.append(text)
            
            return "\n\n".join(text_content)
        except Exception as e:
            logger.error(f"Error extracting text from PDF: {e}")
            raise
    
    def extract_tables_from_pdf(self, pdf_path: str) -> List[Dict[str, Any]]:
        """Extract tables from PDF."""
        try:
            tables = []
            with pdfplumber.open(pdf_path) as pdf:
                for page_num, page in enumerate(pdf.pages, 1):
                    page_tables = page.extract_tables()
                    for table in page_tables:
                        if table:
                            tables.append({
                                "page": page_num,
                                "data": table
                            })
            return tables
        except Exception as e:
            logger.error(f"Error extracting tables from PDF: {e}")
            return []
    
    def extract_invoice_data(self, pdf_path: str) -> Dict[str, Any]:
        """Extract invoice data from PDF using AI."""
        try:
            text = self.extract_text_from_pdf(pdf_path)
            
            # Use AI to extract structured invoice data
            prompt = f"""Extract invoice information from the following text and return as JSON:
            
Text:
{text[:2000]}  # Limit to avoid token limits

Extract:
- invoice_number
- date
- due_date
- customer_name
- customer_address
- total_amount
- tax_amount
- line_items (list of items with description, quantity, unit_price, total)

Return only valid JSON, no additional text."""

            if self.ai_service.is_available():
                response = self.ai_service.generate_response(prompt, max_tokens=1000)
                # Parse JSON from response
                import json
                import re
                json_match = re.search(r'\{.*\}', response, re.DOTALL)
                if json_match:
                    return json.loads(json_match.group())
            
            # Fallback: basic extraction
            return self._basic_invoice_extraction(text)
        except Exception as e:
            logger.error(f"Error extracting invoice data: {e}")
            return {}
    
    def _basic_invoice_extraction(self, text: str) -> Dict[str, Any]:
        """Basic invoice extraction without AI."""
        import re
        
        invoice_data = {}
        
        # Extract invoice number
        invoice_match = re.search(r'invoice[#\s:]*([A-Z0-9-]+)', text, re.IGNORECASE)
        if invoice_match:
            invoice_data["invoice_number"] = invoice_match.group(1)
        
        # Extract dates
        date_match = re.search(r'date[:\s]+(\d{1,2}[/-]\d{1,2}[/-]\d{2,4})', text, re.IGNORECASE)
        if date_match:
            invoice_data["date"] = date_match.group(1)
        
        # Extract total
        total_match = re.search(r'total[:\s$]*([\d,]+\.?\d*)', text, re.IGNORECASE)
        if total_match:
            invoice_data["total_amount"] = float(total_match.group(1).replace(',', ''))
        
        return invoice_data
    
    def extract_purchase_order_data(self, pdf_path: str) -> Dict[str, Any]:
        """Extract purchase order data from PDF."""
        text = self.extract_text_from_pdf(pdf_path)
        
        prompt = f"""Extract purchase order information from the following text:
        
{text[:2000]}

Extract:
- po_number
- vendor_name
- order_date
- items (list with product_name, quantity, unit_price)
- total_amount

Return only valid JSON."""

        if self.ai_service.is_available():
            response = self.ai_service.generate_response(prompt, max_tokens=1000)
            import json
            import re
            json_match = re.search(r'\{.*\}', response, re.DOTALL)
            if json_match:
                return json.loads(json_match.group())
        
        return {}
    
    def summarize_document(self, pdf_path: str) -> str:
        """Generate AI summary of document."""
        text = self.extract_text_from_pdf(pdf_path)
        
        # Limit text length for AI processing
        text_sample = text[:3000] if len(text) > 3000 else text
        
        prompt = f"""Summarize the following document in 2-3 sentences:

{text_sample}"""

        if self.ai_service.is_available():
            return self.ai_service.generate_response(prompt, max_tokens=200)
        
        return "Document summary unavailable (AI service not available)"

