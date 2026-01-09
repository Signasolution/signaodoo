# -*- coding: utf-8 -*-
from odoo import models

class SaleOrder(models.Model):
    _inherit = "sale.order"

    def _signa_get_quote_style(self):
        """Return the style string from partner. Safe if Studio field is missing."""
        self.ensure_one()
        partner = self.partner_id
        field_name = "x_studio_style_de_devis"
        if not partner:
            return False
        if field_name not in partner._fields:
            return False
        return partner[field_name] or False
