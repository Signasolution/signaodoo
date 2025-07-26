from odoo import models, api

class AccountMoveLine(models.Model):
    _inherit = 'account.move.line'

    @api.onchange('move_id.partner_id')
    def _onchange_partner_discount(self):
        if self.move_id.move_type in ['out_invoice', 'out_refund']:
            partner = self.move_id.partner_id
            if partner.type_client_id:
                self.discount = partner.type_client_id.discount_rate
