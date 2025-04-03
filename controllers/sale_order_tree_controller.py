# python
from odoo import http

class SaleOrderTreeController(http.Controller):
    @http.route('/sale_orders', auth='public', website=True)
    def sale_order_tree(self, **kw):
        # 根据 URL 参数获取订单状态，用于过滤订单（示例中返回空列表，可替换查询逻辑）
        status = kw.get('status', '')
        orders = []  # 此处可使用 ORM 查询符合状态的订单

        # simulate fetching orders from the database
        orders = http.request.env['sale.order'].search([('state', '=', status)])

        # 示例分页信息（实际开发中根据订单总数计算）
        pager = {
            'current_page': 1,
            'total_pages': 1,
        }
        return http.request.render('sale_order_batch.custom_sale_order_tree_page', {
            'orders': orders,
            'pager': pager,
        })