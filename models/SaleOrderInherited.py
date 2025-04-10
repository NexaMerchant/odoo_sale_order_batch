from odoo import models, fields, api
from odoo import tools
from odoo.exceptions import UserError
import logging

_logger = logging.getLogger(__name__)

class SaleOrderInherited(models.Model):
    _inherit = 'sale.order'

    order_line_images = fields.Html(string='产品图片', compute='_compute_order_line_images')

    shipping_status = fields.Selection([
        ('pending', '待处理'),
        ('draft', '运单号申请'),
        ('waiting_stock', '待打单有货'),
        ('waiting_backorder', '待打单缺货'),
        ('shipped_success', '已交运发货成功'),
        ('shipped_failed', '已交运发货失败'),
        ('refunded', '已退款'),
        ('on_hold', '已搁置'),
        ('other', '其他'),
    ], string='发货状态', default='pending', tracking=True)

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
                    # Use a table to display the image and SKU side-by-side
                    images_html += '<table style="width:100%; border-collapse: collapse; margin-bottom: 5px;">'
                    images_html += '<tr>'
                    
                    # Image cell
                    images_html += '<td style="width: 60px; padding: 5px; vertical-align: top;">'
                    if img_url:
                        images_html += '<img src="%s" style="height:60px;width:60px;border:1px solid #ccc;" />' % img_url
                    images_html += '</td>'
                    
                    # SKU and Price cell
                    images_html += '<td style="padding: 5px; vertical-align: top;">'
                    images_html += '<div style="font-size:12px;color:#888;">SKU: %s</div>' % (product.default_code or '')
                    images_html += '<div style="font-size:12px;color:#888;">Price: %s</div>' % (line.price_unit)  # Display the price
                    images_html += '</td>'
                    
                    images_html += '</tr>'
                    images_html += '</table>'
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

    @api.model
    def _read_group(self, domain, fields, groupby, offset=0, limit=None, orderby=False, lazy=True):
        res = super()._read_group(domain, fields, groupby, offset=offset, limit=limit, orderby=orderby, lazy=lazy)
        
        # Add the count to the filter labels
        for group in res:
            if group.get('__domain'):
                group['__count'] = self.search_count(group['__domain'])
                group['display_name'] = '%s (%s)' % (group['display_name'], group['__count'])
        return res


    def get_tracking_number_from_api(self, order):
        print('get_tracking_number_from_api: ' + order.carrier_id.name)
        print('get_tracking_number_from_api: ' + order.carrier_id.delivery_type)
        if order.carrier_id and order.carrier_id.delivery_type == 'cnexpress':
            # 在这里添加调用API的逻辑
            # 例如，假设API返回一个物流号
            # use CNEExpressRequest to get the tracking number
            # 这里可以调用外部API或其他方法来获取物流号
            # 例如，假设你从相关的 stock.picking 中获取物流号
            # print(order.carrier_id.name)
            # # print the order carrier_id method and attributes
            # print(order.carrier_id)
            # print(order.carrier_id.delivery_type)
            # # print the order carrier_id public methods and attributes
            # print(dir(order.carrier_id))
            # # if the carrier_id is cneexpress, use api to get the tracking number


            # order picking_ids
            # if the order has picking_ids, get the first picking_id
            tracking_number = ""
            if order.picking_ids:
                print("order.picking_ids")
                print(order.picking_ids)
                tracking_number = order.carrier_id.send_shipping(order.picking_ids)
            print("get_tracking_number_from_api1111")
            print(tracking_number)
            return tracking_number



    def action_batch_get_delivery_shipping_number(self):
        for order in self:
            # 在这里添加获取物流号的逻辑
            # 如果没有选择物流配送跳过
            if not order.carrier_id:
                continue
            # 如果有物流后，通过接口获取对应的物流号
            # 这里可以调用外部API或其他方法来获取物流号

            # 例如，假设你从相关的 stock.picking 中获取物流号
            # 这里可以调用外部API或其他方法来获取物流号

            # if the carrier_id is cneexpress, use api to get the tracking number

            tracking_number = self.get_tracking_number_from_api(order)
            print("action_batch_get_delivery_shipping_number")
            print(tracking_number)



            # 例如，假设你从相关的 stock.picking 中获取物流号
            tracking_refs = order.picking_ids.filtered(lambda p: p.state != 'cancel').mapped('carrier_tracking_ref')
            order.carrier_tracking_ref = ', '.join(filter(None, tracking_refs)) or '无'

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