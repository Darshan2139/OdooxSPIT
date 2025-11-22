"""
StockMaster Database Models
"""

from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from datetime import datetime

# Import db from app to avoid circular import
from app import db

class User(UserMixin, db.Model):
    """User model for authentication"""
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False, index=True)
    password = db.Column(db.String(255), nullable=False)
    role = db.Column(db.String(20), default='warehouse_staff')  # inventory_manager or warehouse_staff
    otp_code = db.Column(db.String(6))
    otp_expiry = db.Column(db.DateTime)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f'<User {self.email}>'


class Warehouse(db.Model):
    """Warehouse model"""
    __tablename__ = 'warehouses'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    code = db.Column(db.String(20), unique=True, nullable=False, index=True)
    address = db.Column(db.Text)
    city = db.Column(db.String(100))
    state = db.Column(db.String(100))
    zip_code = db.Column(db.String(20))
    country = db.Column(db.String(100))
    phone = db.Column(db.String(20))
    email = db.Column(db.String(100))
    active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    products = db.relationship('ProductLocation', backref='warehouse', lazy=True)
    
    def __repr__(self):
        return f'<Warehouse {self.name}>'


class Category(db.Model):
    """Product category model"""
    __tablename__ = 'categories'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False, unique=True)
    description = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    products = db.relationship('Product', backref='category', lazy=True)
    
    def __repr__(self):
        return f'<Category {self.name}>'


class Product(db.Model):
    """Product model"""
    __tablename__ = 'products'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False)
    sku = db.Column(db.String(50), unique=True, nullable=False, index=True)
    category_id = db.Column(db.Integer, db.ForeignKey('categories.id'))
    uom = db.Column(db.String(20), default='Unit')  # Unit of Measure
    min_stock = db.Column(db.Float, default=0.0)
    max_stock = db.Column(db.Float, default=0.0)
    reorder_qty = db.Column(db.Float, default=0.0)
    # Pricing
    cost_price = db.Column(db.Float, default=0.0)
    sale_price = db.Column(db.Float, default=0.0)
    currency = db.Column(db.String(8), default='USD')
    active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    locations = db.relationship('ProductLocation', backref='product', lazy=True, cascade='all, delete-orphan')
    receipt_lines = db.relationship('ReceiptLine', backref='product', lazy=True)
    delivery_lines = db.relationship('DeliveryLine', backref='product', lazy=True)
    transfer_lines = db.relationship('TransferLine', backref='product', lazy=True)
    adjustments = db.relationship('Adjustment', backref='product', lazy=True)
    ledger_entries = db.relationship('StockLedger', backref='product', lazy=True)
    
    @property
    def total_stock(self):
        """Calculate total stock across all locations"""
        return sum(loc.quantity for loc in self.locations)
    
    @property
    def low_stock(self):
        """Check if product is low on stock"""
        return self.min_stock > 0 and self.total_stock <= self.min_stock
    
    def get_stock_by_location(self, location_id):
        """Get stock quantity for a specific location"""
        location = ProductLocation.query.filter_by(
            product_id=self.id, 
            location_id=location_id
        ).first()
        return location.quantity if location else 0.0
    
    def update_stock_location(self, location_id, quantity):
        """Update stock for a specific location"""
        location = ProductLocation.query.filter_by(
            product_id=self.id,
            location_id=location_id
        ).first()
        
        if location:
            new_qty = location.quantity + quantity
            if new_qty < 0:
                raise ValueError(f'Insufficient stock. Available: {location.quantity}, Required: {abs(quantity)}')
            location.quantity = new_qty
        else:
            if quantity < 0:
                raise ValueError(f'Insufficient stock. Available: 0, Required: {abs(quantity)}')
            location = ProductLocation(
                product_id=self.id,
                location_id=location_id,
                quantity=quantity
            )
            db.session.add(location)
        
        db.session.commit()
    
    def __repr__(self):
        return f'<Product {self.name}>'


