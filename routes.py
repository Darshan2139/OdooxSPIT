"""
StockMaster Routes
"""

from flask import render_template, request, redirect, url_for, flash, jsonify, session
from flask_login import login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime, timedelta
import random
import string
from app import app, db, send_email
from models import (User, Warehouse, Category, Product, Location, ProductLocation,
                   Receipt, ReceiptLine, Delivery, DeliveryLine, Transfer, TransferLine,
                   Adjustment, Partner, StockLedger, Notification, NotificationPreference)
from utils import inventory_manager_required, warehouse_staff_or_manager, create_notification, get_user_unread_notifications_count, get_user_notifications, notify_operation_completed

def generate_sequence(prefix, model_class):
    """Generate unique sequence number"""
    count = model_class.query.count()
    return f"{prefix}-{str(count + 1).zfill(5)}"

# ========== Authentication Routes ==========

@app.route('/')
def index():
    """Landing page"""
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))
    return redirect(url_for('login'))

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    """User signup"""
    if request.method == 'POST':
        name = request.form.get('name')
        email = request.form.get('email')
        password = request.form.get('password')
        role = request.form.get('role', 'warehouse_staff')
        
        if not name or not email or not password:
            flash('All fields are required', 'error')
            return render_template('signup.html')
        
        if User.query.filter_by(email=email).first():
            flash('Email already registered', 'error')
            return render_template('signup.html')
        
        user = User(
            name=name,
            email=email,
            password=generate_password_hash(password),
            role=role
        )
        db.session.add(user)
        db.session.commit()
        
        flash('Account created successfully! Please login.', 'success')
        return redirect(url_for('login'))
    
    return render_template('signup.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    """User login"""
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        
        user = User.query.filter_by(email=email).first()
        
        if user and check_password_hash(user.password, password):
            login_user(user)
            flash('Login successful!', 'success')
            return redirect(url_for('dashboard'))
        else:
            flash('Invalid email or password', 'error')
    
    return render_template('login.html')

@app.route('/logout')
@login_required
def logout():
    """User logout"""
    logout_user()
    flash('Logged out successfully', 'success')
    return redirect(url_for('login'))

@app.route('/forgot-password', methods=['GET', 'POST'])
def forgot_password():
    """Request OTP for password reset"""
    if request.method == 'POST':
        email = request.form.get('email')
        user = User.query.filter_by(email=email).first()
        
        if user:
            # Generate 6-digit OTP
            otp = ''.join(random.choices(string.digits, k=6))
            user.otp_code = otp
            user.otp_expiry = datetime.utcnow() + timedelta(minutes=10)
            db.session.commit()
            
            # Send OTP via email
            subject = "StockMaster - Password Reset OTP"
            body = f"Your OTP for password reset is: {otp}\n\nThis OTP will expire in 10 minutes."
            if send_email(subject, app.config['MAIL_DEFAULT_SENDER'], [email], body):
                flash('OTP sent to your email. Please check your inbox.', 'info')
            else:
                flash('Failed to send OTP email. Please try again later.', 'error')
                return redirect(url_for('forgot_password'))
            session['reset_email'] = email
            return redirect(url_for('reset_password'))
        else:
            flash('Email not found', 'error')
    
    return render_template('forgot_password.html')

@app.route('/reset-password', methods=['GET', 'POST'])
def reset_password():
    """Reset password with OTP"""
    email = session.get('reset_email')
    if not email:
        return redirect(url_for('forgot_password'))
    
    if request.method == 'POST':
        otp = request.form.get('otp')
        new_password = request.form.get('password')
        
        user = User.query.filter_by(email=email).first()
        
        if user and user.otp_code == otp and user.otp_expiry > datetime.utcnow():
            user.password = generate_password_hash(new_password)
            user.otp_code = None
            user.otp_expiry = None
            db.session.commit()
            session.pop('reset_email', None)
            flash('Password reset successfully! Please login.', 'success')
            return redirect(url_for('login'))
        else:
            flash('Invalid or expired OTP', 'error')
    
    return render_template('reset_password.html', email=email)

# ========== Test Email ==========

@app.route('/test-email')
def test_email():
    """Test email endpoint"""
    try:
        success = send_email(
            subject='Test Email from StockMaster',
            sender=app.config['MAIL_USERNAME'],
            recipients=[app.config['MAIL_USERNAME']],
            text_body='This is a test email from StockMaster. If you\'re reading this, the email service is working!',
            html_body='''
                <h1>StockMaster Test Email</h1>
                <p>If you're reading this, the email service is working correctly!</p>
                <p>This email confirms that your StockMaster application can send emails.</p>
            '''
        )
        if success:
            return jsonify({'status': 'success', 'message': 'Test email sent successfully!'}), 200
        else:
            return jsonify({'status': 'error', 'message': 'Failed to send test email. Check server logs.'}), 500
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500

# ========== Dashboard ==========

@app.route('/dashboard')
@login_required
def dashboard():
    """Dashboard with KPIs"""
    kpis = {
        'total_products': Product.query.filter_by(active=True).count(),
        'low_stock_items': sum(1 for p in Product.query.filter_by(active=True).all() if p.low_stock),
        'out_of_stock_items': sum(1 for p in Product.query.filter_by(active=True).all() if p.total_stock <= 0),
        'pending_receipts': Receipt.query.filter(Receipt.state.in_(['draft', 'waiting', 'ready'])).count(),
        'pending_deliveries': Delivery.query.filter(Delivery.state.in_(['draft', 'picking', 'packing', 'ready'])).count(),
        'scheduled_transfers': Transfer.query.filter(Transfer.state.in_(['draft', 'waiting', 'ready'])).count(),
    }
    
    # Recent activities
    recent_receipts = Receipt.query.order_by(Receipt.created_at.desc()).limit(5).all()
    recent_deliveries = Delivery.query.order_by(Delivery.created_at.desc()).limit(5).all()
    low_stock_products = [p for p in Product.query.filter_by(active=True).all() if p.low_stock][:10]
    
    return render_template('dashboard.html', kpis=kpis, recent_receipts=recent_receipts, 
                         recent_deliveries=recent_deliveries, low_stock_products=low_stock_products)

# ========== Products ==========

@app.route('/products')
@login_required
def products():
    """List products"""
    search = request.args.get('search', '')
    category_id = request.args.get('category_id', type=int)
    low_stock = request.args.get('low_stock') == '1'
    
    query = Product.query.filter_by(active=True)
    
    if search:
        query = query.filter(Product.name.contains(search) | Product.sku.contains(search))
    if category_id:
        query = query.filter_by(category_id=category_id)
    if low_stock:
        products_list = query.all()
        products_list = [p for p in products_list if p.low_stock]
    else:
        products_list = query.all()
    
    categories = Category.query.all()
    return render_template('products/list.html', products=products_list, categories=categories, 
                         search=search, category_id=category_id, low_stock=low_stock)

@app.route('/products/create', methods=['GET', 'POST'])
@login_required
@warehouse_staff_or_manager
def product_create():
    """Create product"""
    if request.method == 'POST':
        product = Product(
            name=request.form.get('name'),
            sku=request.form.get('sku'),
            category_id=request.form.get('category_id', type=int) or None,
            uom=request.form.get('uom', 'Unit'),
            min_stock=float(request.form.get('min_stock', 0) or 0),
            max_stock=float(request.form.get('max_stock', 0) or 0),
            reorder_qty=float(request.form.get('reorder_qty', 0) or 0),
            cost_price=float(request.form.get('cost_price', 0) or 0),
            sale_price=float(request.form.get('sale_price', 0) or 0),
            currency=request.form.get('currency', 'USD'),
        )
        db.session.add(product)
        db.session.commit()
        flash('Product created successfully', 'success')
        create_notification(current_user.id, 'Product Created', f'New product "{product.name}" has been created', 'system', 'product', product.id)
        return redirect(url_for('products'))
    
    categories = Category.query.all()
    return render_template('products/form.html', product=None, categories=categories)

@app.route('/products/<int:id>')
@login_required
def product_detail(id):
    """Product detail"""
    product = Product.query.get_or_404(id)
    return render_template('products/detail.html', product=product)

@app.route('/products/<int:id>/edit', methods=['GET', 'POST'])
@login_required
@warehouse_staff_or_manager
def product_edit(id):
    """Edit product"""
    product = Product.query.get_or_404(id)
    
    if request.method == 'POST':
        product.name = request.form.get('name')
        product.sku = request.form.get('sku')
        product.category_id = request.form.get('category_id', type=int) or None
        product.uom = request.form.get('uom', 'Unit')
        product.min_stock = float(request.form.get('min_stock', 0) or 0)
        product.max_stock = float(request.form.get('max_stock', 0) or 0)
        product.reorder_qty = float(request.form.get('reorder_qty', 0) or 0)
        # Pricing updates
        try:
            product.cost_price = float(request.form.get('cost_price', product.cost_price) or product.cost_price or 0)
        except ValueError:
            product.cost_price = product.cost_price or 0
        try:
            product.sale_price = float(request.form.get('sale_price', product.sale_price) or product.sale_price or 0)
        except ValueError:
            product.sale_price = product.sale_price or 0
        product.currency = request.form.get('currency', product.currency or 'USD')
        db.session.commit()
        flash('Product updated successfully', 'success')
        return redirect(url_for('product_detail', id=id))
    
    categories = Category.query.all()
    return render_template('products/form.html', product=product, categories=categories)


@app.route('/products/<int:id>/price-update', methods=['POST'])
@login_required
@inventory_manager_required
def product_price_update(id):
    """API endpoint to update product prices (AJAX) - inventory manager only"""
    product = Product.query.get_or_404(id)
    data = request.get_json() or {}
    try:
        from utils import validate_price, log_price_change

        old_cost = product.cost_price or 0.0
        old_sale = product.sale_price or 0.0

        new_cost = validate_price(data.get('cost_price', old_cost))
        new_sale = validate_price(data.get('sale_price', old_sale))

        # Update product
        product.cost_price = new_cost
        product.sale_price = new_sale
        product.currency = data.get('currency', product.currency or 'USD')
        db.session.commit()

        # Log history
        log_price_change(current_user.id, product, old_cost, new_cost, old_sale, new_sale, reason=data.get('reason'))

        return jsonify({'success': True, 'cost_price': new_cost, 'sale_price': new_sale})
    except ValueError as e:
        return jsonify({'success': False, 'error': str(e)}), 400
    except Exception as e:
        return jsonify({'success': False, 'error': 'Failed to update price'}), 500


@app.route('/products/<int:id>/price-history')
@login_required
def product_price_history(id):
    """Show price history for a product"""
    product = Product.query.get_or_404(id)
    history = product and getattr(product, 'price_history', None)
    if history is None:
        # Query directly
        from models import PriceHistory
        history = PriceHistory.query.filter_by(product_id=id).order_by(PriceHistory.created_at.desc()).all()
    return render_template('products/price_history.html', product=product, history=history)

# ========== Receipts ==========

@app.route('/receipts')
@login_required
def receipts():
    """List receipts"""
    state = request.args.get('state', '')
    query = Receipt.query
    
    if state:
        query = query.filter_by(state=state)
    
    receipts_list = query.order_by(Receipt.created_at.desc()).all()
    return render_template('receipts/list.html', receipts=receipts_list, state=state)

@app.route('/receipts/create', methods=['GET', 'POST'])
@login_required
@warehouse_staff_or_manager
def receipt_create():
    """Create receipt"""
    if request.method == 'POST':
        receipt = Receipt(
            receipt_number=generate_sequence('REC', Receipt),
            date=datetime.strptime(request.form.get('date'), '%Y-%m-%dT%H:%M'),
            supplier_id=request.form.get('supplier_id', type=int) or None,
            warehouse_id=request.form.get('warehouse_id', type=int),
            location_id=request.form.get('location_id', type=int),
            notes=request.form.get('notes'),
            user_id=current_user.id,
            state='draft'
        )
        db.session.add(receipt)
        db.session.flush()
        
        # Add lines
        product_ids = request.form.getlist('product_id[]')
        quantities = request.form.getlist('quantity[]')
        
        for product_id, quantity in zip(product_ids, quantities):
            if product_id and quantity:
                line = ReceiptLine(
                    receipt_id=receipt.id,
                    product_id=int(product_id),
                    quantity=float(quantity)
                )
                db.session.add(line)
        
        db.session.commit()
        flash('Receipt created successfully', 'success')
        create_notification(current_user.id, 'Receipt Created', f'Receipt {receipt.receipt_number} has been created', 'operation_completed', 'receipt', receipt.id)
        return redirect(url_for('receipt_detail', id=receipt.id))
    
    warehouses = Warehouse.query.filter_by(active=True).all()
    suppliers = Partner.query.filter_by(type='supplier', active=True).all()
    products = Product.query.filter_by(active=True).all()
    return render_template('receipts/form.html', receipt=None, warehouses=warehouses, 
                         suppliers=suppliers, products=products)

@app.route('/receipts/<int:id>')
@login_required
def receipt_detail(id):
    """Receipt detail"""
    receipt = Receipt.query.get_or_404(id)
    return render_template('receipts/detail.html', receipt=receipt)

@app.route('/receipts/<int:id>/validate', methods=['POST'])
@login_required
@warehouse_staff_or_manager
def receipt_validate(id):
    """Validate receipt"""
    receipt = Receipt.query.get_or_404(id)
    
    if receipt.state != 'ready':
        flash('Receipt must be in Ready state', 'error')
        return redirect(url_for('receipt_detail', id=id))
    
    try:
        for line in receipt.lines:
            line.product.update_stock_location(receipt.location_id, line.quantity)
            
            # Log in ledger
            ledger = StockLedger(
                date=receipt.date,
                product_id=line.product_id,
                location_id=receipt.location_id,
                operation_type='receipt',
                reference=receipt.receipt_number,
                quantity_in=line.quantity,
                quantity_out=0.0,
                balance=line.product.get_stock_by_location(receipt.location_id),
                partner_id=receipt.supplier_id,
                user_id=current_user.id
            )
            db.session.add(ledger)
        
        receipt.state = 'done'
        db.session.commit()
        flash('Receipt validated successfully', 'success')
        notify_operation_completed(current_user.id, 'receipt', receipt.receipt_number, f'Quantity: {receipt.total_quantity}')
    except ValueError as e:
        flash(str(e), 'error')
    
    return redirect(url_for('receipt_detail', id=id))

@app.route('/receipts/<int:id>/state/<state>', methods=['POST'])
@login_required
def receipt_change_state(id, state):
    """Change receipt state"""
    receipt = Receipt.query.get_or_404(id)
    receipt.state = state
    db.session.commit()
    flash(f'Receipt state changed to {state}', 'success')
    return redirect(url_for('receipt_detail', id=id))

# ========== Deliveries ==========

@app.route('/deliveries')
@login_required
def deliveries():
    """List deliveries"""
    state = request.args.get('state', '')
    query = Delivery.query
    
    if state:
        query = query.filter_by(state=state)
    
    deliveries_list = query.order_by(Delivery.created_at.desc()).all()
    return render_template('deliveries/list.html', deliveries=deliveries_list, state=state)

@app.route('/deliveries/create', methods=['GET', 'POST'])
@login_required
@warehouse_staff_or_manager
def delivery_create():
    """Create delivery"""
    if request.method == 'POST':
        delivery = Delivery(
            delivery_number=generate_sequence('DEL', Delivery),
            date=datetime.strptime(request.form.get('date'), '%Y-%m-%dT%H:%M'),
            customer_id=request.form.get('customer_id', type=int) or None,
            warehouse_id=request.form.get('warehouse_id', type=int),
            location_id=request.form.get('location_id', type=int),
            notes=request.form.get('notes'),
            user_id=current_user.id,
            state='draft'
        )
        db.session.add(delivery)
        db.session.flush()
        
        # Add lines
        product_ids = request.form.getlist('product_id[]')
        quantities = request.form.getlist('quantity[]')
        
        for product_id, quantity in zip(product_ids, quantities):
            if product_id and quantity:
                line = DeliveryLine(
                    delivery_id=delivery.id,
                    product_id=int(product_id),
                    quantity=float(quantity)
                )
                db.session.add(line)
        
        db.session.commit()
        flash('Delivery created successfully', 'success')
        create_notification(current_user.id, 'Delivery Created', f'Delivery {delivery.delivery_number} has been created', 'operation_completed', 'delivery', delivery.id)
        return redirect(url_for('delivery_detail', id=delivery.id))
    
    warehouses = Warehouse.query.filter_by(active=True).all()
    customers = Partner.query.filter_by(type='customer', active=True).all()
    products = Product.query.filter_by(active=True).all()
    return render_template('deliveries/form.html', delivery=None, warehouses=warehouses, 
                         customers=customers, products=products)

@app.route('/deliveries/<int:id>')
@login_required
def delivery_detail(id):
    """Delivery detail"""
    delivery = Delivery.query.get_or_404(id)
    return render_template('deliveries/detail.html', delivery=delivery)

@app.route('/deliveries/<int:id>/validate', methods=['POST'])
@login_required
@warehouse_staff_or_manager
def delivery_validate(id):
    """Validate delivery"""
    delivery = Delivery.query.get_or_404(id)
    
    if delivery.state != 'ready':
        flash('Delivery must be in Ready state', 'error')
        return redirect(url_for('delivery_detail', id=id))
    
    try:
        for line in delivery.lines:
            # Check stock availability
            available = line.product.get_stock_by_location(delivery.location_id)
            if available < line.quantity:
                raise ValueError(f'Insufficient stock for {line.product.name}. Available: {available}, Required: {line.quantity}')
            
            # Decrease stock
            line.product.update_stock_location(delivery.location_id, -line.quantity)
            
            # Log in ledger
            ledger = StockLedger(
                date=delivery.date,
                product_id=line.product_id,
                location_id=delivery.location_id,
                operation_type='delivery',
                reference=delivery.delivery_number,
                quantity_in=0.0,
                quantity_out=line.quantity,
                balance=line.product.get_stock_by_location(delivery.location_id),
                partner_id=delivery.customer_id,
                user_id=current_user.id
            )
            db.session.add(ledger)
        
        delivery.state = 'done'
        db.session.commit()
        flash('Delivery validated successfully', 'success')
        notify_operation_completed(current_user.id, 'delivery', delivery.delivery_number, f'Quantity: {delivery.total_quantity}')
    except ValueError as e:
        flash(str(e), 'error')
    
    return redirect(url_for('delivery_detail', id=id))

@app.route('/deliveries/<int:id>/state/<state>', methods=['POST'])
@login_required
def delivery_change_state(id, state):
    """Change delivery state"""
    delivery = Delivery.query.get_or_404(id)
    delivery.state = state
    db.session.commit()
    flash(f'Delivery state changed to {state}', 'success')
    return redirect(url_for('delivery_detail', id=id))

# ========== Transfers ==========

@app.route('/transfers')
@login_required
def transfers():
    """List transfers"""
    state = request.args.get('state', '')
    query = Transfer.query
    
    if state:
        query = query.filter_by(state=state)
    
    transfers_list = query.order_by(Transfer.created_at.desc()).all()
    return render_template('transfers/list.html', transfers=transfers_list, state=state)

@app.route('/transfers/create', methods=['GET', 'POST'])
@login_required
@warehouse_staff_or_manager
def transfer_create():
    """Create transfer"""
    if request.method == 'POST':
        transfer = Transfer(
            transfer_number=generate_sequence('TRF', Transfer),
            date=datetime.strptime(request.form.get('date'), '%Y-%m-%dT%H:%M'),
            source_location_id=request.form.get('source_location_id', type=int),
            destination_location_id=request.form.get('destination_location_id', type=int),
            notes=request.form.get('notes'),
            user_id=current_user.id,
            state='draft'
        )
        db.session.add(transfer)
        db.session.flush()
        
        # Add lines
        product_ids = request.form.getlist('product_id[]')
        quantities = request.form.getlist('quantity[]')
        
        for product_id, quantity in zip(product_ids, quantities):
            if product_id and quantity:
                line = TransferLine(
                    transfer_id=transfer.id,
                    product_id=int(product_id),
                    quantity=float(quantity)
                )
                db.session.add(line)
        
        db.session.commit()
        flash('Transfer created successfully', 'success')
        create_notification(current_user.id, 'Transfer Created', f'Transfer {transfer.transfer_number} has been created', 'operation_completed', 'transfer', transfer.id)
        return redirect(url_for('transfer_detail', id=transfer.id))
    
    locations = Location.query.filter_by(active=True).all()
    products = Product.query.filter_by(active=True).all()
    return render_template('transfers/form.html', transfer=None, locations=locations, products=products)

@app.route('/transfers/<int:id>')
@login_required
def transfer_detail(id):
    """Transfer detail"""
    transfer = Transfer.query.get_or_404(id)
    return render_template('transfers/detail.html', transfer=transfer)

@app.route('/transfers/<int:id>/validate', methods=['POST'])
@login_required
@warehouse_staff_or_manager
def transfer_validate(id):
    """Validate transfer"""
    transfer = Transfer.query.get_or_404(id)
    
    if transfer.state != 'ready':
        flash('Transfer must be in Ready state', 'error')
        return redirect(url_for('transfer_detail', id=id))
    
    try:
        for line in transfer.lines:
            # Check stock availability
            available = line.product.get_stock_by_location(transfer.source_location_id)
            if available < line.quantity:
                raise ValueError(f'Insufficient stock for {line.product.name}. Available: {available}, Required: {line.quantity}')
            
            # Move stock
            line.product.update_stock_location(transfer.source_location_id, -line.quantity)
            line.product.update_stock_location(transfer.destination_location_id, line.quantity)
            
            # Log in ledger (source - out)
            ledger_out = StockLedger(
                date=transfer.date,
                product_id=line.product_id,
                location_id=transfer.source_location_id,
                operation_type='transfer_out',
                reference=transfer.transfer_number,
                quantity_in=0.0,
                quantity_out=line.quantity,
                balance=line.product.get_stock_by_location(transfer.source_location_id),
                user_id=current_user.id
            )
            db.session.add(ledger_out)
            
            # Log in ledger (destination - in)
            ledger_in = StockLedger(
                date=transfer.date,
                product_id=line.product_id,
                location_id=transfer.destination_location_id,
                operation_type='transfer_in',
                reference=transfer.transfer_number,
                quantity_in=line.quantity,
                quantity_out=0.0,
                balance=line.product.get_stock_by_location(transfer.destination_location_id),
                user_id=current_user.id
            )
            db.session.add(ledger_in)
        
        transfer.state = 'done'
        db.session.commit()
        flash('Transfer validated successfully', 'success')
        notify_operation_completed(current_user.id, 'transfer', transfer.transfer_number, f'Quantity: {transfer.total_quantity}')
    except ValueError as e:
        flash(str(e), 'error')
    
    return redirect(url_for('transfer_detail', id=id))

@app.route('/transfers/<int:id>/state/<state>', methods=['POST'])
@login_required
def transfer_change_state(id, state):
    """Change transfer state"""
    transfer = Transfer.query.get_or_404(id)
    transfer.state = state
    db.session.commit()
    flash(f'Transfer state changed to {state}', 'success')
    return redirect(url_for('transfer_detail', id=id))

# ========== Adjustments ==========

@app.route('/adjustments')
@login_required
def adjustments():
    """List adjustments"""
    adjustments_list = Adjustment.query.order_by(Adjustment.created_at.desc()).all()
    return render_template('adjustments/list.html', adjustments=adjustments_list)

@app.route('/adjustments/create', methods=['GET', 'POST'])
@login_required
@inventory_manager_required
def adjustment_create():
    """Create adjustment"""
    if request.method == 'POST':
        product_id = request.form.get('product_id', type=int)
        location_id = request.form.get('location_id', type=int)
        counted_qty = float(request.form.get('counted_qty', 0))
        
        product = Product.query.get(product_id)
        recorded_qty = product.get_stock_by_location(location_id)
        difference = counted_qty - recorded_qty
        
        adjustment = Adjustment(
            adjustment_number=generate_sequence('ADJ', Adjustment),
            date=datetime.strptime(request.form.get('date'), '%Y-%m-%dT%H:%M'),
            product_id=product_id,
            location_id=location_id,
            recorded_qty=recorded_qty,
            counted_qty=counted_qty,
            difference=difference,
            reason=request.form.get('reason'),
            user_id=current_user.id,
            state='draft'
        )
        db.session.add(adjustment)
        db.session.commit()
        flash('Adjustment created successfully', 'success')
        create_notification(current_user.id, 'Adjustment Created', f'Stock adjustment {adjustment.adjustment_number} has been created', 'system', 'adjustment', adjustment.id)
        return redirect(url_for('adjustment_detail', id=adjustment.id))
    
    products = Product.query.filter_by(active=True).all()
    locations = Location.query.filter_by(active=True).all()
    return render_template('adjustments/form.html', adjustment=None, products=products, locations=locations)

@app.route('/adjustments/<int:id>')
@login_required
def adjustment_detail(id):
    """Adjustment detail"""
    adjustment = Adjustment.query.get_or_404(id)
    return render_template('adjustments/detail.html', adjustment=adjustment)

@app.route('/adjustments/<int:id>/validate', methods=['POST'])
@login_required
@inventory_manager_required
def adjustment_validate(id):
    """Validate adjustment"""
    adjustment = Adjustment.query.get_or_404(id)
    
    if adjustment.state != 'draft':
        flash('Adjustment already validated', 'error')
        return redirect(url_for('adjustment_detail', id=id))
    
    try:
        # Update stock
        adjustment.product.update_stock_location(adjustment.location_id, adjustment.difference)
        
        # Log in ledger
        ledger = StockLedger(
            date=adjustment.date,
            product_id=adjustment.product_id,
            location_id=adjustment.location_id,
            operation_type='adjustment',
            reference=adjustment.adjustment_number,
            quantity_in=adjustment.difference if adjustment.difference > 0 else 0.0,
            quantity_out=abs(adjustment.difference) if adjustment.difference < 0 else 0.0,
            balance=adjustment.product.get_stock_by_location(adjustment.location_id),
            notes=adjustment.reason,
            user_id=current_user.id
        )
        db.session.add(ledger)
        
        adjustment.state = 'done'
        db.session.commit()
        flash('Adjustment validated successfully', 'success')
        notify_operation_completed(current_user.id, 'adjustment', adjustment.adjustment_number, f'Difference: {adjustment.difference}')
    except ValueError as e:
        flash(str(e), 'error')
    
    return redirect(url_for('adjustment_detail', id=id))

# ========== Stock Ledger ==========

@app.route('/ledger')
@login_required
def ledger():
    """Stock ledger"""
    product_id = request.args.get('product_id', type=int)
    location_id = request.args.get('location_id', type=int)
    operation_type = request.args.get('operation_type', '')
    
    query = StockLedger.query
    
    if product_id:
        query = query.filter_by(product_id=product_id)
    if location_id:
        query = query.filter_by(location_id=location_id)
    if operation_type:
        query = query.filter_by(operation_type=operation_type)
    
    entries = query.order_by(StockLedger.date.desc()).limit(100).all()
    products = Product.query.filter_by(active=True).all()
    locations = Location.query.filter_by(active=True).all()
    
    return render_template('ledger/list.html', entries=entries, products=products, 
                         locations=locations, product_id=product_id, location_id=location_id, 
                         operation_type=operation_type)

# ========== User Profile ==========

@app.route('/profile')
@login_required
def profile():
    """View user profile"""
    # Get user statistics
    receipts_count = Receipt.query.filter_by(user_id=current_user.id).count()
    deliveries_count = Delivery.query.filter_by(user_id=current_user.id).count()
    transfers_count = Transfer.query.filter_by(user_id=current_user.id).count()
    adjustments_count = Adjustment.query.filter_by(user_id=current_user.id).count()
    
    stats = {
        'receipts': receipts_count,
        'deliveries': deliveries_count,
        'transfers': transfers_count,
        'adjustments': adjustments_count,
    }
    
    return render_template('profile/view.html', user=current_user, stats=stats)

@app.route('/profile/edit', methods=['GET', 'POST'])
@login_required
def profile_edit():
    """Edit user profile"""
    if request.method == 'POST':
        current_user.name = request.form.get('name')
        current_user.email = request.form.get('email')
        db.session.commit()
        flash('Profile updated successfully', 'success')
        return redirect(url_for('profile'))
    
    return render_template('profile/edit.html', user=current_user)

@app.route('/profile/change-password', methods=['GET', 'POST'])
@login_required
def change_password():
    """Change password"""
    if request.method == 'POST':
        current_password = request.form.get('current_password')
        new_password = request.form.get('new_password')
        confirm_password = request.form.get('confirm_password')
        
        if not check_password_hash(current_user.password, current_password):
            flash('Current password is incorrect', 'error')
            return render_template('profile/change_password.html')
        
        if new_password != confirm_password:
            flash('New passwords do not match', 'error')
            return render_template('profile/change_password.html')
        
        current_user.password = generate_password_hash(new_password)
        db.session.commit()
        flash('Password changed successfully', 'success')
        return redirect(url_for('profile'))
    
    return render_template('profile/change_password.html')

# ========== Categories ==========

@app.route('/categories')
@login_required
@inventory_manager_required
def categories():
    """List categories"""
    categories_list = Category.query.all()
    return render_template('categories/list.html', categories=categories_list)

@app.route('/categories/create', methods=['GET', 'POST'])
@login_required
@inventory_manager_required
def category_create():
    """Create category"""
    if request.method == 'POST':
        category = Category(
            name=request.form.get('name'),
            description=request.form.get('description')
        )
        db.session.add(category)
        db.session.commit()
        flash('Category created successfully', 'success')
        return redirect(url_for('categories'))
    
    return render_template('categories/form.html', category=None)

@app.route('/categories/<int:id>/edit', methods=['GET', 'POST'])
@login_required
@inventory_manager_required
def category_edit(id):
    """Edit category"""
    category = Category.query.get_or_404(id)
    
    if request.method == 'POST':
        category.name = request.form.get('name')
        category.description = request.form.get('description')
        db.session.commit()
        flash('Category updated successfully', 'success')
        return redirect(url_for('categories'))
    
    return render_template('categories/form.html', category=category)

@app.route('/categories/<int:id>/delete', methods=['POST'])
@login_required
@inventory_manager_required
def category_delete(id):
    """Delete category"""
    category = Category.query.get_or_404(id)
    
    # Check if category is used by products
    if category.products:
        flash(f'Cannot delete category. It is used by {len(category.products)} product(s).', 'error')
        return redirect(url_for('categories'))
    
    db.session.delete(category)
    db.session.commit()
    flash('Category deleted successfully', 'success')
    return redirect(url_for('categories'))

# ========== Partners ==========

@app.route('/partners')
@login_required
@inventory_manager_required
def partners():
    """List partners"""
    partner_type = request.args.get('type', '')
    query = Partner.query
    
    if partner_type:
        query = query.filter_by(type=partner_type)
    
    partners_list = query.order_by(Partner.name).all()
    return render_template('partners/list.html', partners=partners_list, partner_type=partner_type)

@app.route('/partners/create', methods=['GET', 'POST'])
@login_required
@inventory_manager_required
def partner_create():
    """Create partner"""
    if request.method == 'POST':
        partner = Partner(
            name=request.form.get('name'),
            type=request.form.get('type'),
            email=request.form.get('email'),
            phone=request.form.get('phone'),
            address=request.form.get('address'),
            city=request.form.get('city'),
            state=request.form.get('state'),
            zip_code=request.form.get('zip_code'),
            country=request.form.get('country'),
        )
        db.session.add(partner)
        db.session.commit()
        flash('Partner created successfully', 'success')
        return redirect(url_for('partners'))
    
    return render_template('partners/form.html', partner=None)

@app.route('/partners/<int:id>')
@login_required
@inventory_manager_required
def partner_detail(id):
    """View partner details"""
    partner = Partner.query.get_or_404(id)
    receipts = Receipt.query.filter_by(supplier_id=id).limit(10).all() if partner.type == 'supplier' else []
    deliveries = Delivery.query.filter_by(customer_id=id).limit(10).all() if partner.type == 'customer' else []
    return render_template('partners/detail.html', partner=partner, receipts=receipts, deliveries=deliveries)

@app.route('/partners/<int:id>/edit', methods=['GET', 'POST'])
@login_required
@inventory_manager_required
def partner_edit(id):
    """Edit partner"""
    partner = Partner.query.get_or_404(id)
    
    if request.method == 'POST':
        partner.name = request.form.get('name')
        partner.type = request.form.get('type')
        partner.email = request.form.get('email')
        partner.phone = request.form.get('phone')
        partner.address = request.form.get('address')
        partner.city = request.form.get('city')
        partner.state = request.form.get('state')
        partner.zip_code = request.form.get('zip_code')
        partner.country = request.form.get('country')
        db.session.commit()
        flash('Partner updated successfully', 'success')
        return redirect(url_for('partner_detail', id=id))
    
    return render_template('partners/form.html', partner=partner)

@app.route('/partners/<int:id>/delete', methods=['POST'])
@login_required
@inventory_manager_required
def partner_delete(id):
    """Delete partner"""
    partner = Partner.query.get_or_404(id)
    
    # Check if partner is used in transactions
    if partner.receipts or partner.deliveries:
        flash('Cannot delete partner. It is used in transactions.', 'error')
        return redirect(url_for('partner_detail', id=id))
    
    db.session.delete(partner)
    db.session.commit()
    flash('Partner deleted successfully', 'success')
    return redirect(url_for('partners'))

# ========== Settings Dashboard ==========

@app.route('/settings')
@login_required
def settings():
    """Settings dashboard"""
    warehouses_count = Warehouse.query.filter_by(active=True).count()
    locations_count = Location.query.filter_by(active=True).count()
    categories_count = Category.query.count()
    partners_count = Partner.query.count()
    
    return render_template('settings/dashboard.html', 
                         warehouses_count=warehouses_count,
                         locations_count=locations_count,
                         categories_count=categories_count,
                         partners_count=partners_count,
                         is_inventory_manager=current_user.role == 'inventory_manager')

# ========== Warehouses & Locations ==========

@app.route('/warehouses')
@login_required
def warehouses():
    """List warehouses"""
    warehouses_list = Warehouse.query.filter_by(active=True).all()
    return render_template('warehouses/list.html', warehouses=warehouses_list)

@app.route('/warehouses/<int:id>')
@login_required
def warehouse_detail(id):
    """View warehouse details"""
    warehouse = Warehouse.query.get_or_404(id)
    locations = Location.query.filter_by(warehouse_id=id, active=True).all()
    return render_template('warehouses/detail.html', warehouse=warehouse, locations=locations)

@app.route('/warehouses/create', methods=['GET', 'POST'])
@login_required
@inventory_manager_required
def warehouse_create():
    """Create warehouse"""
    if request.method == 'POST':
        warehouse = Warehouse(
            name=request.form.get('name'),
            code=request.form.get('code'),
            address=request.form.get('address'),
            city=request.form.get('city'),
            state=request.form.get('state'),
            zip_code=request.form.get('zip_code'),
            country=request.form.get('country'),
            phone=request.form.get('phone'),
            email=request.form.get('email'),
        )
        db.session.add(warehouse)
        db.session.flush()
        
        # Create default location
        location = Location(
            name=f"{warehouse.name} - Main",
            warehouse_id=warehouse.id,
            code=f"{warehouse.code}-MAIN"
        )
        db.session.add(location)
        db.session.commit()
        
        flash('Warehouse created successfully', 'success')
        return redirect(url_for('warehouses'))
    
    return render_template('warehouses/form.html', warehouse=None)

@app.route('/warehouses/<int:id>/edit', methods=['GET', 'POST'])
@login_required
@inventory_manager_required
def warehouse_edit(id):
    """Edit warehouse"""
    warehouse = Warehouse.query.get_or_404(id)
    
    if request.method == 'POST':
        warehouse.name = request.form.get('name')
        warehouse.code = request.form.get('code')
        warehouse.address = request.form.get('address')
        warehouse.city = request.form.get('city')
        warehouse.state = request.form.get('state')
        warehouse.zip_code = request.form.get('zip_code')
        warehouse.country = request.form.get('country')
        warehouse.phone = request.form.get('phone')
        warehouse.email = request.form.get('email')
        db.session.commit()
        flash('Warehouse updated successfully', 'success')
        return redirect(url_for('warehouse_detail', id=id))
    
    return render_template('warehouses/form.html', warehouse=warehouse)

# ========== Locations ==========

@app.route('/warehouses/<int:warehouse_id>/locations')
@login_required
def warehouse_locations(warehouse_id):
    """List locations for a warehouse"""
    warehouse = Warehouse.query.get_or_404(warehouse_id)
    locations = Location.query.filter_by(warehouse_id=warehouse_id, active=True).all()
    return render_template('locations/list.html', warehouse=warehouse, locations=locations)

@app.route('/warehouses/<int:warehouse_id>/locations/create', methods=['GET', 'POST'])
@login_required
@inventory_manager_required
def location_create(warehouse_id):
    """Create location in warehouse"""
    warehouse = Warehouse.query.get_or_404(warehouse_id)
    
    if request.method == 'POST':
        location = Location(
            name=request.form.get('name'),
            warehouse_id=warehouse_id,
            code=request.form.get('code'),
            description=request.form.get('description')
        )
        db.session.add(location)
        db.session.commit()
        flash('Location created successfully', 'success')
        return redirect(url_for('warehouse_locations', warehouse_id=warehouse_id))
    
    return render_template('locations/form.html', warehouse=warehouse, location=None)

@app.route('/locations/<int:id>/edit', methods=['GET', 'POST'])
@login_required
@inventory_manager_required
def location_edit(id):
    """Edit location"""
    location = Location.query.get_or_404(id)
    
    if request.method == 'POST':
        location.name = request.form.get('name')
        location.code = request.form.get('code')
        location.description = request.form.get('description')
        db.session.commit()
        flash('Location updated successfully', 'success')
        return redirect(url_for('warehouse_locations', warehouse_id=location.warehouse_id))
    
    return render_template('locations/form.html', warehouse=location.warehouse, location=location)

@app.route('/locations/<int:id>/delete', methods=['POST'])
@login_required
@inventory_manager_required
def location_delete(id):
    """Delete location"""
    location = Location.query.get_or_404(id)
    warehouse_id = location.warehouse_id
    
    # Check if location has stock
    if location.product_locations:
        total_stock = sum(pl.quantity for pl in location.product_locations)
        if total_stock > 0:
            flash(f'Cannot delete location. It has {total_stock} units of stock.', 'error')
            return redirect(url_for('warehouse_locations', warehouse_id=warehouse_id))
    
    location.active = False
    db.session.commit()
    flash('Location deleted successfully', 'success')
    return redirect(url_for('warehouse_locations', warehouse_id=warehouse_id))

# ========== Notifications ==========

@app.route('/notifications')
@login_required
def notifications():
    """View all notifications"""
    page = request.args.get('page', 1, type=int)
    filter_type = request.args.get('filter', 'all')  # all, unread, read
    
    query = Notification.query.filter(
        Notification.user_id == current_user.id,
        (Notification.expires_at == None) | (Notification.expires_at > datetime.utcnow())
    )
    
    if filter_type == 'unread':
        query = query.filter(Notification.is_read == False)
    elif filter_type == 'read':
        query = query.filter(Notification.is_read == True)
    
    notifications_list = query.order_by(Notification.created_at.desc()).paginate(page=page, per_page=20)
    
    return render_template('notifications/list.html', notifications=notifications_list, filter_type=filter_type)

@app.route('/notifications/<int:id>')
@login_required
def notification_detail(id):
    """View notification detail"""
    notification = Notification.query.get_or_404(id)
    
    # Check ownership
    if notification.user_id != current_user.id:
        flash('Access denied', 'error')
        return redirect(url_for('notifications'))
    
    # Mark as read
    notification.mark_as_read()
    
    return render_template('notifications/detail.html', notification=notification)

@app.route('/notifications/<int:id>/read', methods=['POST'])
@login_required
def mark_notification_read(id):
    """Mark notification as read"""
    notification = Notification.query.get_or_404(id)
    
    if notification.user_id != current_user.id:
        return jsonify({'error': 'Access denied'}), 403
    
    notification.mark_as_read()
    return jsonify({'success': True})

@app.route('/notifications/<int:id>/delete', methods=['POST'])
@login_required
def delete_notification(id):
    """Delete a notification"""
    notification = Notification.query.get_or_404(id)
    
    if notification.user_id != current_user.id:
        return jsonify({'error': 'Access denied'}), 403
    
    db.session.delete(notification)
    db.session.commit()
    
    return jsonify({'success': True})

@app.route('/notifications/read-all', methods=['POST'])
@login_required
def mark_all_notifications_read():
    """Mark all notifications as read"""
    Notification.query.filter(
        Notification.user_id == current_user.id,
        Notification.is_read == False,
        (Notification.expires_at == None) | (Notification.expires_at > datetime.utcnow())
    ).update({'is_read': True, 'read_at': datetime.utcnow()})
    
    db.session.commit()
    return jsonify({'success': True})

@app.route('/api/notifications/unread-count')
@login_required
def api_unread_notifications_count():
    """Get unread notifications count (for navbar)"""
    count = get_user_unread_notifications_count(current_user.id)
    return jsonify({'count': count})

@app.route('/api/notifications/recent')
@login_required
def api_recent_notifications():
    """Get recent notifications (for dropdown)"""
    notifications_list = get_user_notifications(current_user.id, limit=5, unread_only=False)
    
    data = [{
        'id': n.id,
        'title': n.title,
        'message': n.message,
        'type': n.notification_type,
        'is_read': n.is_read,
        'created_at': n.created_at.strftime('%Y-%m-%d %H:%M'),
        'url': url_for('notification_detail', id=n.id)
    } for n in notifications_list]
    
    return jsonify({'notifications': data})

@app.route('/notifications-preferences', methods=['GET', 'POST'])
@login_required
def notification_preferences():
    """Manage notification preferences"""
    prefs = NotificationPreference.query.filter_by(user_id=current_user.id).first()
    
    if not prefs:
        prefs = NotificationPreference(user_id=current_user.id)
        db.session.add(prefs)
        db.session.commit()
    
    if request.method == 'POST':
        prefs.enable_low_stock_alerts = request.form.get('enable_low_stock_alerts') == 'on'
        prefs.enable_operation_alerts = request.form.get('enable_operation_alerts') == 'on'
        prefs.enable_system_alerts = request.form.get('enable_system_alerts') == 'on'
        prefs.enable_email_notifications = request.form.get('enable_email_notifications') == 'on'
        prefs.low_stock_threshold = float(request.form.get('low_stock_threshold', 0.3))
        prefs.updated_at = datetime.utcnow()
        db.session.commit()
        flash('Notification preferences updated successfully', 'success')
        return redirect(url_for('notification_preferences'))
    
    return render_template('notifications/preferences.html', preferences=prefs)

# ========== API Routes ==========

@app.route('/api/locations/<int:warehouse_id>')
@login_required
def api_locations(warehouse_id):
    """Get locations for a warehouse"""
    locations = Location.query.filter_by(warehouse_id=warehouse_id, active=True).all()
    return jsonify([{'id': loc.id, 'name': loc.name} for loc in locations])

@app.route('/api/product-stock/<int:product_id>/<int:location_id>')
@login_required
def api_product_stock(product_id, location_id):
    """Get product stock for a location"""
    product = Product.query.get_or_404(product_id)
    stock = product.get_stock_by_location(location_id)
    return jsonify({'stock': stock})

