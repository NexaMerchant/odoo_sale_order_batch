# python
from odoo import http
from odoo.http import request
from odoo.addons.web.controllers.report import ReportController
from PyPDF2 import PdfReader, PdfWriter
import io
import base64
import requests
from odoo import fields
from odoo.exceptions import UserError

class CustomReportController(http.Controller):
    @http.route(['/report/pdf/sale_order_batch.report_batch_picking'], type='http', auth="user")
    def report_pdf_with_merge(self, **kw):
        # 获取批量打印的 sale.order id 列表
        ids = request.httprequest.args.get('ids')
        if not ids:
            return request.not_found()
        id_list = [int(i) for i in ids.split(',') if i.isdigit()]

        report_obj = request.env['ir.actions.report']
        writer = PdfWriter()

        # check the sale order is not printed and need to confirm continue printing

        for order_id in id_list:

            # 1. 检查订单是否已打印

            # 1. 生成主报表PDF
            pdf_content, _ = report_obj._render_qweb_pdf('sale_order_batch.action_report_batch_picking', [order_id])
            reader_main = PdfReader(io.BytesIO(pdf_content))
            for page in reader_main.pages:
                writer.add_page(page)

            # 2. 获取外部PDF（可根据订单号动态生成URL）
            # 这里以订单号为快递单号举例，实际可根据你的业务调整
            sale_order = request.env['sale.order'].sudo().browse(order_id)
            carrier_no = sale_order.name or ''
            # if order carrier is cne, use the carrier_no as the external PDF URL
            if not carrier_no:
                continue

            # base use pick id to get the extenal pdf url from ir_attachment
            pick_id = request.env['stock.picking'].sudo().search([('sale_id', '=', order_id)], limit=1)
            if not pick_id:
                continue
            pick_id = pick_id.id
            attachment = request.env['ir.attachment'].sudo().search([('res_id', '=', pick_id), ('res_model', '=', 'stock.picking')], limit=1)
            if not attachment:
                continue
            attachment_id = attachment.id
            attachment_data = request.env['ir.attachment'].sudo().browse(attachment_id)
            external_pdf_url = attachment_data.url or ''
            if not external_pdf_url:
                continue
            resp = requests.get(external_pdf_url)
            external_pdf = resp.content if resp.status_code == 200 else None

            if external_pdf:
                reader_attach = PdfReader(io.BytesIO(external_pdf))
                for page in reader_attach.pages:
                    writer.add_page(page)

        output = io.BytesIO()
        writer.write(output)
        merged_pdf = output.getvalue()

        filename = sale_order.name + '.pdf' if order_id else 'merged_report.pdf'

        # add a message to the order with the user who printed it
        user_id = request.env.user.id

        sale_order = request.env['sale.order'].sudo().browse(order_id)
        if not sale_order:
            return request.not_found()
        
        message = "批量打印的订单号: %s" % ', '.join([str(order_id) for order_id in id_list])
        message += "\n打印人: %s" % request.env.user.name
        message += "\n打印时间: %s" % fields.Datetime.now()
        sale_order.message_post(body=message)

        # update the order print time
        sale_order.write({'print_time': fields.Datetime.now()})

        pdfhttpheaders = [
            ('Content-Type', 'application/pdf'),
            ('Content-Length', len(merged_pdf)),
            ('Content-Disposition', 'inline; filename="%s"' % filename),
            ('Content-Transfer-Encoding', 'binary'),
        ]
        return request.make_response(merged_pdf, headers=pdfhttpheaders)