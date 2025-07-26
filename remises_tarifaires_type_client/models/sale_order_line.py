from odoo import models, api

class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'

    @api.onchange('order_id.partner_id')
    def _onchange_partner_discount(self):
        if self.order_id.partner_id.type_client_id:
            self.discount = self.order_id.partner_id.type_client_id.discount_rate
