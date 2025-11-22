# StockMaster Project Structure

```
stockmaster-odoo/
├── app.py                      # Flask application entry point
├── models.py                   # Flask SQLAlchemy database models
├── routes.py                   # Flask route handlers (53 routes)
├── utils.py                    # Utility functions and decorators
├── requirements.txt            # Python dependencies
├── .env                        # Environment configuration (not in git)
├── .gitignore                  # Git ignore rules
├── README.md                   # Main project documentation
│
├── docs/                       # Documentation
│   ├── QUICK_START.md          # Quick start guide
│
├── migrations/                 # Database migrations and seed scripts
│   ├── __init__.py
│   ├── migrate_add_pricing.py  # Schema migration: add pricing columns
│   ├── seed_inr_data.py        # Seed realistic INR product data
│   ├── seed_sales_data.py      # Seed customer and delivery records
│   └── run_db_check.py         # Quick database verification script
│
├── static/                     # Flask static assets
│   ├── stockmaster-ui.css      # Main stylesheet
│   └── stockmaster-ui.js       # Frontend JavaScript
│
├── templates/                  # Jinja2 HTML templates
│   ├── base.html               # Base template (navigation, layout)
│   ├── login.html              # Login page
│   ├── signup.html             # Signup page
│   ├── dashboard.html          # Dashboard/KPI page
│   ├── settings/               # Settings templates
│   ├── profile/                # User profile templates
│   ├── products/               # Product templates
│   │   ├── list.html
│   │   ├── form.html
│   │   ├── detail.html
│   │   └── price_history.html  # Price change history
│   ├── receipts/               # Receipt (inbound stock) templates
│   ├── deliveries/             # Delivery (outbound stock) templates
│   ├── transfers/              # Transfer (internal move) templates
│   ├── adjustments/            # Stock adjustment templates
│   ├── warehouses/             # Warehouse management templates
│   ├── locations/              # Location templates
│   ├── categories/             # Category templates
│   ├── partners/               # Supplier/customer templates
│   ├── ledger/                 # Stock ledger templates
│   ├── notifications/          # Notification templates
│   │   ├── list.html
│   │   ├── detail.html
│   │   ├── preferences.html
│   └── email/                  # Email templates (OTP, notifications)
│
├── stockmaster/                # Odoo module
│   ├── __init__.py
│   ├── __manifest__.py         # Odoo module manifest
│   ├── README.md
│   ├── models/
│   │   ├── __init__.py
│   │   ├── product.py          # StockMaster product model (with pricing)
│   │   ├── ...                 # (Other Odoo models)
│   ├── views/                  # Odoo XML views
│   │   ├── product_views.xml   # Product views with pricing fields
│   │   └── ...
│   ├── security/               # Access control rules
│   └── data/                   # Demo data and sequences
│
└── .git/                       # Git repository (not included in listings)
```

## Key Features

### Inventory Management
- Product management with SKU tracking
- Multi-location stock tracking
- Real-time inventory ledger
- Low stock alerts

### Operations
- Receipts (inbound goods) → Draft → Waiting → Ready → Done
- Deliveries (outbound goods) → Draft → Picking → Packing → Ready → Done
- Transfers (internal stock moves)
- Adjustments (physical count reconciliation)

### Pricing (NEW)
- Cost price and sale price per product
- Currency support (default: INR)
- Price history tracking
- Quick inline price updates (admin only)

### User Management
- Role-based access (inventory_manager, warehouse_staff)
- Profile management
- Password reset via OTP
- Session management

### Notifications
- Real-time alerts (low stock, operations, system)
- User preferences
- Auto-expiring notifications
- Email integration

### Reporting & Analytics
- KPI dashboard
- Stock ledger with filtering
- Recent activities
- Price history audit trail

## File Organization

### Core Application Files
- `app.py` – Flask app initialization, database setup
- `models.py` – SQLAlchemy ORM models (10+ tables)
- `routes.py` – 53 Flask routes covering all operations
- `utils.py` – Helper functions, decorators, notification logic

