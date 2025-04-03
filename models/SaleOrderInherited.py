from odoo import models, fields, api

class SaleOrderInherited(models.Model):
    _inherit = 'sale.order'

    order_line_images = fields.Html(string='产品图片', compute='_compute_order_line_images')

    @api.depends('order_line')
    def _compute_order_line_images(self):
        for order in self:
            images_html = ''
            for line in order.order_line:
                if line.product_id:
                    product = line.product_id
                    img_url = ''
                    if product.image_128:
                        img_url = '/web/image/product.product/%s/image_128' % product.id
                    images_html += '<div style="display:inline-block;text-align:center;margin-right:2px;">'
                    if img_url:
                        images_html += '<img src="%s" style="height:60px;width:60px;border:1px solid #ccc;" />' % img_url
                    images_html += '<div style="font-size:10px;">%s</div>' % product.name
                    images_html += '<div style="font-size:10px;color:#888;">SKU: %s</div>' % (
                                product.default_code or '')
                    images_html += '</div>'
            order.order_line_images = images_html

    custom_field = fields.Char(string='Custom Field')

    shipping_country_id = fields.Many2one(
        'res.country',
        string='Shipping Country',
        compute='_compute_shipping_country',
        store=True
    )

    # Add a new field to store the delivery number
    delivery_number = fields.Char(
        string='Delivery Number',
        compute='_compute_delivery_number',
        store=True
    )

    payment_term_id = fields.Many2one('account.payment.term', string='Payment Term')

    # Add a new field to store the delivery carrier
    @api.depends('picking_ids')
    def _compute_delivery_number(self):
        for order in self:
            delivery_numbers = order.picking_ids.filtered(lambda p: p.state != 'cancel').mapped('name')
            order.delivery_number = ', '.join(delivery_numbers)

    @api.depends('partner_shipping_id', 'partner_shipping_id.country_id')
    def _compute_shipping_country(self):
        for order in self:
            order.shipping_country_id = order.partner_shipping_id.country_id

    def action_batch_choose_delivery(self):
        view_id = self.env.ref('delivery.choose_delivery_carrier_view_form').id
        return {
            'name': '批量选择配送方式',
            'type': 'ir.actions.act_window',
            'view_mode': 'form',
            'res_model': 'choose.delivery.carrier',
            'view_id': view_id,
            'views': [(view_id, 'form')],
            'target': 'new',
            'context': {
                'default_order_ids': self.ids,
                'active_ids': self.ids,
            }
        }

    def action_choose_delivery(self):
        self.ensure_one()
        view_id = self.env.ref('delivery.choose_delivery_carrier_view_form').id
        return {
            'name': 'Add a shipping method',
            'type': 'ir.actions.act_window',
            'view_mode': 'form',
            'res_model': 'choose.delivery.carrier',
            'view_id': view_id,
            'views': [(view_id, 'form')],
            'target': 'new',
            'context': {
                'default_order_id': self.id,
                'default_carrier_id': self.carrier_id.id
            }
        }