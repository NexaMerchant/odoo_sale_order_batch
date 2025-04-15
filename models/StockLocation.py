from odoo import models

class StockLocation(models.Model):
    _inherit = 'stock.location'

    def _get_complete_name(self):
        names = []
        location = self
        while location:
            names.append(location.name or '')
            location = location.location_id
        # 这里将分隔符从 '/' 改为 ' - '
        return ' - '.join(reversed(names))