### Configuration
- `.env` – Secrets (DATABASE_URL, email, keys) — **not in git**
- `.gitignore` – Standard Python/Flask ignores
- `requirements.txt` – Pinned Python dependencies

### Documentation
- `README.md` – Complete project guide (installation, config, API reference)
- `docs/QUICK_START.md` – Quick reference for common tasks
- `STRUCTURE.md` – This file

### Database & Migrations
- `migrations/migrate_add_pricing.py` – Schema: add cost_price, sale_price, currency columns
- `migrations/seed_inr_data.py` – Realistic product, category, warehouse, supplier data
- `migrations/seed_sales_data.py` – Sample customers and delivery transactions
- `migrations/run_db_check.py` – Verify schema and data

### Frontend
- `static/stockmaster-ui.css` – Responsive styling (1000+ lines)
- `static/stockmaster-ui.js` – Notifications, dropdowns, interactions
- `templates/base.html` – Navigation bar, notifications bell, auth
- `templates/*/` – Feature-specific templates (30+ files)

### Odoo Module (Optional)
- `stockmaster/` – Standalone Odoo app for ERP integration
- Mirrors Flask models in Odoo ORM
- XML views for Odoo UI

## Database Schema

### Core Tables
- `users` – User accounts with roles
- `categories` – Product categories
- `products` – Product master with pricing (cost_price, sale_price, currency)
- `warehouses` – Warehouse locations
- `locations` – Bins/sections within warehouses
- `product_locations` – Stock by location (junction table)
- `partners` – Suppliers and customers

### Operations
- `receipts`, `receipt_lines` – Inbound goods
- `deliveries`, `delivery_lines` – Outbound goods
- `transfers`, `transfer_lines` – Internal transfers
- `adjustments` – Physical count adjustments

### Audit & Notifications
- `stock_ledger` – Complete audit trail of all stock movements
- `notifications` – User alerts and messages
- `notification_preferences` – Per-user notification settings
- `price_history` – Record of all pricing changes

## Getting Started

### First Run
```bash
# 1. Clone & setup
git clone <repo>
cd stockmaster-odoo
python -m venv venv
source venv/bin/activate  # or venv\Scripts\activate on Windows
pip install -r requirements.txt

# 2. Configure
cp .env.example .env
# Edit .env with your DATABASE_URL, email settings, SECRET_KEY

# 3. Initialize database
python app.py
# This will create tables and default admin user

# 4. Run migrations (if needed)
python migrations/migrate_add_pricing.py
python migrations/seed_inr_data.py
python migrations/seed_sales_data.py

# 5. Run app
python app.py
# Visit http://localhost:5000
```

### Default Credentials
- Email: admin@stockmaster.com
- Password: admin123
- Role: inventory_manager

## Development

### Adding a New Feature
1. Create model in `models.py`
2. Add route handler in `routes.py`
3. Create template(s) in `templates/<feature>/`
4. Add CSS to `static/stockmaster-ui.css` if needed
5. Add utility functions to `utils.py` if needed
6. Test locally, then commit

### Database Changes
1. Edit model in `models.py`
2. Create migration script in `migrations/` (example: `migrate_add_*.py`)
3. Run migration: `python migrations/migrate_add_*.py`
4. Test with `migrations/run_db_check.py`
5. Commit both code and migration

### Deployment
- Use production WSGI server (Gunicorn)
- Set environment variables (no .env file in production)
- Run database migrations before starting
- Use reverse proxy (Nginx) with SSL
- Regular database backups

## Common Tasks

| Task | Command |
|------|---------|
| Check DB | `python migrations/run_db_check.py` |
| Seed data | `python migrations/seed_inr_data.py` |
| Seed sales | `python migrations/seed_sales_data.py` |
| Run app | `python app.py` |
| Reset DB | Drop tables in PostgreSQL and rerun `python app.py` |

---

**Last Updated:** November 22, 2025  
**Version:** 1.0 + Pricing + INR
