# -*- coding: utf-8 -*-

from odoo import models, fields, api


class StockMasterStockMove(models.Model):
    _name = 'stockmaster.stock.move'
    _description = 'Stock Movement'
    _order = 'date desc, id desc'

    name = fields.Char(string='Move Reference', compute='_compute_name', store=True)
    move_type = fields.Selection([
        ('receipt', 'Receipt'),
        ('delivery', 'Delivery'),
        ('transfer', 'Transfer'),
        ('adjustment_in', 'Adjustment (Increase)'),
        ('adjustment_out', 'Adjustment (Decrease)'),
    ], string='Move Type', required=True, index=True)
    
    reference = fields.Char(string='Reference', required=True, help='Reference to source document')
    product_id = fields.Many2one('stockmaster.product', string='Product', required=True, index=True)
    location_id = fields.Many2one('stock.location', string='Source Location', index=True)
    location_dest_id = fields.Many2one('stock.location', string='Destination Location', index=True)
    quantity = fields.Float(string='Quantity', required=True)
    date = fields.Datetime(string='Date', required=True, default=fields.Datetime.now, index=True)
    
    # References to source documents
    receipt_id = fields.Many2one('stockmaster.receipt', string='Receipt', ondelete='cascade')
    delivery_id = fields.Many2one('stockmaster.delivery', string='Delivery', ondelete='cascade')
    transfer_id = fields.Many2one('stockmaster.transfer', string='Transfer', ondelete='cascade')
    adjustment_id = fields.Many2one('stockmaster.adjustment', string='Adjustment', ondelete='cascade')
    
    partner_id = fields.Many2one('res.partner', string='Partner', help='Supplier or Customer')
    
    state = fields.Selection([
        ('draft', 'Draft'),
        ('done', 'Done'),
    ], string='Status', default='done', required=True)

    @api.depends('move_type', 'reference', 'product_id')
    def _compute_name(self):
        for record in self:
            record.name = f"{record.move_type.upper()}: {record.reference} - {record.product_id.name if record.product_id else ''}"