class Location(db.Model):
    """Location model (within warehouses)"""
    __tablename__ = 'locations'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    warehouse_id = db.Column(db.Integer, db.ForeignKey('warehouses.id'), nullable=False)
    code = db.Column(db.String(20))
    description = db.Column(db.Text)
    active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    warehouse = db.relationship('Warehouse', backref='locations')
    product_locations = db.relationship('ProductLocation', backref='location', lazy=True)
    
    def __repr__(self):
        return f'<Location {self.name}>'


class ProductLocation(db.Model):
    """Product stock by location"""
    __tablename__ = 'product_locations'
    
    id = db.Column(db.Integer, primary_key=True)
    product_id = db.Column(db.Integer, db.ForeignKey('products.id'), nullable=False)
    location_id = db.Column(db.Integer, db.ForeignKey('locations.id'), nullable=False)
    quantity = db.Column(db.Float, default=0.0, nullable=False)
    warehouse_id = db.Column(db.Integer, db.ForeignKey('warehouses.id'))
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    __table_args__ = (db.UniqueConstraint('product_id', 'location_id', name='unique_product_location'),)
    
    def __repr__(self):
        return f'<ProductLocation {self.product_id}-{self.location_id}: {self.quantity}>'


class Receipt(db.Model):
    """Receipt model (Incoming Stock)"""
    __tablename__ = 'receipts'
    
    id = db.Column(db.Integer, primary_key=True)
    receipt_number = db.Column(db.String(50), unique=True, nullable=False, index=True)
    date = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    supplier_id = db.Column(db.Integer, db.ForeignKey('partners.id'))
    warehouse_id = db.Column(db.Integer, db.ForeignKey('warehouses.id'), nullable=False)
    location_id = db.Column(db.Integer, db.ForeignKey('locations.id'), nullable=False)
    state = db.Column(db.String(20), default='draft')  # draft, waiting, ready, done, canceled
    notes = db.Column(db.Text)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    supplier = db.relationship('Partner', foreign_keys=[supplier_id])
    warehouse = db.relationship('Warehouse')
    location = db.relationship('Location')
    user = db.relationship('User')
    lines = db.relationship('ReceiptLine', backref='receipt', lazy=True, cascade='all, delete-orphan')
    
    @property
    def total_products(self):
        return len(self.lines)
    
    @property
    def total_quantity(self):
        return sum(line.quantity for line in self.lines)
    
    def __repr__(self):
        return f'<Receipt {self.receipt_number}>'


class ReceiptLine(db.Model):
    """Receipt line items"""
    __tablename__ = 'receipt_lines'
    
    id = db.Column(db.Integer, primary_key=True)
    receipt_id = db.Column(db.Integer, db.ForeignKey('receipts.id'), nullable=False)
    product_id = db.Column(db.Integer, db.ForeignKey('products.id'), nullable=False)
    quantity = db.Column(db.Float, nullable=False)
    received_qty = db.Column(db.Float, default=0.0)
    
    def __repr__(self):
        return f'<ReceiptLine {self.id}>'


class Delivery(db.Model):
    """Delivery model (Outgoing Stock)"""
    __tablename__ = 'deliveries'
    
    id = db.Column(db.Integer, primary_key=True)
    delivery_number = db.Column(db.String(50), unique=True, nullable=False, index=True)
    date = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    customer_id = db.Column(db.Integer, db.ForeignKey('partners.id'))
    warehouse_id = db.Column(db.Integer, db.ForeignKey('warehouses.id'), nullable=False)
    location_id = db.Column(db.Integer, db.ForeignKey('locations.id'), nullable=False)
    state = db.Column(db.String(20), default='draft')  # draft, picking, packing, ready, done, canceled
    notes = db.Column(db.Text)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    customer = db.relationship('Partner', foreign_keys=[customer_id])
    warehouse = db.relationship('Warehouse')
    location = db.relationship('Location')
    user = db.relationship('User')
    lines = db.relationship('DeliveryLine', backref='delivery', lazy=True, cascade='all, delete-orphan')
    
    @property
    def total_products(self):
        return len(self.lines)
    
    @property
    def total_quantity(self):
        return sum(line.quantity for line in self.lines)
    
    def __repr__(self):
        return f'<Delivery {self.delivery_number}>'


