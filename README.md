# 📦 StockMaster - Inventory Management System

<div align="center">

![StockMaster Logo](static/stockmaster-ui.js)

**A comprehensive, full-featured inventory management system built with Flask and PostgreSQL**

[![Python](https://img.shields.io/badge/Python-3.8%2B-blue)](https://www.python.org/)
[![Flask](https://img.shields.io/badge/Flask-2.3.3-green)](https://flask.palletsprojects.com/)
[![PostgreSQL](https://img.shields.io/badge/PostgreSQL-Latest-336791)](https://www.postgresql.org/)
[![License](https://img.shields.io/badge/License-MIT-yellow)](LICENSE)
[![Status](https://img.shields.io/badge/Status-Production%20Ready-brightgreen)]()

[Features](#-features) • [Quick Start](#-quick-start) • [Installation](#-installation) • [Documentation](#-documentation) • [Support](#-support)

</div>

---

## 🎯 Overview

**StockMaster** is a modern, user-friendly inventory management system designed for businesses of all sizes. It provides real-time stock tracking, automated notifications, comprehensive reporting, and role-based access control.

Perfect for:
- ✅ Warehouse management
- ✅ Inventory tracking
- ✅ Supply chain operations
- ✅ Stock audits and adjustments
- ✅ Multi-location inventory

---

## ✨ Features

### 📊 Core Inventory Management
- **Product Management** - Create and manage products with SKUs, categories, and stock levels
- **Pricing Management** - Set and manage product cost and sale prices, supports currency and sync with Odoo product prices
- **Warehouse Management** - Organize inventory across multiple warehouses and locations
- **Real-time Stock Tracking** - Monitor stock levels across all locations
- **Stock Ledger** - Complete audit trail of all inventory movements
- **Low Stock Alerts** - Automatic notifications when inventory falls below minimum levels

### 📦 Operations
- **Receipts** - Track incoming stock from suppliers with full workflow (Draft → Waiting → Ready → Done)
- **Deliveries** - Manage outgoing shipments to customers (Draft → Picking → Packing → Ready → Done)
- **Transfers** - Move stock between locations or warehouses
- **Adjustments** - Record physical inventory counts and reconcile with system

### 👥 User Management & Security
- **Role-Based Access Control** - Two-tier system (Inventory Manager & Warehouse Staff)
- **User Authentication** - Secure login with password hashing
- **Profile Management** - Users can edit profile and change password
- **Session Management** - Automatic session handling with Flask-Login
- **OTP-Based Password Reset** - Secure password recovery via email

### 🔔 Notification System
- **Real-time Notifications** - Instant alerts for important events
- **Multiple Notification Types** - Low stock, operation completed, system alerts
- **User Preferences** - Customize which notifications you receive
- **Unread Badge** - Quick indicator of pending notifications
- **Auto-expiring** - Notifications automatically cleaned up after 30 days

### 📈 Reporting & Analytics
- **KPI Dashboard** - View key metrics at a glance (Total products, low stock items, pending operations)
- **Recent Activities** - Track recent receipts, deliveries, and low stock items
- **Movement History** - Complete record of all stock movements with filtering and search
- **Product Reports** - Stock levels, reorder quantities, categories

### 🔍 Search & Filtering
- **Global Search** - Find products, suppliers, customers across the system
- **Advanced Filters** - Filter by category, warehouse, location, status, date range
- **Quick Actions** - Bulk operations and quick status changes

### 🎨 User Interface
- **Responsive Design** - Works on desktop, tablet, and mobile
- **Intuitive Navigation** - Clean, organized menu structure
- **Dark/Light Mode Ready** - Professional color scheme
- **Real-time Updates** - Auto-refresh notifications and stock levels
- **Smooth Animations** - Professional transitions and interactions

### ⚡ Performance & Scalability
- **Database Indexing** - Optimized queries for fast performance
- **Pagination** - Handle large datasets efficiently
- **Caching Ready** - Foundation for caching implementations
- **Auto-cleanup** - Removes expired data automatically

---

## 🚀 Quick Start

### Prerequisites
- Python 3.8 or higher
- PostgreSQL 11 or higher
- Git

### Installation

1. **Clone the repository**
```bash
git clone https://github.com/yourusername/stockmaster.git
cd stockmaster
```

2. **Create virtual environment**
```bash
python -m venv venv

# On Windows
venv\Scripts\activate

# On macOS/Linux
source venv/bin/activate
```

3. **Install dependencies**
```bash
pip install -r requirements.txt
```

4. **Configure database**
```bash
# Update app.py with your PostgreSQL credentials
# Edit the DATABASE_URL connection string
```

5. **Initialize database**
```bash
python app.py
# This will create tables and default admin user
```

6. **Run the application**
```bash
python app.py
```

7. **Access the application**
```
Open http://localhost:5000 in your browser
```

### Default Credentials
```
Email: admin@stockmaster.com
Password: admin123
```

⚠️ **IMPORTANT**: Change these credentials in production!

---

## 📋 Installation Guide

### Windows Installation

```bash
# 1. Clone repository
git clone https://github.com/yourusername/stockmaster.git
cd stockmaster

# 2. Create virtual environment
python -m venv venv
venv\Scripts\activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Set environment variables
set FLASK_APP=app.py
set FLASK_ENV=development
set SECRET_KEY=your-secret-key-here
set MAIL_USERNAME=your-email@gmail.com
set MAIL_PASSWORD=your-app-password

# 5. Run application
python app.py
```

### macOS/Linux Installation

```bash
# 1. Clone repository
git clone https://github.com/yourusername/stockmaster.git
cd stockmaster

# 2. Create virtual environment
python3 -m venv venv
source venv/bin/activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Set environment variables
export FLASK_APP=app.py
export FLASK_ENV=development
export SECRET_KEY=your-secret-key-here
export MAIL_USERNAME=your-email@gmail.com
export MAIL_PASSWORD=your-app-password

# 5. Run application
python app.py
```

### Docker Installation (Optional)

```bash
# Build image
docker build -t stockmaster .

# Run container
docker run -p 5000:5000 \
  -e DATABASE_URL=postgresql://user:password@db:5432/stockmaster \
  stockmaster
```

---

## 🔧 Configuration

### Environment Variables

Create a `.env` file in the project root:

```env
# Database
DATABASE_URL=postgresql://postgres:password@localhost:5432/stockmaster

# Flask
SECRET_KEY=your-very-secret-key-change-this
FLASK_ENV=production

# Email Configuration (for notifications)
MAIL_SERVER=smtp.gmail.com
MAIL_PORT=587
MAIL_USE_TLS=true
MAIL_USERNAME=your-email@gmail.com
MAIL_PASSWORD=your-app-password
MAIL_DEFAULT_SENDER=noreply@stockmaster.com

# AWS S3 (optional, for file uploads)
AWS_ACCESS_KEY_ID=your-access-key
AWS_SECRET_ACCESS_KEY=your-secret-key
AWS_S3_BUCKET=your-bucket-name
```

### Database Setup

```bash
# Using PostgreSQL
createdb stockmaster
psql stockmaster < schema.sql

# Or let the app create tables automatically
python app.py
```

---

## 📚 Documentation

### Main Documents

| Document | Description |
|----------|-------------|
| [QUICK_START.md](QUICK_START.md) | Quick reference guide and testing workflow |
| [NOTIFICATION_FEATURE.md](NOTIFICATION_FEATURE.md) | Complete notification system documentation |
| [NOTIFICATION_QUICK_START.md](NOTIFICATION_QUICK_START.md) | Notification feature quick reference |
| [NOTIFICATION_VISUAL_GUIDE.md](NOTIFICATION_VISUAL_GUIDE.md) | UI/UX design of notification system |
| [NOTIFICATION_LAUNCH_CHECKLIST.md](NOTIFICATION_LAUNCH_CHECKLIST.md) | Pre-launch verification checklist |

---

## 🗺️ Project Structure

```
stockmaster/
├── app.py                      # Main Flask application
├── models.py                   # Database models
├── routes.py                   # Application routes (53 routes)
├── utils.py                    # Utility functions
├── requirements.txt            # Python dependencies
├── .env                        # Environment variables (not in repo)
├── .gitignore                  # Git ignore rules
│
├── static/
│   ├── stockmaster-ui.css      # Main stylesheet
│   └── stockmaster-ui.js       # Frontend JavaScript
│
├── templates/
│   ├── base.html               # Base template with navigation
│   ├── login.html              # Login page
│   ├── signup.html             # Signup page
│   ├── dashboard.html          # Dashboard KPIs
│   ├── products/
│   │   ├── list.html           # Product list
│   │   ├── form.html           # Product form
│   │   └── detail.html         # Product detail
│   ├── receipts/
│   │   ├── list.html           # Receipt list
│   │   ├── form.html           # Receipt form
│   │   └── detail.html         # Receipt detail
│   ├── deliveries/
│   │   ├── list.html           # Delivery list
│   │   ├── form.html           # Delivery form
│   │   └── detail.html         # Delivery detail
│   ├── transfers/              # Transfer templates
│   ├── adjustments/            # Adjustment templates
│   ├── warehouses/             # Warehouse templates
│   ├── categories/             # Category templates
│   ├── partners/               # Partner templates
│   ├── notifications/          # Notification templates
│   ├── ledger/                 # Stock ledger templates
│   └── profile/                # User profile templates
│
└── stockmaster/ (Odoo Module)
    ├── __manifest__.py         # Module manifest
    ├── models/                 # Odoo models
    ├── views/                  # Odoo views
    ├── security/               # Security rules
    └── data/                   # Demo data
```

---

## 🔐 User Roles

### Inventory Manager
- ✅ Create/edit/delete categories
- ✅ Create/edit/delete suppliers and customers
- ✅ Create/edit/delete warehouses and locations
- ✅ Perform stock adjustments
- ✅ View all reports and analytics
- ✅ Manage user profiles

### Warehouse Staff
- ✅ Create receipts and deliveries
- ✅ Update receipt/delivery status
- ✅ View stock levels
- ✅ View stock history
- ✅ Manage own profile
- ❌ Cannot manage categories, suppliers, or warehouses

---

## 📊 Database Schema

### Core Tables

```sql
-- Users
CREATE TABLE users (
  id SERIAL PRIMARY KEY,
  name VARCHAR(100),
  email VARCHAR(100) UNIQUE,
  password VARCHAR(255),
  role VARCHAR(20),
  created_at TIMESTAMP
);

-- Warehouses
CREATE TABLE warehouses (
  id SERIAL PRIMARY KEY,
  name VARCHAR(100),
  code VARCHAR(20) UNIQUE,
  address TEXT,
  active BOOLEAN
);

-- Locations (within warehouses)
CREATE TABLE locations (
  id SERIAL PRIMARY KEY,
  warehouse_id INTEGER REFERENCES warehouses,
  name VARCHAR(100),
  code VARCHAR(20),
  active BOOLEAN
);

-- Products
CREATE TABLE products (
  id SERIAL PRIMARY KEY,
  name VARCHAR(200),
  sku VARCHAR(50) UNIQUE,
  category_id INTEGER,
  min_stock FLOAT,
  max_stock FLOAT,
  active BOOLEAN
);

-- Stock by Location
CREATE TABLE product_locations (
  id SERIAL PRIMARY KEY,
  product_id INTEGER REFERENCES products,
  location_id INTEGER REFERENCES locations,
  quantity FLOAT,
  UNIQUE(product_id, location_id)
);

-- Stock Ledger (Audit Trail)
CREATE TABLE stock_ledger (
  id SERIAL PRIMARY KEY,
  date TIMESTAMP,
  product_id INTEGER REFERENCES products,
  location_id INTEGER REFERENCES locations,
  operation_type VARCHAR(20),
  quantity_in FLOAT,
  quantity_out FLOAT,
  balance FLOAT,
  reference VARCHAR(50)
);

-- Notifications
CREATE TABLE notifications (
  id SERIAL PRIMARY KEY,
  user_id INTEGER REFERENCES users,
  title VARCHAR(200),
  message TEXT,
  notification_type VARCHAR(50),
  is_read BOOLEAN,
  created_at TIMESTAMP,
  expires_at TIMESTAMP
);
```

---

## 🚀 API Routes

### Authentication
| Method | Route | Description |
|--------|-------|-------------|
| GET | `/` | Landing page |
| GET | `/login` | Login form |
| POST | `/login` | Process login |
| GET | `/signup` | Signup form |
| POST | `/signup` | Create new user |
| GET | `/logout` | Logout user |
| GET | `/forgot-password` | Password reset form |
| POST | `/forgot-password` | Send OTP |
| GET | `/reset-password` | Reset password form |
| POST | `/reset-password` | Process password reset |

### Dashboard & Navigation
| Method | Route | Description |
|--------|-------|-------------|
| GET | `/dashboard` | Main dashboard |
| GET | `/settings` | Settings dashboard |

### Products
| Method | Route | Description |
|--------|-------|-------------|
| GET | `/products` | Product list |
| GET | `/products/create` | Create product form |
| POST | `/products/create` | Create product |
| GET | `/products/<id>` | Product detail |
| GET | `/products/<id>/edit` | Edit product form |
| POST | `/products/<id>/edit` | Update product |

### Receipts
| Method | Route | Description |
|--------|-------|-------------|
| GET | `/receipts` | Receipt list |
| GET | `/receipts/create` | Create receipt form |
| POST | `/receipts/create` | Create receipt |
| GET | `/receipts/<id>` | Receipt detail |
| POST | `/receipts/<id>/validate` | Validate receipt |
| POST | `/receipts/<id>/state/<state>` | Change state |

### Deliveries
| Method | Route | Description |
|--------|-------|-------------|
| GET | `/deliveries` | Delivery list |
| GET | `/deliveries/create` | Create delivery form |
| POST | `/deliveries/create` | Create delivery |
| GET | `/deliveries/<id>` | Delivery detail |
| POST | `/deliveries/<id>/validate` | Validate delivery |

### Transfers
| Method | Route | Description |
|--------|-------|-------------|
| GET | `/transfers` | Transfer list |
| GET | `/transfers/create` | Create transfer form |
| POST | `/transfers/create` | Create transfer |
| GET | `/transfers/<id>` | Transfer detail |
| POST | `/transfers/<id>/validate` | Validate transfer |

### Adjustments
| Method | Route | Description |
|--------|-------|-------------|
| GET | `/adjustments` | Adjustment list |
| GET | `/adjustments/create` | Create adjustment form |
| POST | `/adjustments/create` | Create adjustment |
| GET | `/adjustments/<id>` | Adjustment detail |
| POST | `/adjustments/<id>/validate` | Validate adjustment |

### Notifications
| Method | Route | Description |
|--------|-------|-------------|
| GET | `/notifications` | Notifications center |
| GET | `/notifications/<id>` | Notification detail |
| POST | `/notifications/<id>/read` | Mark as read |
| POST | `/notifications/<id>/delete` | Delete notification |
| POST | `/notifications/read-all` | Mark all as read |
| GET/POST | `/notifications-preferences` | Manage preferences |

### Stock Ledger
| Method | Route | Description |
|--------|-------|-------------|
| GET | `/ledger` | Stock ledger/history |

### Warehouses & Locations
| Method | Route | Description |
|--------|-------|-------------|
| GET | `/warehouses` | Warehouse list |
| GET | `/warehouses/<id>` | Warehouse detail |
| GET | `/warehouses/create` | Create warehouse form |
| POST | `/warehouses/create` | Create warehouse |
| GET | `/warehouses/<id>/edit` | Edit warehouse form |
| POST | `/warehouses/<id>/edit` | Update warehouse |
| GET | `/warehouses/<id>/locations` | Location list |
| GET | `/warehouses/<id>/locations/create` | Create location form |
| POST | `/warehouses/<id>/locations/create` | Create location |
| GET | `/locations/<id>/edit` | Edit location form |
| POST | `/locations/<id>/edit` | Update location |
| POST | `/locations/<id>/delete` | Delete location |

### Categories & Partners
| Method | Route | Description |
|--------|-------|-------------|
| GET | `/categories` | Category list |
| GET | `/categories/create` | Create category form |
| POST | `/categories/create` | Create category |
| GET | `/categories/<id>/edit` | Edit category form |
| POST | `/categories/<id>/edit` | Update category |
| POST | `/categories/<id>/delete` | Delete category |
| GET | `/partners` | Partner list |
| GET | `/partners/create` | Create partner form |
| POST | `/partners/create` | Create partner |
| GET | `/partners/<id>` | Partner detail |
| GET | `/partners/<id>/edit` | Edit partner form |
| POST | `/partners/<id>/edit` | Update partner |
| POST | `/partners/<id>/delete` | Delete partner |

### User Profile
| Method | Route | Description |
|--------|-------|-------------|
| GET | `/profile` | View profile |
| GET | `/profile/edit` | Edit profile form |
| POST | `/profile/edit` | Update profile |
| GET | `/profile/change-password` | Change password form |
| POST | `/profile/change-password` | Process password change |

### API Endpoints
| Method | Route | Description |
|--------|-------|-------------|
| GET | `/api/locations/<id>` | Get locations (JSON) |
| GET | `/api/product-stock/<product_id>/<location_id>` | Get stock (JSON) |
| GET | `/api/notifications/unread-count` | Get unread count (JSON) |
| GET | `/api/notifications/recent` | Get recent notifications (JSON) |

---

## 🔄 Workflow Examples

### Complete a Receipt

```
1. Navigate to Operations → Receipts
2. Click "NEW" to create receipt
3. Select supplier
4. Add products and quantities
5. Click "Save"
6. View receipt details
7. Change status: Draft → Waiting
8. Change status: Waiting → Ready
9. Click "Validate" to confirm receipt
10. Status changes to: Done
11. Stock updated automatically
```

### Transfer Stock Between Locations

```
1. Navigate to Operations → Transfers
2. Click "NEW" to create transfer
3. Select source location
4. Select destination location
5. Add products and quantities
6. Click "Save"
7. View transfer details
8. Change status: Draft → Waiting
9. Change status: Waiting → Ready
10. Click "Validate" to confirm transfer
11. Status changes to: Done
12. Stock moved automatically
```

### Adjust Physical Inventory

```
1. Navigate to Operations → Adjustments
2. Click "NEW" to create adjustment
3. Select product
4. Select location
5. Enter counted quantity
6. Select reason
7. Click "Save"
8. View adjustment details
9. Click "Validate"
10. Difference recorded in ledger
11. Stock updated to counted quantity
```

---

## 🧪 Testing

### Manual Testing Checklist

- [ ] Create user account
- [ ] Login/logout
- [ ] Change password
- [ ] Create product
- [ ] Create warehouse
- [ ] Create location
- [ ] Create supplier/customer
- [ ] Create receipt (from Draft to Done)
- [ ] Create delivery (from Draft to Done)
- [ ] Create transfer (from Draft to Done)
- [ ] Create adjustment
- [ ] View stock ledger
- [ ] Check notifications
- [ ] Update notification preferences
- [ ] View dashboard KPIs

### Running Tests

```bash
# Unit tests (if available)
pytest tests/

# Coverage report
pytest --cov=. tests/

# Integration tests
python -m unittest discover
```

---

## 📈 Performance Optimization

### Database Optimization
```sql
-- Create indexes for frequently queried columns
CREATE INDEX idx_product_sku ON products(sku);
CREATE INDEX idx_stock_ledger_date ON stock_ledger(date);
CREATE INDEX idx_notifications_user ON notifications(user_id);
CREATE INDEX idx_product_location ON product_locations(product_id, location_id);
```

### Caching Strategy
- Cache product listings (5 minutes)
- Cache warehouse data (10 minutes)
- Cache user permissions (session)
- No caching for real-time stock

### Query Optimization
- Use pagination (20 items per page)
- Use select_related() for foreign keys
- Use prefetch_related() for reverse relations
- Add database indexes

---

## 🐛 Troubleshooting

### Common Issues

**Issue: "Database connection failed"**
```
Solution: Check DATABASE_URL in .env file and ensure PostgreSQL is running
```

**Issue: "ModuleNotFoundError"**
```
Solution: Run 'pip install -r requirements.txt' to install dependencies
```

**Issue: "Access Denied on Settings"**
```
Solution: Login as admin (Inventory Manager role required)
```

**Issue: "Notifications not appearing"**
```
Solution: Check notification preferences are enabled in /notifications-preferences
```

**Issue: "Slow performance"**
```
Solution: 
1. Check database indexes are created
2. Clear browser cache
3. Check server logs for slow queries
```

---

## 🔐 Security Best Practices

- ✅ Change default admin password immediately
- ✅ Use strong SECRET_KEY in production
- ✅ Enable HTTPS in production
- ✅ Keep dependencies updated
- ✅ Use environment variables for sensitive data
- ✅ Enable CSRF protection
- ✅ Implement rate limiting
- ✅ Regular security audits
- ✅ Keep backups of database

### Production Deployment

```bash
# 1. Set production settings
export FLASK_ENV=production
export SECRET_KEY=$(python -c 'import secrets; print(secrets.token_hex(32))')

# 2. Use production server (Gunicorn)
pip install gunicorn
gunicorn -w 4 -b 0.0.0.0:5000 app:app

# 3. Use reverse proxy (Nginx)
# Configure Nginx to proxy requests to Gunicorn

# 4. Enable SSL/TLS
# Use Let's Encrypt for free certificates

# 5. Regular backups
pg_dump stockmaster > backup.sql

# 6. Monitor logs
tail -f /var/log/stockmaster/app.log
```

---

## 📦 Dependencies

### Core Dependencies
- **Flask** (2.3.3) - Web framework
- **Flask-SQLAlchemy** (3.0.5) - ORM
- **Flask-Login** (0.6.3) - Authentication
- **Werkzeug** (2.3.7) - WSGI utilities
- **Flask-Mail** (0.9.1) - Email support
- **psycopg2-binary** (2.9.7) - PostgreSQL driver
- **python-dotenv** (1.0.0) - Environment variables

### Development Dependencies
- pytest
- pytest-cov
- black (code formatting)
- flake8 (linting)

---

## 🤝 Contributing

Contributions are welcome! Please follow these steps:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit changes (`git commit -m 'Add amazing feature'`)
4. Push to branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

### Coding Standards
- Follow PEP 8 style guide
- Add docstrings to functions
- Write tests for new features
- Update documentation

---

## 📄 License

This project is licensed under the MIT License - see [LICENSE](LICENSE) file for details.

---

## 👨‍💼 Support

### Getting Help

- 📖 Read the [documentation](NOTIFICATION_FEATURE.md)
- 🐛 Check [existing issues](https://github.com/yourusername/stockmaster/issues)
- 💬 Create a [new issue](https://github.com/yourusername/stockmaster/issues/new)
- 📧 Email: support@stockmaster.com

### Roadmap

- [ ] Advanced reporting and analytics
- [ ] Mobile app (React Native)
- [ ] API authentication (JWT)
- [ ] Barcode scanning support
- [ ] Integration with accounting software
- [ ] Multi-language support
- [ ] Dark mode UI
- [ ] Push notifications

---

## 🙏 Acknowledgments

- Built with [Flask](https://flask.palletsprojects.com/)
- Database: [PostgreSQL](https://www.postgresql.org/)
- Icons: [Bootstrap Icons](https://icons.getbootstrap.com/)
- UI Components: Custom CSS

---

## 📊 Project Statistics

- **Total Routes**: 53
- **Database Models**: 10+
- **Templates**: 30+
- **CSS Lines**: 1000+
- **Python Lines**: 2000+
- **Notification Types**: 4
- **User Roles**: 2

---

## 🎉 Getting Started Now!

```bash
# 1. Clone
git clone https://github.com/yourusername/stockmaster.git

# 2. Setup
cd stockmaster
python -m venv venv
source venv/bin/activate  # or venv\Scripts\activate on Windows
pip install -r requirements.txt

# 3. Configure
# Update app.py with your database credentials

# 4. Run
python app.py

# 5. Access
# Open http://localhost:5000
```

---

<div align="center">

**Made with ❤️ for inventory management**

[⬆ back to top](#-stockmaster---inventory-management-system)

</div>
