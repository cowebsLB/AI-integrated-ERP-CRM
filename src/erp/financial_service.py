"""
Financial management service.
"""
from typing import List, Optional
from sqlalchemy.orm import Session
from datetime import datetime
from src.database.base import SessionLocal
from src.database.models.erp_models import Account, Transaction, Invoice, InvoiceItem, Payment, TransactionType, InvoiceStatus


class FinancialService:
    """Service for financial management operations."""
    
    def __init__(self):
        self.db: Session = SessionLocal()
    
    def create_account(self, account_code: str, account_name: str, account_type: str, 
                      parent_id: Optional[int] = None, balance: float = 0.0) -> Account:
        """Create a new account."""
        account = Account(
            account_code=account_code,
            account_name=account_name,
            account_type=account_type,
            parent_id=parent_id,
            balance=balance
        )
        self.db.add(account)
        self.db.commit()
        self.db.refresh(account)
        return account
    
    def get_accounts(self) -> List[Account]:
        """Get all accounts."""
        return self.db.query(Account).filter(Account.is_active == True).all()
    
    def create_transaction(self, account_id: int, transaction_type: TransactionType,
                          amount: float, description: str = None, reference: str = None) -> Transaction:
        """Create a new transaction."""
        transaction = Transaction(
            account_id=account_id,
            transaction_type=transaction_type,
            amount=amount,
            description=description,
            reference=reference
        )
        self.db.add(transaction)
        
        # Update account balance
        account = self.db.query(Account).filter(Account.id == account_id).first()
        if account:
            if transaction_type == TransactionType.INCOME:
                account.balance += amount
            elif transaction_type == TransactionType.EXPENSE:
                account.balance -= amount
        
        self.db.commit()
        self.db.refresh(transaction)
        return transaction
    
    def create_invoice(self, invoice_number: str, customer_id: Optional[int],
                      due_date: datetime, items: List[dict]) -> Invoice:
        """Create a new invoice."""
        invoice = Invoice(
            invoice_number=invoice_number,
            customer_id=customer_id,
            due_date=due_date
        )
        self.db.add(invoice)
        self.db.flush()
        
        subtotal = 0.0
        for item_data in items:
            item = InvoiceItem(
                invoice_id=invoice.id,
                description=item_data['description'],
                quantity=item_data.get('quantity', 1.0),
                unit_price=item_data['unit_price'],
                total=item_data.get('quantity', 1.0) * item_data['unit_price']
            )
            subtotal += item.total
            self.db.add(item)
        
        invoice.subtotal = subtotal
        invoice.tax = subtotal * 0.1  # 10% tax (adjust as needed)
        invoice.total = invoice.subtotal + invoice.tax
        
        self.db.commit()
        self.db.refresh(invoice)
        return invoice
    
    def get_invoices(self, status: Optional[InvoiceStatus] = None) -> List[Invoice]:
        """Get invoices, optionally filtered by status."""
        query = self.db.query(Invoice)
        if status:
            query = query.filter(Invoice.status == status)
        return query.order_by(Invoice.created_at.desc()).all()
    
    def record_payment(self, invoice_id: int, amount: float, payment_method: str,
                      reference: str = None) -> Payment:
        """Record a payment for an invoice."""
        payment = Payment(
            invoice_id=invoice_id,
            amount=amount,
            payment_method=payment_method,
            reference=reference,
            status="completed"
        )
        self.db.add(payment)
        
        # Update invoice status if fully paid
        invoice = self.db.query(Invoice).filter(Invoice.id == invoice_id).first()
        if invoice:
            total_paid = sum(p.amount for p in invoice.payments if p.status == "completed")
            if total_paid >= invoice.total:
                invoice.status = InvoiceStatus.PAID
        
        self.db.commit()
        self.db.refresh(payment)
        return payment
    
    def update_account(self, account_id: int, **kwargs) -> Optional[Account]:
        """Update account fields."""
        account = self.db.query(Account).filter(Account.id == account_id).first()
        if account:
            for key, value in kwargs.items():
                if hasattr(account, key):
                    setattr(account, key, value)
            self.db.commit()
            self.db.refresh(account)
        return account
    
    def delete_account(self, account_id: int) -> bool:
        """Soft delete an account (deactivate)."""
        account = self.db.query(Account).filter(Account.id == account_id).first()
        if account:
            account.is_active = False
            self.db.commit()
            return True
        return False
    
    def update_invoice(self, invoice_id: int, **kwargs) -> Optional[Invoice]:
        """Update invoice fields."""
        invoice = self.db.query(Invoice).filter(Invoice.id == invoice_id).first()
        if invoice:
            for key, value in kwargs.items():
                if hasattr(invoice, key):
                    setattr(invoice, key, value)
            self.db.commit()
            self.db.refresh(invoice)
        return invoice
    
    def delete_invoice(self, invoice_id: int) -> bool:
        """Delete an invoice."""
        invoice = self.db.query(Invoice).filter(Invoice.id == invoice_id).first()
        if invoice:
            self.db.delete(invoice)
            self.db.commit()
            return True
        return False
    
    def get_invoice(self, invoice_id: int) -> Optional[Invoice]:
        """Get an invoice by ID."""
        return self.db.query(Invoice).filter(Invoice.id == invoice_id).first()
    
    def close(self):
        """Close the database session."""
        self.db.close()