class DeliveryLine(db.Model):
    """Delivery line items"""
    __tablename__ = 'delivery_lines'
    
    id = db.Column(db.Integer, primary_key=True)
    delivery_id = db.Column(db.Integer, db.ForeignKey('deliveries.id'), nullable=False)
    product_id = db.Column(db.Integer, db.ForeignKey('products.id'), nullable=False)
    quantity = db.Column(db.Float, nullable=False)
    picked_qty = db.Column(db.Float, default=0.0)
    packed_qty = db.Column(db.Float, default=0.0)
    
    def __repr__(self):
        return f'<DeliveryLine {self.id}>'


class Transfer(db.Model):
    """Internal Transfer model"""
    __tablename__ = 'transfers'
    
    id = db.Column(db.Integer, primary_key=True)
    transfer_number = db.Column(db.String(50), unique=True, nullable=False, index=True)
    date = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    source_location_id = db.Column(db.Integer, db.ForeignKey('locations.id'), nullable=False)
    destination_location_id = db.Column(db.Integer, db.ForeignKey('locations.id'), nullable=False)
    state = db.Column(db.String(20), default='draft')  # draft, waiting, ready, done, canceled
    notes = db.Column(db.Text)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    source_location = db.relationship('Location', foreign_keys=[source_location_id])
    destination_location = db.relationship('Location', foreign_keys=[destination_location_id])
    user = db.relationship('User')
    lines = db.relationship('TransferLine', backref='transfer', lazy=True, cascade='all, delete-orphan')
    
    @property
    def total_products(self):
        return len(self.lines)
    
    @property
    def total_quantity(self):
        return sum(line.quantity for line in self.lines)
    
    def __repr__(self):
        return f'<Transfer {self.transfer_number}>'


class TransferLine(db.Model):
    """Transfer line items"""
    __tablename__ = 'transfer_lines'
    
    id = db.Column(db.Integer, primary_key=True)
    transfer_id = db.Column(db.Integer, db.ForeignKey('transfers.id'), nullable=False)
    product_id = db.Column(db.Integer, db.ForeignKey('products.id'), nullable=False)
    quantity = db.Column(db.Float, nullable=False)
    
    def __repr__(self):
        return f'<TransferLine {self.id}>'


class Adjustment(db.Model):
    """Stock Adjustment model"""
    __tablename__ = 'adjustments'
    
    id = db.Column(db.Integer, primary_key=True)
    adjustment_number = db.Column(db.String(50), unique=True, nullable=False, index=True)
    date = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    product_id = db.Column(db.Integer, db.ForeignKey('products.id'), nullable=False)
    location_id = db.Column(db.Integer, db.ForeignKey('locations.id'), nullable=False)
    recorded_qty = db.Column(db.Float, default=0.0)
    counted_qty = db.Column(db.Float, nullable=False)
    difference = db.Column(db.Float, default=0.0)
    reason = db.Column(db.Text)
    state = db.Column(db.String(20), default='draft')  # draft, done, canceled
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    location = db.relationship('Location')
    user = db.relationship('User')
    
    def __repr__(self):
        return f'<Adjustment {self.adjustment_number}>'


class Partner(db.Model):
    """Partner model (Suppliers and Customers)"""
    __tablename__ = 'partners'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False)
    type = db.Column(db.String(20))  # supplier or customer
    email = db.Column(db.String(100))
    phone = db.Column(db.String(20))
    address = db.Column(db.Text)
    city = db.Column(db.String(100))
    state = db.Column(db.String(100))
    zip_code = db.Column(db.String(20))
    country = db.Column(db.String(100))
    active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    receipts = db.relationship('Receipt', backref='partner_receipts', foreign_keys='Receipt.supplier_id')
    deliveries = db.relationship('Delivery', backref='partner_deliveries', foreign_keys='Delivery.customer_id')
    
    def __repr__(self):
        return f'<Partner {self.name}>'


