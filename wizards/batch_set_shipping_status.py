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
        ('not_postd', '暂不发'),
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
            # 如果修改订单状态为 'not_postd'，修改订单的仓库为 None,把现在的仓库ID更新到 original_warehouse_id
            if self.shipping_status == 'not_postd':
                # 准备要写入的仓库相关值
                warehouse_vals_to_write = {}
                if order.warehouse_id:
                    warehouse_vals_to_write['original_warehouse_id'] = order.warehouse_id.id
                    warehouse_vals_to_write['warehouse_id'] = 1
                
                # 记录在修改仓库之前的订单状态，特别是判断是否为 'sale'
                initial_order_state = order.state

                # 写入仓库变更
                if warehouse_vals_to_write:
                    order.write(warehouse_vals_to_write)

                # 如果订单原状态是 'sale' (或其他已确认会生成拣货的状态)，
                # 则需要取消拣货和相关的库存移动
                if initial_order_state == 'sale': # 您可以根据需要扩展此条件，例如 ['sale', 'done'] 但要注意 'done' 状态的订单取消逻辑
                    order.action_cancel()  # 这会取消相关的拣货单和库存移动，并将订单状态设置为 'cancel'
                
                # 确保订单最终状态为 'draft'
                if order.state != 'draft':
                    order.action_draft() # 如果 action_cancel 后状态为 'cancel', 此操作会将其变为 'draft'

                # 订单的仓库单的仓库也需要更新为 1
                if order.picking_ids:
                    for picking in order.picking_ids:
                        picking.write({'location_id': 1})

            else: # 当 shipping_status 不是 'not_postd' 时
                # 如果存在原始仓库信息，则恢复仓库
                if order.original_warehouse_id:
                    order.write({
                        'warehouse_id': order.original_warehouse_id,
                        'original_warehouse_id': False,
                    })
                    # 注意：如果此时订单状态是 'draft'，并且新的 shipping_status 暗示订单应重新激活，
                    # 您可能需要考虑调用 order.action_confirm() 来重新生成基于新（恢复后）仓库的拣货单。
                    # 例如:
                    # if order.state == 'draft' and self.shipping_status in ['pending', 'waiting_stock']: # 假设这些状态意味着激活
                    #     order.action_confirm()
                    # 这部分逻辑取决于您对其他 shipping_status 的业务定义。  

                    # 出库单也需要更新为原始仓库
                    if order.picking_ids:
                        for picking in order.picking_ids:
                            picking.write({'location_id': 39})

        return {'type': 'ir.actions.act_window_close'}