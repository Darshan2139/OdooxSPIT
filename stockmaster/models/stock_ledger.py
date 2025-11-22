# -*- coding: utf-8 -*-

from odoo import models, fields, api


class StockMasterStockLedger(models.Model):
    _name = 'stockmaster.stock.ledger'
    _description = 'Stock Ledger (Audit Trail)'
    _order = 'date desc, id desc'
    _rec_name = 'reference'

    date = fields.Datetime(string='Date', required=True, default=fields.Datetime.now, index=True)
    product_id = fields.Many2one('stockmaster.product', string='Product', required=True, index=True)
    location_id = fields.Many2one('stock.location', string='Location', required=True, index=True)
    
    operation_type = fields.Selection([
        ('receipt', 'Receipt'),
        ('delivery', 'Delivery'),
        ('transfer_in', 'Transfer In'),
        ('transfer_out', 'Transfer Out'),
        ('adjustment', 'Adjustment'),
    ], string='Operation Type', required=True, index=True)
    
    reference = fields.Char(string='Reference', required=True, index=True, help='Reference to source document')
    
    quantity_in = fields.Float(string='Quantity In', default=0.0)
    quantity_out = fields.Float(string='Quantity Out', default=0.0)
    balance = fields.Float(string='Balance', required=True, help='Stock balance after this transaction')
    
    partner_id = fields.Many2one('res.partner', string='Partner', help='Supplier or Customer')
    notes = fields.Text(string='Notes')
    
    # References to source documents
    receipt_id = fields.Many2one('stockmaster.receipt', string='Receipt', ondelete='set null')
    delivery_id = fields.Many2one('stockmaster.delivery', string='Delivery', ondelete='set null')
    transfer_id = fields.Many2one('stockmaster.transfer', string='Transfer', ondelete='set null')
    adjustment_id = fields.Many2one('stockmaster.adjustment', string='Adjustment', ondelete='set null')
    
    user_id = fields.Many2one('res.users', string='User', default=lambda self: self.env.user)

