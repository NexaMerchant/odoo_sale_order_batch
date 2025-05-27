from odoo import models, fields

class BatchPrintLabelWizard(models.TransientModel):
    _name = 'batch.print.label.wizard'
    _description = 'Batch Print Label Confirmation Wizard'

    message = fields.Text(string="确认信息", readonly=True, default="您确定要为所选的订单批量打印面单吗？")

    def action_confirm_print(self):
        self.ensure_one()
        active_ids = self.env.context.get('active_ids', [])
        if not active_ids:
            return {'type': 'ir.actions.act_window_close'}

        report_url = '/report/pdf/sale_order_batch.report_batch_picking?ids=%s' % ','.join(map(str, active_ids))
        return {
            'type': 'ir.actions.act_url',
            'url': report_url,
            'target': 'new',
        }