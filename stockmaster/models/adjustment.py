# -*- coding: utf-8 -*-

from odoo import models, fields, api
from odoo.exceptions import ValidationError, UserError


class StockMasterAdjustment(models.Model):
    _name = 'stockmaster.adjustment'
    _description = 'Stock Adjustment'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'date desc, id desc'

    name = fields.Char(string='Adjustment Number', required=True, default=lambda self: self._generate_adjustment_number(), readonly=True, copy=False)
    date = fields.Datetime(string='Adjustment Date', required=True, default=fields.Datetime.now, tracking=True)
    
    location_id = fields.Many2one('stock.location', string='Location', required=True, tracking=True)
    product_id = fields.Many2one('stockmaster.product', string='Product', required=True, tracking=True)
    
    recorded_qty = fields.Float(string='Recorded Quantity', compute='_compute_recorded_qty', store=False, help='Current stock in system')
    counted_qty = fields.Float(string='Counted Quantity', required=True, help='Physical count')
    difference = fields.Float(string='Difference', compute='_compute_difference', store=False)
    
    state = fields.Selection([
        ('draft', 'Draft'),
        ('done', 'Done'),
        ('canceled', 'Canceled')
    ], string='Status', default='draft', required=True, tracking=True)
    
    reason = fields.Text(string='Reason for Adjustment', help='Explain why this adjustment is needed')
    user_id = fields.Many2one('res.users', string='Responsible', default=lambda self: self.env.user, tracking=True)
    
    _sql_constraints = [
        ('name_unique', 'unique(name)', 'Adjustment number must be unique!'),
    ]

    @api.model
    def _generate_adjustment_number(self):
        """Generate unique adjustment number"""
        sequence = self.env['ir.sequence'].next_by_code('stockmaster.adjustment') or 'New'
        return sequence

    @api.depends('product_id', 'location_id')
    def _compute_recorded_qty(self):
        for record in self:
            if record.product_id and record.location_id:
                record.recorded_qty = record.product_id.get_stock_by_location(record.location_id)
            else:
                record.recorded_qty = 0.0

    @api.depends('recorded_qty', 'counted_qty')
    def _compute_difference(self):
        for record in self:
            record.difference = record.counted_qty - record.recorded_qty

    @api.onchange('product_id', 'location_id')
    def _onchange_product_location(self):
        if self.product_id and self.location_id:
            self.recorded_qty = self.product_id.get_stock_by_location(self.location_id)

    def action_validate(self):
        """Validate adjustment and update stock"""
        for record in self:
            if record.state != 'draft':
                raise UserError('Adjustment must be in Draft state to be validated.')
            
            if not record.product_id or not record.location_id:
                raise UserError('Please select a product and location.')
            
            # Calculate adjustment quantity
            adjustment_qty = record.difference
            
            # Update product stock in location
            record.product_id.update_stock_location(record.location_id, adjustment_qty, 'adjustment')
            
            # Create stock move record
            move_type = 'adjustment_in' if adjustment_qty > 0 else 'adjustment_out'
            self.env['stockmaster.stock.move'].create({
                'move_type': move_type,
                'reference': record.name,
                'product_id': record.product_id.id,
                'location_id': record.location_id.id if adjustment_qty < 0 else False,
                'location_dest_id': record.location_id.id if adjustment_qty > 0 else False,
                'quantity': abs(adjustment_qty),
                'date': record.date,
                'adjustment_id': record.id,
            })
            
            # Log in ledger
            self.env['stockmaster.stock.ledger'].create({
                'date': record.date,
                'product_id': record.product_id.id,
                'location_id': record.location_id.id,
                'operation_type': 'adjustment',
                'reference': record.name,
                'quantity_in': adjustment_qty if adjustment_qty > 0 else 0.0,
                'quantity_out': abs(adjustment_qty) if adjustment_qty < 0 else 0.0,
                'balance': record.product_id.get_stock_by_location(record.location_id),
                'notes': record.reason or 'Stock adjustment',
            })
            
            record.state = 'done'
            record.message_post(body=f'Adjustment validated. Stock {("increased" if adjustment_qty > 0 else "decreased")} by {abs(adjustment_qty)}.')

    def action_cancel(self):
        """Cancel adjustment"""
        for record in self:
            if record.state == 'done':
                raise UserError('Cannot cancel an adjustment that has been validated.')
            record.state = 'canceled'

    def action_reset_to_draft(self):
        """Reset to draft"""
        for record in self:
            if record.state == 'done':
                raise UserError('Cannot reset a validated adjustment to draft.')
            record.state = 'draft'

