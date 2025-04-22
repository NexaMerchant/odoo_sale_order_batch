from odoo import models, fields, api

class BatchSetShippingStatus(models.TransientModel):
    _name = 'batch.set.shipping.status'
    _description = '批量设置发货状态'

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
    ], string='发货状态', required=True)

    def action_apply(self):
        # 直接批量更新 sale.order 的 shipping_status
        active_ids = self.env.context.get('active_ids', [])
        orders = self.env['sale.order'].browse(active_ids)
        orders.write({'shipping_status': self.shipping_status})

        # log the action for sale order
        for order in orders:
            # 记录用户操作日志
            user = self.env.user
            order.message_post(body=f'用户 {user.name} 批量设置发货状态为: {self.shipping_status}')
            #order.message_post(body=f'批量设置发货状态为: {self.shipping_status}')

        return {'type': 'ir.actions.act_window_close'}