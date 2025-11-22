# StockMaster - Inventory Management System

A comprehensive Odoo module for inventory management that digitizes and streamlines all stock-related operations.

## Features

- **Product Management**: Create and manage products with SKU tracking, categories, and stock levels
- **Receipts**: Record incoming stock from suppliers
- **Delivery Orders**: Manage outgoing stock to customers with pick/pack/validate workflow
- **Internal Transfers**: Move stock between locations within the organization
- **Stock Adjustments**: Fix discrepancies between recorded and physical stock
- **Real-time Dashboard**: View KPIs including total products, low stock items, pending operations
- **Stock Ledger**: Complete audit trail of all inventory movements
- **Multi-warehouse Support**: Manage inventory across multiple warehouses
- **Low Stock Alerts**: Automatic alerts when stock falls below minimum levels
- **OTP Authentication**: Secure password reset with OTP

## Installation

1. Copy the `stockmaster` folder to your Odoo addons directory
2. Update the apps list in Odoo
3. Install the "StockMaster - Inventory Management System" module

## Dependencies

- Odoo 16.0 or later
- Python 3.10+
- PostgreSQL database
- Odoo modules: `base`, `stock`, `product`, `mail`

## User Roles

- **Inventory Manager**: Full access to all operations and settings
- **Warehouse Staff**: Limited access to perform operations (receipts, deliveries, transfers)

## Usage

### Creating Products

1. Navigate to **StockMaster > Products**
2. Click **Create**
3. Fill in product details (Name, SKU, Category, UOM)
4. Set minimum stock level for low stock alerts
5. Save

### Receiving Stock

1. Navigate to **StockMaster > Operations > Receipts**
2. Click **Create**
3. Select supplier and warehouse
4. Add products and quantities
5. Confirm → Mark Ready → Validate
6. Stock is automatically updated

### Delivering Stock

1. Navigate to **StockMaster > Operations > Delivery Orders**
2. Click **Create**
3. Select customer and warehouse
4. Add products and quantities
5. Pick → Pack → Mark Ready → Validate
6. Stock is automatically decreased

### Internal Transfers

1. Navigate to **StockMaster > Operations > Internal Transfers**
2. Click **Create**
3. Select source and destination locations
4. Add products and quantities
5. Confirm → Mark Ready → Validate
6. Stock is moved between locations

### Stock Adjustments

1. Navigate to **StockMaster > Operations > Stock Adjustments**
2. Click **Create**
3. Select product and location
4. Enter counted quantity
5. System shows difference automatically
6. Validate to update stock

## API Endpoints

- `/stockmaster/signup` - User signup (POST)
- `/stockmaster/login` - User login (POST)
- `/stockmaster/forgot-password` - Request OTP (POST)
- `/stockmaster/reset-password` - Reset password with OTP (POST)

## Support

For issues or questions, please contact the development team.

