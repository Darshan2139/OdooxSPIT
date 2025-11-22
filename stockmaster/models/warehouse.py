# -*- coding: utf-8 -*-

from odoo import models, fields, api


class StockMasterWarehouse(models.Model):
    _name = 'stockmaster.warehouse'
    _description = 'StockMaster Warehouse'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    name = fields.Char(string='Warehouse Name', required=True, tracking=True)
    code = fields.Char(string='Code', required=True, tracking=True)
    warehouse_id = fields.Many2one('stock.warehouse', string='Related Odoo Warehouse', ondelete='cascade')
    location_id = fields.Many2one('stock.location', string='Main Location', required=True)
    active = fields.Boolean(string='Active', default=True)
    
    # Address information
    street = fields.Char(string='Street')
    street2 = fields.Char(string='Street2')
    city = fields.Char(string='City')
    state_id = fields.Many2one('res.country.state', string='State')
    zip = fields.Char(string='ZIP')
    country_id = fields.Many2one('res.country', string='Country')
    phone = fields.Char(string='Phone')
    email = fields.Char(string='Email')
    
    # Statistics
    total_products = fields.Integer(string='Total Products', compute='_compute_statistics', store=False)
    total_stock_value = fields.Float(string='Total Stock Value', compute='_compute_statistics', store=False)
    
    _sql_constraints = [
        ('code_unique', 'unique(code)', 'Warehouse code must be unique!'),
    ]

    @api.depends('location_id')
    def _compute_statistics(self):
        for record in self:
            # Count products with stock in this warehouse
            product_locations = self.env['stockmaster.product.location'].search([
                ('warehouse_id', '=', record.warehouse_id.id if record.warehouse_id else False)
            ])
            record.total_products = len(product_locations.mapped('product_id'))
            # Stock value calculation would require product cost, simplified here
            record.total_stock_value = sum(product_locations.mapped('quantity'))

    @api.model
    def create(self, vals):
        # Create related Odoo warehouse if not exists
        if not vals.get('warehouse_id'):
            warehouse_vals = {
                'name': vals.get('name'),
                'code': vals.get('code'),
            }
            warehouse = self.env['stock.warehouse'].create(warehouse_vals)
            vals['warehouse_id'] = warehouse.id
            vals['location_id'] = warehouse.lot_stock_id.id
        
        return super(StockMasterWarehouse, self).create(vals)


class ResUsers(models.Model):
    _inherit = 'res.users'

    warehouse_ids = fields.Many2many('stockmaster.warehouse', string='Assigned Warehouses',
                                     help='Warehouses this user has access to')
    otp_code = fields.Char(string='OTP Code', help='Temporary OTP for password reset')
    otp_expiry = fields.Datetime(string='OTP Expiry', help='OTP expiration time')

