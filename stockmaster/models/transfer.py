# -*- coding: utf-8 -*-

from odoo import models, fields, api
from odoo.exceptions import ValidationError, UserError


class StockMasterTransfer(models.Model):
    _name = 'stockmaster.transfer'
    _description = 'Internal Stock Transfer'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'date desc, id desc'

    name = fields.Char(string='Transfer Number', required=True, default=lambda self: self._generate_transfer_number(), readonly=True, copy=False)
    date = fields.Datetime(string='Transfer Date', required=True, default=fields.Datetime.now, tracking=True)
    
    source_location_id = fields.Many2one('stock.location', string='Source Location', required=True, tracking=True)
    destination_location_id = fields.Many2one('stock.location', string='Destination Location', required=True, tracking=True)
    
    state = fields.Selection([
        ('draft', 'Draft'),
        ('waiting', 'Waiting'),
        ('ready', 'Ready'),
        ('done', 'Done'),
        ('canceled', 'Canceled')
    ], string='Status', default='draft', required=True, tracking=True)
    
    transfer_line_ids = fields.One2many('stockmaster.transfer.line', 'transfer_id', string='Transfer Lines', required=True)
    
    # Computed fields
    total_products = fields.Integer(string='Total Products', compute='_compute_totals', store=False)
    total_quantity = fields.Float(string='Total Quantity', compute='_compute_totals', store=False)
    
    notes = fields.Text(string='Notes')
    user_id = fields.Many2one('res.users', string='Responsible', default=lambda self: self.env.user, tracking=True)
    
    _sql_constraints = [
        ('name_unique', 'unique(name)', 'Transfer number must be unique!'),
        ('different_locations', 'CHECK(source_location_id != destination_location_id)', 'Source and destination locations must be different!'),
    ]

    @api.model
    def _generate_transfer_number(self):
        """Generate unique transfer number"""
        sequence = self.env['ir.sequence'].next_by_code('stockmaster.transfer') or 'New'
        return sequence

    @api.depends('transfer_line_ids', 'transfer_line_ids.quantity')
    def _compute_totals(self):
        for record in self:
            record.total_products = len(record.transfer_line_ids)
            record.total_quantity = sum(record.transfer_line_ids.mapped('quantity'))

    @api.constrains('source_location_id', 'destination_location_id')
    def _check_locations(self):
        for record in self:
            if record.source_location_id == record.destination_location_id:
                raise ValidationError('Source and destination locations must be different!')

    def action_confirm(self):
        """Move to waiting state"""
        for record in self:
            if not record.transfer_line_ids:
                raise UserError('Please add at least one product to the transfer.')
            record.state = 'waiting'

    def action_ready(self):
        """Move to ready state"""
        for record in self:
            if record.state != 'waiting':
                raise UserError('Transfer must be in Waiting state to be marked as Ready.')
            
            # Check stock availability in source location
            for line in record.transfer_line_ids:
                available_stock = line.product_id.get_stock_by_location(record.source_location_id)
                if available_stock < line.quantity:
                    raise UserError(f'Insufficient stock for {line.product_id.name} in source location. Available: {available_stock}, Required: {line.quantity}')
            
            record.state = 'ready'

    def action_validate(self):
        """Validate transfer and move stock"""
        for record in self:
            if record.state != 'ready':
                raise UserError('Transfer must be in Ready state to be validated.')
            
            if not record.transfer_line_ids:
                raise UserError('Please add at least one product to the transfer.')
            
            # Update stock: decrease from source, increase in destination
            for line in record.transfer_line_ids:
                available_stock = line.product_id.get_stock_by_location(record.source_location_id)
                if available_stock < line.quantity:
                    raise UserError(f'Insufficient stock for {line.product_id.name} in source location. Available: {available_stock}, Required: {line.quantity}')
                
                # Decrease from source location
                line.product_id.update_stock_location(record.source_location_id, -line.quantity, 'transfer')
                
                # Increase in destination location
                line.product_id.update_stock_location(record.destination_location_id, line.quantity, 'transfer')
                
                # Create stock move record
                self.env['stockmaster.stock.move'].create({
                    'move_type': 'transfer',
                    'reference': record.name,
                    'product_id': line.product_id.id,
                    'location_id': record.source_location_id.id,
                    'location_dest_id': record.destination_location_id.id,
                    'quantity': line.quantity,
                    'date': record.date,
                    'transfer_id': record.id,
                })
                
                # Log in ledger (source location - out)
                self.env['stockmaster.stock.ledger'].create({
                    'date': record.date,
                    'product_id': line.product_id.id,
                    'location_id': record.source_location_id.id,
                    'operation_type': 'transfer_out',
                    'reference': record.name,
                    'quantity_in': 0.0,
                    'quantity_out': line.quantity,
                    'balance': line.product_id.get_stock_by_location(record.source_location_id),
                })
                
                # Log in ledger (destination location - in)
                self.env['stockmaster.stock.ledger'].create({
                    'date': record.date,
                    'product_id': line.product_id.id,
                    'location_id': record.destination_location_id.id,
                    'operation_type': 'transfer_in',
                    'reference': record.name,
                    'quantity_in': line.quantity,
                    'quantity_out': 0.0,
                    'balance': line.product_id.get_stock_by_location(record.destination_location_id),
                })
            
            record.state = 'done'
            record.message_post(body='Transfer validated. Stock moved between locations.')

    def action_cancel(self):
        """Cancel transfer"""
        for record in self:
            if record.state == 'done':
                raise UserError('Cannot cancel a transfer that has been validated.')
            record.state = 'canceled'

    def action_reset_to_draft(self):
        """Reset to draft"""
        for record in self:
            if record.state == 'done':
                raise UserError('Cannot reset a validated transfer to draft.')
            record.state = 'draft'


class StockMasterTransferLine(models.Model):
    _name = 'stockmaster.transfer.line'
    _description = 'Transfer Line'

    transfer_id = fields.Many2one('stockmaster.transfer', string='Transfer', required=True, ondelete='cascade')
    product_id = fields.Many2one('stockmaster.product', string='Product', required=True)
    quantity = fields.Float(string='Quantity', required=True, default=1.0)
    uom_id = fields.Many2one('uom.uom', string='Unit of Measure', related='product_id.uom_id', readonly=True)
    
    _sql_constraints = [
        ('quantity_positive', 'CHECK(quantity > 0)', 'Quantity must be positive!'),
    ]

    @api.onchange('product_id')
    def _onchange_product(self):
        if self.product_id:
            self.uom_id = self.product_id.uom_id

