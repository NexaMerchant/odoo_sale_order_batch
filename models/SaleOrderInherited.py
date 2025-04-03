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

    carrier_shipping_number = fields.Char(
        string='物流号',
        compute='_compute_carrier_shipping_number',
        store=True
    )

    carrier_tracking_ref = fields.Char(
        string='跟踪码',
        compute='_compute_carrier_tracking_ref',
        store=True
    )

    @api.depends('picking_ids.carrier_tracking_ref')
    def _compute_carrier_tracking_ref(self):
        for order in self:
            # 可按需要选择最新寄送单或拼接所有寄送单跟踪码
            tracking_refs = order.picking_ids.filtered(lambda p: p.state != 'cancel').mapped('carrier_tracking_ref')
            order.carrier_tracking_ref = ', '.join(filter(None, tracking_refs)) or '无'

    @api.depends('carrier_id')
    def _compute_carrier_shipping_number(self):
        for order in self:
            if order.carrier_id and hasattr(order.carrier_id, 'shipping_number'):
                order.carrier_shipping_number = order.carrier_id.shipping_number or '无'
            else:
                order.carrier_shipping_number = '无'

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

    def action_batch_get_shipping_numbers(self):
        for order in self:
            # 示例业务逻辑：以订单号后四位生成面单号，可根据需要替换为实际获取逻辑
            if order.name:
                order.delivery_number = "SHP" + order.name[-4:]
        return True

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