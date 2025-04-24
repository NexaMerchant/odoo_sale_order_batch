from odoo import models, fields, api

class BatchChooseDeliveryCarrier(models.TransientModel):
    _name = 'batch.choose.delivery.carrier'
    _description = '批量选择快递'

    carrier_id = fields.Many2one('delivery.carrier', string='快递方式', required=True)
    order_ids = fields.Many2many('sale.order', string='订单', required=True)

    @api.model
    def default_get(self, fields):
        res = super().default_get(fields)
        order_ids = self.env.context.get('active_ids') or self.env.context.get('default_order_ids')
        if order_ids:
            res['order_ids'] = [(6, 0, order_ids)]
        return res

    def action_apply(self):
        """Apply the selected carrier to the selected orders."""
        for order in self.order_ids:
            order.carrier_id = self.carrier_id.id
            order.carrier_tracking_ref = False  # Reset tracking reference
            order.shipping_status = 'draft'
            # 自动计算运费并添加运费行
            price = self.carrier_id.rate_shipment(order)['price']
            order._create_delivery_line(self.carrier_id, price)
            #order._compute_amount_all()
            # 如需自定义快递商品行，可保留以下逻辑
            # 设置拣货单的快递方式
            order.carrier_id = self.carrier_id.id
            # 设置拣货单的快递单号为空
            carrier_product = self.carrier_id.product_id
            if carrier_product:
                exist = order.order_line.filtered(lambda l: l.product_id == carrier_product)
                if not exist:
                    self.env['sale.order.line'].create({
                        'order_id': order.id,
                        'product_id': carrier_product.id,
                        'name': carrier_product.name,
                        'product_uom_qty': 1,
                        'product_uom': carrier_product.uom_id.id,
                        'price_unit': carrier_product.lst_price,
                    })
        return {'type': 'ir.actions.act_window_close'}