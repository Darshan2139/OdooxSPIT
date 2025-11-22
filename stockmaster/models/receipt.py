# -*- coding: utf-8 -*-

from odoo import models, fields, api
from odoo.exceptions import ValidationError, UserError
from datetime import datetime


class StockMasterReceipt(models.Model):
    _name = 'stockmaster.receipt'
    _description = 'Stock Receipt (Incoming Stock)'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'date desc, id desc'

    name = fields.Char(string='Receipt Number', required=True, default=lambda self: self._generate_receipt_number(), readonly=True, copy=False)
    date = fields.Datetime(string='Receipt Date', required=True, default=fields.Datetime.now, tracking=True)
    supplier_id = fields.Many2one('res.partner', string='Supplier', required=True, domain=[('supplier_rank', '>', 0)], tracking=True)
    warehouse_id = fields.Many2one('stockmaster.warehouse', string='Warehouse', required=True, tracking=True)
    location_id = fields.Many2one('stock.location', string='Destination Location', required=True, tracking=True)
    
    state = fields.Selection([
        ('draft', 'Draft'),
        ('waiting', 'Waiting'),
        ('ready', 'Ready'),
        ('done', 'Done'),
        ('canceled', 'Canceled')
    ], string='Status', default='draft', required=True, tracking=True)
    
    receipt_line_ids = fields.One2many('stockmaster.receipt.line', 'receipt_id', string='Receipt Lines', required=True)
    
    # Computed fields
    total_products = fields.Integer(string='Total Products', compute='_compute_totals', store=False)
    total_quantity = fields.Float(string='Total Quantity', compute='_compute_totals', store=False)
    
    notes = fields.Text(string='Notes')
    user_id = fields.Many2one('res.users', string='Responsible', default=lambda self: self.env.user, tracking=True)
    
    _sql_constraints = [
        ('name_unique', 'unique(name)', 'Receipt number must be unique!'),
    ]

    @api.model
    def _generate_receipt_number(self):
        """Generate unique receipt number"""
        sequence = self.env['ir.sequence'].next_by_code('stockmaster.receipt') or 'New'
        return sequence

    @api.depends('receipt_line_ids', 'receipt_line_ids.quantity')
    def _compute_totals(self):
        for record in self:
            record.total_products = len(record.receipt_line_ids)
            record.total_quantity = sum(record.receipt_line_ids.mapped('quantity'))

    @api.onchange('warehouse_id')
    def _onchange_warehouse(self):
        if self.warehouse_id and self.warehouse_id.location_id:
            self.location_id = self.warehouse_id.location_id

    def action_confirm(self):
        """Move to waiting state"""
        for record in self:
            if not record.receipt_line_ids:
                raise UserError('Please add at least one product to the receipt.')
            record.state = 'waiting'

    def action_ready(self):
        """Move to ready state"""
        for record in self:
            if record.state != 'waiting':
                raise UserError('Receipt must be in Waiting state to be marked as Ready.')
            record.state = 'ready'

    def action_validate(self):
        """Validate receipt and update stock"""
        for record in self:
            if record.state != 'ready':
                raise UserError('Receipt must be in Ready state to be validated.')
            
            if not record.receipt_line_ids:
                raise UserError('Please add at least one product to the receipt.')
            
            # Create stock moves and update stock
            for line in record.receipt_line_ids:
                # Update product stock in location
                line.product_id.update_stock_location(record.location_id, line.quantity, 'receipt')
                
                # Create stock move record
                self.env['stockmaster.stock.move'].create({
                    'move_type': 'receipt',
                    'reference': record.name,
                    'product_id': line.product_id.id,
                    'location_id': False,  # External source
                    'location_dest_id': record.location_id.id,
                    'quantity': line.quantity,
                    'date': record.date,
                    'partner_id': record.supplier_id.id,
                    'receipt_id': record.id,
                })
                
                # Log in ledger
                self.env['stockmaster.stock.ledger'].create({
                    'date': record.date,
                    'product_id': line.product_id.id,
                    'location_id': record.location_id.id,
                    'operation_type': 'receipt',
                    'reference': record.name,
                    'quantity_in': line.quantity,
                    'quantity_out': 0.0,
                    'balance': line.product_id.get_stock_by_location(record.location_id),
                    'partner_id': record.supplier_id.id,
                })
            
            record.state = 'done'
            record.message_post(body='Receipt validated. Stock updated.')

    def action_cancel(self):
        """Cancel receipt"""
        for record in self:
            if record.state == 'done':
                raise UserError('Cannot cancel a receipt that has been validated.')
            record.state = 'canceled'

    def action_reset_to_draft(self):
        """Reset to draft"""
        for record in self:
            if record.state == 'done':
                raise UserError('Cannot reset a validated receipt to draft.')
            record.state = 'draft'


class StockMasterReceiptLine(models.Model):
    _name = 'stockmaster.receipt.line'
    _description = 'Receipt Line'

    receipt_id = fields.Many2one('stockmaster.receipt', string='Receipt', required=True, ondelete='cascade')
    product_id = fields.Many2one('stockmaster.product', string='Product', required=True)
    quantity = fields.Float(string='Quantity', required=True, default=1.0)
    uom_id = fields.Many2one('uom.uom', string='Unit of Measure', related='product_id.uom_id', readonly=True)
    received_qty = fields.Float(string='Received Quantity', default=0.0, help='Actual quantity received')
    
    _sql_constraints = [
        ('quantity_positive', 'CHECK(quantity > 0)', 'Quantity must be positive!'),
    ]

    @api.onchange('product_id')
    def _onchange_product(self):
        if self.product_id:
            self.uom_id = self.product_id.uom_id

