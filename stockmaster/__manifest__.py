# -*- coding: utf-8 -*-
{
    'name': 'StockMaster - Inventory Management System',
    'version': '1.0.0',
    'category': 'Inventory',
    'summary': 'Complete Inventory Management System with real-time stock tracking',
    'description': """
        StockMaster - Inventory Management System
        =========================================
        
        A comprehensive inventory management system that digitizes and streamlines
        all stock-related operations within a business.
        
        Features:
        * Product Management with SKU tracking
        * Receipts (Incoming Stock)
        * Delivery Orders (Outgoing Stock)
        * Internal Transfers
        * Stock Adjustments
        * Real-time Dashboard with KPIs
        * Stock Ledger and Move History
        * Multi-warehouse Support
        * Low Stock Alerts
        * OTP-based Authentication
    """,
    'author': 'StockMaster Team',
    'website': 'https://www.example.com',
    'depends': [
        'base',
        'stock',
        'product',
        'mail',
    ],
    'data': [
        'security/ir.model.access.csv',
        'security/security.xml',
        'data/sequences.xml',
        'views/menu.xml',
        'views/dashboard.xml',
        'views/product_views.xml',
        'views/warehouse_views.xml',
        'views/receipt_views.xml',
        'views/delivery_views.xml',
        'views/transfer_views.xml',
        'views/adjustment_views.xml',
        'views/ledger_views.xml',
        'data/demo_data.xml',
    ],
    'demo': [
        'data/demo_data.xml',
    ],
    'installable': True,
    'application': True,
    'auto_install': False,
    'license': 'LGPL-3',
}

