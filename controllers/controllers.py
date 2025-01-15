# -*- coding: utf-8 -*-
# from odoo import http


# class SaleOrderBatch(http.Controller):
#     @http.route('/sale_order_batch/sale_order_batch', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/sale_order_batch/sale_order_batch/objects', auth='public')
#     def list(self, **kw):
#         return http.request.render('sale_order_batch.listing', {
#             'root': '/sale_order_batch/sale_order_batch',
#             'objects': http.request.env['sale_order_batch.sale_order_batch'].search([]),
#         })

#     @http.route('/sale_order_batch/sale_order_batch/objects/<model("sale_order_batch.sale_order_batch"):obj>', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('sale_order_batch.object', {
#             'object': obj
#         })