class StockLedger(db.Model):
    """Stock Ledger (Audit Trail)"""
    __tablename__ = 'stock_ledger'
    
    id = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.DateTime, default=datetime.utcnow, nullable=False, index=True)
    product_id = db.Column(db.Integer, db.ForeignKey('products.id'), nullable=False, index=True)
    location_id = db.Column(db.Integer, db.ForeignKey('locations.id'), nullable=False, index=True)
    operation_type = db.Column(db.String(20), nullable=False, index=True)  # receipt, delivery, transfer_in, transfer_out, adjustment
    reference = db.Column(db.String(50), nullable=False, index=True)
    quantity_in = db.Column(db.Float, default=0.0)
    quantity_out = db.Column(db.Float, default=0.0)
    balance = db.Column(db.Float, nullable=False)
    partner_id = db.Column(db.Integer, db.ForeignKey('partners.id'))
    notes = db.Column(db.Text)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    
    # Relationships
    location = db.relationship('Location')
    partner = db.relationship('Partner')
    user = db.relationship('User')
    
    def __repr__(self):
        return f'<StockLedger {self.reference}>'


class Notification(db.Model):
    """Notification model"""
    __tablename__ = 'notifications'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, index=True)
    title = db.Column(db.String(200), nullable=False)
    message = db.Column(db.Text, nullable=False)
    notification_type = db.Column(db.String(50), nullable=False)  # low_stock, operation_completed, alert, system
    is_read = db.Column(db.Boolean, default=False, index=True)
    related_model = db.Column(db.String(50))  # e.g., 'product', 'receipt', 'delivery'
    related_id = db.Column(db.Integer)  # ID of related object
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False, index=True)
    read_at = db.Column(db.DateTime)
    expires_at = db.Column(db.DateTime)  # Optional: for auto-deletion of old notifications
    
    # Relationships
    user = db.relationship('User', backref='notifications')
    
    def __repr__(self):
        return f'<Notification {self.id}: {self.title}>'
    
    def mark_as_read(self):
        """Mark notification as read"""
        self.is_read = True
        self.read_at = datetime.utcnow()
        db.session.commit()
    
    @property
    def is_expired(self):
        """Check if notification has expired"""
        if self.expires_at:
            return datetime.utcnow() > self.expires_at
        return False


class NotificationPreference(db.Model):
    """User notification preferences"""
    __tablename__ = 'notification_preferences'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), unique=True, nullable=False)
    enable_low_stock_alerts = db.Column(db.Boolean, default=True)
    enable_operation_alerts = db.Column(db.Boolean, default=True)
    enable_system_alerts = db.Column(db.Boolean, default=True)
    enable_email_notifications = db.Column(db.Boolean, default=False)
    low_stock_threshold = db.Column(db.Float, default=0.3)  # Notify when stock < min_stock * threshold
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    user = db.relationship('User', backref='notification_preferences')
    
    def __repr__(self):
        return f'<NotificationPreference {self.user_id}>'


class PriceHistory(db.Model):
    """Price history for products"""
    __tablename__ = 'price_history'

    id = db.Column(db.Integer, primary_key=True)
    product_id = db.Column(db.Integer, db.ForeignKey('products.id'), nullable=False, index=True)
    old_cost = db.Column(db.Float)
    new_cost = db.Column(db.Float)
    old_sale = db.Column(db.Float)
    new_sale = db.Column(db.Float)
    changed_by = db.Column(db.Integer, db.ForeignKey('users.id'))
    reason = db.Column(db.String(255))
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False, index=True)

    product = db.relationship('Product')
    user = db.relationship('User')

    def __repr__(self):
        return f'<PriceHistory {self.product_id} @ {self.created_at}>'

