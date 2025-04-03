# python
from odoo import http

class CustomReportController(http.Controller):
    @http.route('/custom_report', auth='public', website=True)
    def custom_report(self, **kw):
        # 如果有实际数据，可在此处查询后赋值给 docs
        docs = []
        return http.request.render('sale_order_batch.custom_sale_report_template', {
            'docs': docs,
        })