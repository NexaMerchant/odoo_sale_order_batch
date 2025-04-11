from odoo import models, fields

class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'
    
    product_image = fields.Binary(
        string="Product Image",
        related='product_id.image_128',
        readonly=True
    )