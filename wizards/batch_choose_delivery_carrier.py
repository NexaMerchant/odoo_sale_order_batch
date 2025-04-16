from odoo import models, fields, api

class BatchChooseDeliveryCarrier(models.TransientModel):
    _name = 'batch.choose.delivery.carrier'
    _description = '批量选择快递'

    carrier_id = fields.Many2one('delivery.carrier', string='快递方式', required=True)
    order_ids = fields.Many2many('sale.order', string='订单', required=True)

    @api.model
    def default_get(self, fields):
        res = super().default_get(fields)
        order_ids = self.env.context.get('default_order_ids')
        if order_ids:
            res['order_ids'] = order_ids
        return res

    def action_apply(self):
        """Apply the selected carrier to the selected orders."""
        for order in self.order_ids:
            order.carrier_id = self.carrier_id.id