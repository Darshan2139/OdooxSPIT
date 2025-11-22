"""
StockMaster Utility Functions
"""

from functools import wraps
from flask import flash, redirect, url_for
from flask_login import current_user
from datetime import datetime, timedelta


def inventory_manager_required(f):
    """Decorator to require inventory manager role"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated:
            return redirect(url_for('login'))
        if current_user.role != 'inventory_manager':
            flash('Access denied. Inventory Manager role required.', 'error')
            return redirect(url_for('dashboard'))
        return f(*args, **kwargs)
    return decorated_function


def warehouse_staff_or_manager(f):
    """Decorator to allow warehouse staff or manager"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated:
            return redirect(url_for('login'))
        if current_user.role not in ['warehouse_staff', 'inventory_manager']:
            flash('Access denied.', 'error')
            return redirect(url_for('dashboard'))
        return f(*args, **kwargs)
    return decorated_function


# ========== Notification Functions ==========

def create_notification(user_id, title, message, notification_type='system', related_model=None, related_id=None, expires_in_days=30):
    """
    Create a notification for a user
    
    Args:
        user_id: ID of the user to notify
        title: Notification title
        message: Notification message
        notification_type: Type of notification ('low_stock', 'operation_completed', 'alert', 'system')
        related_model: Optional model name (e.g., 'product', 'receipt')
        related_id: Optional ID of related object
        expires_in_days: Days until notification expires
    """
    from app import db
    from models import Notification, NotificationPreference
    
    # Check user preferences
    prefs = NotificationPreference.query.filter_by(user_id=user_id).first()
    
    # Check if this type of notification is enabled
    if prefs:
        if notification_type == 'low_stock' and not prefs.enable_low_stock_alerts:
            return None
        elif notification_type == 'operation_completed' and not prefs.enable_operation_alerts:
            return None
        elif notification_type == 'alert' and not prefs.enable_system_alerts:
            return None
    
    # Calculate expiry date
    expires_at = None
    if expires_in_days:
        expires_at = datetime.utcnow() + timedelta(days=expires_in_days)
    
    notification = Notification(
        user_id=user_id,
        title=title,
        message=message,
        notification_type=notification_type,
        related_model=related_model,
        related_id=related_id,
        expires_at=expires_at
    )
    
    db.session.add(notification)
    db.session.commit()
    
    return notification


def get_user_unread_notifications_count(user_id):
    """Get count of unread notifications for a user"""
    from models import Notification
    
    count = Notification.query.filter(
        Notification.user_id == user_id,
        Notification.is_read == False,
        (Notification.expires_at == None) | (Notification.expires_at > datetime.utcnow())
    ).count()
    
    return count


def get_user_notifications(user_id, limit=10, unread_only=False):
    """
    Get notifications for a user
    
    Args:
        user_id: User ID
        limit: Maximum number of notifications to return
        unread_only: Only return unread notifications
    """
    from models import Notification
    
    query = Notification.query.filter(
        Notification.user_id == user_id,
        (Notification.expires_at == None) | (Notification.expires_at > datetime.utcnow())
    )
    
    if unread_only:
        query = query.filter(Notification.is_read == False)
    
    notifications = query.order_by(Notification.created_at.desc()).limit(limit).all()
    
    return notifications


def notify_low_stock_alert(product):
    """
    Create a low stock alert notification for all users
    
    Args:
        product: Product object
    """
    from models import User, NotificationPreference
    
    # Get all users who should receive low stock alerts
    users_query = User.query.all()
    
    for user in users_query:
        prefs = NotificationPreference.query.filter_by(user_id=user.id).first()
        
        if prefs and prefs.enable_low_stock_alerts:
            create_notification(
                user_id=user.id,
                title=f"Low Stock Alert: {product.name}",
                message=f"Product '{product.name}' (SKU: {product.sku}) is running low on stock. Current stock: {product.total_stock}, Minimum: {product.min_stock}",
                notification_type='low_stock',
                related_model='product',
                related_id=product.id
            )


def notify_operation_completed(user_id, operation_type, reference, details=None):
    """
    Create an operation completed notification
    
    Args:
        user_id: User ID
        operation_type: Type of operation (receipt, delivery, transfer, adjustment)
        reference: Reference number (e.g., receipt number)
        details: Optional additional details
    """
    title_map = {
        'receipt': 'Receipt Completed',
        'delivery': 'Delivery Completed',
        'transfer': 'Transfer Completed',
        'adjustment': 'Adjustment Completed'
    }
    
    message = f"{title_map.get(operation_type, 'Operation')} - Reference: {reference}"
    if details:
        message += f" - {details}"
    
    create_notification(
        user_id=user_id,
        title=title_map.get(operation_type, 'Operation Completed'),
        message=message,
        notification_type='operation_completed',
        related_model=operation_type,
        related_id=None
    )


def notify_system_alert(user_id, title, message, related_model=None, related_id=None):
    """
    Create a system alert notification
    
    Args:
        user_id: User ID
        title: Alert title
        message: Alert message
        related_model: Optional model reference
        related_id: Optional ID reference
    """
    create_notification(
        user_id=user_id,
        title=title,
        message=message,
        notification_type='alert',
        related_model=related_model,
        related_id=related_id
    )


def validate_price(value):
    """Validate and normalize a price value. Returns float or raises ValueError."""
    try:
        if value is None or value == '':
            return 0.0
        pv = float(value)
    except (TypeError, ValueError):
        raise ValueError('Invalid price value')
    if pv < 0:
        raise ValueError('Price cannot be negative')
    return pv


def log_price_change(user_id, product, old_cost, new_cost, old_sale, new_sale, reason=None):
    """Create a PriceHistory record logging the change."""
    from app import db
    from models import PriceHistory

    ph = PriceHistory(
        product_id=product.id,
        old_cost=old_cost,
        new_cost=new_cost,
        old_sale=old_sale,
        new_sale=new_sale,
        changed_by=user_id,
        reason=reason
    )
    db.session.add(ph)
    db.session.commit()
    return ph
