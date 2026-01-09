# -*- coding: utf-8 -*-
from odoo import models

class SaleOrder(models.Model):
    _inherit = "sale.order"

    def _signa_get_quote_style(self):
        """Return partner style value used to route the quote layout.

        Safe by design:
        - if the Studio field is not present yet, return False (fallback to standard layout)
        - if empty, return False
        """
        self.ensure_one()
        partner = self.partner_id
        if not partner:
            return False
        field = partner._fields.get("x_studio_style_de_devis")
        if not field:
            return False
        return partner["x_studio_style_de_devis"] or False
