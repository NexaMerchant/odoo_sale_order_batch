# -*- coding: utf-8 -*-

# from odoo import models, fields, api


# class sale_order_batch(models.Model):
#     _name = 'sale_order_batch.sale_order_batch'
#     _description = 'sale_order_batch.sale_order_batch'

#     name = fields.Char()
#     value = fields.Integer()
#     value2 = fields.Float(compute="_value_pc", store=True)
#     description = fields.Text()
#
#     @api.depends('value')
#     def _value_pc(self):
#         for record in self:
#             record.value2 = float(record.value) / 100

from odoo import models, fields, api

class SaleOrder(models.Model):
    _inherit = 'sale.order'

    order_line = fields.One2many(
        'sale.order.line', 'order_id', string="Order Lines"
    )

    product_image = fields.Binary(
        string="Product Image", compute="_compute_product_image", store=True
    )

    @api.depends("order_line.product_id")
    def _compute_product_image(self):
        for order in self:
            first_line = order.order_line[:1]  # Get the first order line
            order.product_image = first_line.product_id.image_128 if first_line else False

    order_line_products = fields.Many2many(
        'product.product', 
        string="Products", 
        compute='_compute_order_line_products'
    )

    @api.depends('order_line.product_id')
    def _compute_order_line_products(self):
        for order in self:
            order.order_line_products = order.order_line.mapped('product_id')

class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'

    product_id = fields.Many2one(
        'product.product', string="Product"
    )