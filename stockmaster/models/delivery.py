# -*- coding: utf-8 -*-

from odoo import models, fields, api
from odoo.exceptions import ValidationError, UserError
from datetime import datetime


class StockMasterDelivery(models.Model):
    _name = 'stockmaster.delivery'
    _description = 'Delivery Order (Outgoing Stock)'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'date desc, id desc'

    name = fields.Char(string='Delivery Number', required=True, default=lambda self: self._generate_delivery_number(), readonly=True, copy=False)
    date = fields.Datetime(string='Delivery Date', required=True, default=fields.Datetime.now, tracking=True)
    customer_id = fields.Many2one('res.partner', string='Customer', required=True, domain=[('customer_rank', '>', 0)], tracking=True)
    warehouse_id = fields.Many2one('stockmaster.warehouse', string='Warehouse', required=True, tracking=True)
    location_id = fields.Many2one('stock.location', string='Source Location', required=True, tracking=True)
    
    state = fields.Selection([
        ('draft', 'Draft'),
        ('picking', 'Picking'),
        ('packing', 'Packing'),
        ('ready', 'Ready'),
        ('done', 'Done'),
        ('canceled', 'Canceled')
    ], string='Status', default='draft', required=True, tracking=True)
    
    delivery_line_ids = fields.One2many('stockmaster.delivery.line', 'delivery_id', string='Delivery Lines', required=True)
    
    # Computed fields
    total_products = fields.Integer(string='Total Products', compute='_compute_totals', store=False)
    total_quantity = fields.Float(string='Total Quantity', compute='_compute_totals', store=False)
    
    notes = fields.Text(string='Notes')
    user_id = fields.Many2one('res.users', string='Responsible', default=lambda self: self.env.user, tracking=True)
    
    _sql_constraints = [
        ('name_unique', 'unique(name)', 'Delivery number must be unique!'),
    ]

    @api.model
    def _generate_delivery_number(self):
        """Generate unique delivery number"""
        sequence = self.env['ir.sequence'].next_by_code('stockmaster.delivery') or 'New'
        return sequence

    @api.depends('delivery_line_ids', 'delivery_line_ids.quantity')
    def _compute_totals(self):
        for record in self:
            record.total_products = len(record.delivery_line_ids)
            record.total_quantity = sum(record.delivery_line_ids.mapped('quantity'))

    @api.onchange('warehouse_id')
    def _onchange_warehouse(self):
        if self.warehouse_id and self.warehouse_id.location_id:
            self.location_id = self.warehouse_id.location_id

    def action_pick(self):
        """Move to picking state"""
        for record in self:
            if not record.delivery_line_ids:
                raise UserError('Please add at least one product to the delivery.')
            
            # Check stock availability
            for line in record.delivery_line_ids:
                available_stock = line.product_id.get_stock_by_location(record.location_id)
                if available_stock < line.quantity:
                    raise UserError(f'Insufficient stock for {line.product_id.name}. Available: {available_stock}, Required: {line.quantity}')
            
            record.state = 'picking'
            record.message_post(body='Items are being picked.')

    def action_pack(self):
        """Move to packing state"""
        for record in self:
            if record.state != 'picking':
                raise UserError('Delivery must be in Picking state to be packed.')
            record.state = 'packing'
            record.message_post(body='Items are being packed.')

    def action_ready(self):
        """Move to ready state"""
        for record in self:
            if record.state != 'packing':
                raise UserError('Delivery must be in Packing state to be marked as Ready.')
            record.state = 'ready'

    def action_validate(self):
        """Validate delivery and decrease stock"""
        for record in self:
            if record.state != 'ready':
                raise UserError('Delivery must be in Ready state to be validated.')
            
            if not record.delivery_line_ids:
                raise UserError('Please add at least one product to the delivery.')
            
            # Update stock and create stock moves
            for line in record.delivery_line_ids:
                available_stock = line.product_id.get_stock_by_location(record.location_id)
                if available_stock < line.quantity:
                    raise UserError(f'Insufficient stock for {line.product_id.name}. Available: {available_stock}, Required: {line.quantity}')
                
                # Update product stock in location (decrease)
                line.product_id.update_stock_location(record.location_id, -line.quantity, 'delivery')
                
                # Create stock move record
                self.env['stockmaster.stock.move'].create({
                    'move_type': 'delivery',
                    'reference': record.name,
                    'product_id': line.product_id.id,
                    'location_id': record.location_id.id,
                    'location_dest_id': False,  # External destination
                    'quantity': line.quantity,
                    'date': record.date,
                    'partner_id': record.customer_id.id,
                    'delivery_id': record.id,
                })
                
                # Log in ledger
                self.env['stockmaster.stock.ledger'].create({
                    'date': record.date,
                    'product_id': line.product_id.id,
                    'location_id': record.location_id.id,
                    'operation_type': 'delivery',
                    'reference': record.name,
                    'quantity_in': 0.0,
                    'quantity_out': line.quantity,
                    'balance': line.product_id.get_stock_by_location(record.location_id),
                    'partner_id': record.customer_id.id,
                })
            
            record.state = 'done'
            record.message_post(body='Delivery validated. Stock decreased.')

    def action_cancel(self):
        """Cancel delivery"""
        for record in self:
            if record.state == 'done':
                raise UserError('Cannot cancel a delivery that has been validated.')
            record.state = 'canceled'

    def action_reset_to_draft(self):
        """Reset to draft"""
        for record in self:
            if record.state == 'done':
                raise UserError('Cannot reset a validated delivery to draft.')
            record.state = 'draft'


class StockMasterDeliveryLine(models.Model):
    _name = 'stockmaster.delivery.line'
    _description = 'Delivery Line'

    delivery_id = fields.Many2one('stockmaster.delivery', string='Delivery', required=True, ondelete='cascade')
    product_id = fields.Many2one('stockmaster.product', string='Product', required=True)
    quantity = fields.Float(string='Quantity', required=True, default=1.0)
    uom_id = fields.Many2one('uom.uom', string='Unit of Measure', related='product_id.uom_id', readonly=True)
    picked_qty = fields.Float(string='Picked Quantity', default=0.0, help='Actual quantity picked')
    packed_qty = fields.Float(string='Packed Quantity', default=0.0, help='Actual quantity packed')
    
    _sql_constraints = [
        ('quantity_positive', 'CHECK(quantity > 0)', 'Quantity must be positive!'),
    ]

    @api.onchange('product_id')
    def _onchange_product(self):
        if self.product_id:
            self.uom_id = self.product_id.uom_id

