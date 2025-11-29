"""
Inventory management service.
"""
from typing import List, Optional
from sqlalchemy.orm import Session
from datetime import datetime
from src.database.base import SessionLocal
from src.database.models.erp_models import Product, Vendor, PurchaseOrder, PurchaseOrderItem


class InventoryService:
    """Service for inventory management operations."""
    
    def __init__(self):
        self.db: Session = SessionLocal()
    
    def create_product(self, sku: str, name: str, unit_price: float = 0.0,
                      cost_price: float = 0.0, stock_quantity: float = 0.0,
                      category: str = None, description: str = None,
                      min_stock_level: float = 0.0) -> Product:
        """Create a new product."""
        product = Product(
            sku=sku,
            name=name,
            unit_price=unit_price,
            cost_price=cost_price,
            stock_quantity=stock_quantity,
            category=category,
            description=description,
            min_stock_level=min_stock_level
        )
        self.db.add(product)
        self.db.commit()
        self.db.refresh(product)
        return product
    
    def get_products(self, category: Optional[str] = None) -> List[Product]:
        """Get all products, optionally filtered by category."""
        query = self.db.query(Product).filter(Product.is_active == True)
        if category:
            query = query.filter(Product.category == category)
        return query.all()
    
    def update_stock(self, product_id: int, quantity_change: float) -> Product:
        """Update product stock quantity."""
        product = self.db.query(Product).filter(Product.id == product_id).first()
        if product:
            product.stock_quantity += quantity_change
            self.db.commit()
            self.db.refresh(product)
        return product
    
    def get_low_stock_products(self) -> List[Product]:
        """Get products below minimum stock level."""
        return self.db.query(Product).filter(
            Product.stock_quantity <= Product.min_stock_level,
            Product.is_active == True
        ).all()
    
    def create_vendor(self, name: str, email: str = None, phone: str = None,
                     address: str = None) -> Vendor:
        """Create a new vendor."""
        vendor = Vendor(
            name=name,
            email=email,
            phone=phone,
            address=address
        )
        self.db.add(vendor)
        self.db.commit()
        self.db.refresh(vendor)
        return vendor
    
    def get_vendors(self) -> List[Vendor]:
        """Get all active vendors."""
        return self.db.query(Vendor).filter(Vendor.is_active == True).all()
    
    def create_purchase_order(self, po_number: str, vendor_id: int,
                             items: List[dict], expected_date: datetime = None) -> PurchaseOrder:
        """Create a new purchase order."""
        po = PurchaseOrder(
            po_number=po_number,
            vendor_id=vendor_id,
            expected_date=expected_date
        )
        self.db.add(po)
        self.db.flush()
        
        total = 0.0
        for item_data in items:
            item = PurchaseOrderItem(
                purchase_order_id=po.id,
                product_id=item_data['product_id'],
                quantity=item_data['quantity'],
                unit_price=item_data['unit_price'],
                total=item_data['quantity'] * item_data['unit_price']
            )
            total += item.total
            self.db.add(item)
        
        po.total = total
        self.db.commit()
        self.db.refresh(po)
        return po
    
    def receive_purchase_order(self, po_id: int) -> PurchaseOrder:
        """Mark purchase order as received and update stock."""
        po = self.db.query(PurchaseOrder).filter(PurchaseOrder.id == po_id).first()
        if po:
            po.status = "received"
            # Update stock for each item
            for item in po.items:
                product = self.db.query(Product).filter(Product.id == item.product_id).first()
                if product:
                    product.stock_quantity += item.quantity
            self.db.commit()
            self.db.refresh(po)
        return po
    
    def update_product(self, product_id: int, **kwargs) -> Optional[Product]:
        """Update product fields."""
        product = self.db.query(Product).filter(Product.id == product_id).first()
        if product:
            for key, value in kwargs.items():
                if hasattr(product, key):
                    setattr(product, key, value)
            self.db.commit()
            self.db.refresh(product)
        return product
    
    def delete_product(self, product_id: int) -> bool:
        """Soft delete a product (deactivate)."""
        product = self.db.query(Product).filter(Product.id == product_id).first()
        if product:
            product.is_active = False
            self.db.commit()
            return True
        return False
    
    def get_product(self, product_id: int) -> Optional[Product]:
        """Get a product by ID."""
        return self.db.query(Product).filter(Product.id == product_id).first()
    
    def update_vendor(self, vendor_id: int, **kwargs) -> Optional[Vendor]:
        """Update vendor fields."""
        vendor = self.db.query(Vendor).filter(Vendor.id == vendor_id).first()
        if vendor:
            for key, value in kwargs.items():
                if hasattr(vendor, key):
                    setattr(vendor, key, value)
            self.db.commit()
            self.db.refresh(vendor)
        return vendor
    
    def delete_vendor(self, vendor_id: int) -> bool:
        """Soft delete a vendor (deactivate)."""
        vendor = self.db.query(Vendor).filter(Vendor.id == vendor_id).first()
        if vendor:
            vendor.is_active = False
            self.db.commit()
            return True
        return False
    
    def get_vendor(self, vendor_id: int) -> Optional[Vendor]:
        """Get a vendor by ID."""
        return self.db.query(Vendor).filter(Vendor.id == vendor_id).first()
    
    def get_purchase_order(self, po_id: int) -> Optional[PurchaseOrder]:
        """Get a purchase order by ID."""
        return self.db.query(PurchaseOrder).filter(PurchaseOrder.id == po_id).first()
    
    def close(self):
        """Close the database session."""
        self.db.close()

