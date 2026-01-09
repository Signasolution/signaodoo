# -*- coding: utf-8 -*-
from odoo import models

class SaleOrder(models.Model):
    _inherit = "sale.order"

    def _signa_get_quote_style(self):
        """Return the partner style value (Studio field) in a safe way.

        We avoid crashing if the Studio field does not exist (renamed/not installed yet),
        or if partner is missing.
        """
        self.ensure_one()
        partner = self.partner_id
        if not partner:
            return False
        field_name = "x_studio_style_de_devis"
        if field_name not in partner._fields:
            return False
        return partner[field_name] or False
