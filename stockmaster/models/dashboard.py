# -*- coding: utf-8 -*-

from odoo import models, fields, api


class StockMasterDashboard(models.TransientModel):
    _name = 'stockmaster.dashboard'
    _description = 'StockMaster Dashboard'

    # KPIs
    total_products = fields.Integer(string='Total Products', compute='_compute_kpis')
    low_stock_items = fields.Integer(string='Low Stock Items', compute='_compute_kpis')
    out_of_stock_items = fields.Integer(string='Out of Stock Items', compute='_compute_kpis')
    pending_receipts = fields.Integer(string='Pending Receipts', compute='_compute_kpis')
    pending_deliveries = fields.Integer(string='Pending Deliveries', compute='_compute_kpis')
    scheduled_transfers = fields.Integer(string='Scheduled Transfers', compute='_compute_kpis')

    def _compute_kpis(self):
        """Compute dashboard KPIs"""
        for record in self:
            # Total Products
            record.total_products = self.env['stockmaster.product'].search_count([('active', '=', True)])
            
            # Low Stock Items
            products = self.env['stockmaster.product'].search([('active', '=', True)])
            record.low_stock_items = sum(1 for p in products if p.low_stock)
            
            # Out of Stock Items
            record.out_of_stock_items = sum(1 for p in products if p.total_stock <= 0)
            
            # Pending Receipts
            record.pending_receipts = self.env['stockmaster.receipt'].search_count([
                ('state', 'in', ['draft', 'waiting', 'ready'])
            ])
            
            # Pending Deliveries
            record.pending_deliveries = self.env['stockmaster.delivery'].search_count([
                ('state', 'in', ['draft', 'picking', 'packing', 'ready'])
            ])
            
            # Scheduled Transfers
            record.scheduled_transfers = self.env['stockmaster.transfer'].search_count([
                ('state', 'in', ['draft', 'waiting', 'ready'])
            ])

    @api.model
    def get_kpis(self):
        """Get KPI values - create a record to compute"""
        dashboard = self.create({})
        return {
            'total_products': dashboard.total_products,
            'low_stock_items': dashboard.low_stock_items,
            'out_of_stock_items': dashboard.out_of_stock_items,
            'pending_receipts': dashboard.pending_receipts,
            'pending_deliveries': dashboard.pending_deliveries,
            'scheduled_transfers': dashboard.scheduled_transfers,
        }

