# -*- coding: utf-8 -*-

from odoo import models, fields, api
from odoo.exceptions import ValidationError


class StockMasterProduct(models.Model):
    _name = 'stockmaster.product'
    _description = 'StockMaster Product'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'name'

    name = fields.Char(string='Product Name', required=True, tracking=True)
    sku = fields.Char(string='SKU / Code', required=True, index=True, tracking=True)
    category_id = fields.Many2one('product.category', string='Category', tracking=True)
    uom_id = fields.Many2one('uom.uom', string='Unit of Measure', required=True, default=lambda self: self._get_default_uom())
    initial_stock = fields.Float(string='Initial Stock', default=0.0)
    min_stock = fields.Float(string='Minimum Stock Level', default=0.0, help='Alert when stock falls below this level')
    max_stock = fields.Float(string='Maximum Stock Level', default=0.0)
    reorder_qty = fields.Float(string='Reorder Quantity', default=0.0, help='Suggested quantity to reorder')
    active = fields.Boolean(string='Active', default=True)
    
    # Stock tracking
    stock_by_location_ids = fields.One2many('stockmaster.product.location', 'product_id', string='Stock by Location')
    total_stock = fields.Float(string='Total Stock', compute='_compute_total_stock', store=False)
    low_stock = fields.Boolean(string='Low Stock', compute='_compute_low_stock', store=False)
    
    # Related to Odoo product
    product_id = fields.Many2one('product.product', string='Related Product', ondelete='cascade')
    
    _sql_constraints = [
        ('sku_unique', 'unique(sku)', 'SKU must be unique!'),
    ]

    @api.model
    def _get_default_uom(self):
        return self.env.ref('uom.product_uom_unit', raise_if_not_found=False)

    @api.depends('stock_by_location_ids', 'stock_by_location_ids.quantity')
    def _compute_total_stock(self):
        for record in self:
            record.total_stock = sum(record.stock_by_location_ids.mapped('quantity'))

    @api.depends('total_stock', 'min_stock')
    def _compute_low_stock(self):
        for record in self:
            record.low_stock = record.total_stock <= record.min_stock if record.min_stock > 0 else False

    @api.model
    def create(self, vals):
        # Create related Odoo product if not exists
        if not vals.get('product_id'):
            product_vals = {
                'name': vals.get('name'),
                'default_code': vals.get('sku'),
                'categ_id': vals.get('category_id'),
                'uom_id': vals.get('uom_id'),
                'type': 'product',
            }
            product = self.env['product.product'].create(product_vals)
            vals['product_id'] = product.id
        
        # Set initial stock if provided
        if vals.get('initial_stock', 0) > 0:
            # Initial stock will be set via stock adjustment or receipt
            pass
        
        return super(StockMasterProduct, self).create(vals)

    def write(self, vals):
        # Update related Odoo product
        if 'name' in vals or 'sku' in vals or 'category_id' in vals:
            for record in self:
                if record.product_id:
                    product_vals = {}
                    if 'name' in vals:
                        product_vals['name'] = vals['name']
                    if 'sku' in vals:
                        product_vals['default_code'] = vals['sku']
                    if 'category_id' in vals:
                        product_vals['categ_id'] = vals['category_id']
                    if product_vals:
                        record.product_id.write(product_vals)
        
        return super(StockMasterProduct, self).write(vals)

    def get_stock_by_location(self, location_id):
        """Get stock quantity for a specific location"""
        self.ensure_one()
        stock_line = self.stock_by_location_ids.filtered(lambda l: l.location_id.id == location_id.id)
        return stock_line.quantity if stock_line else 0.0

    def update_stock_location(self, location_id, quantity, operation_type='adjustment'):
        """Update stock for a specific location"""
        self.ensure_one()
        stock_line = self.stock_by_location_ids.filtered(lambda l: l.location_id.id == location_id.id)
        
        if stock_line:
            new_quantity = stock_line.quantity + quantity
            if new_quantity < 0:
                raise ValidationError(f'Insufficient stock for {self.name} in location {location_id.name}. Available: {stock_line.quantity}, Required: {abs(quantity)}')
            stock_line.quantity = new_quantity
        else:
            if quantity < 0:
                raise ValidationError(f'Insufficient stock for {self.name} in location {location_id.name}. Available: 0, Required: {abs(quantity)}')
            self.env['stockmaster.product.location'].create({
                'product_id': self.id,
                'location_id': location_id.id,
                'quantity': quantity,
            })


class StockMasterProductLocation(models.Model):
    _name = 'stockmaster.product.location'
    _description = 'Product Stock by Location'
    _rec_name = 'location_id'

    product_id = fields.Many2one('stockmaster.product', string='Product', required=True, ondelete='cascade')
    location_id = fields.Many2one('stock.location', string='Location', required=True)
    quantity = fields.Float(string='Quantity', default=0.0, required=True)
    warehouse_id = fields.Many2one('stock.warehouse', string='Warehouse', related='location_id.warehouse_id', store=True)

    _sql_constraints = [
        ('product_location_unique', 'unique(product_id, location_id)', 'Product can only have one stock record per location!'),
    ]

