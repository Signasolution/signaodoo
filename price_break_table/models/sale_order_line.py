# -*- coding: utf-8 -*-

from odoo import models, api, _
from odoo.exceptions import ValidationError


class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'

    @api.constrains('product_id', 'product_uom_qty')
    def _check_min_purchase_qty(self):
        for line in self:
            if not line.product_id or not line.order_id.pricelist_id:
                continue
            rule = self.env['product.min.purchase.qty'].search([
                ('product_tmpl_id', '=', line.product_id.product_tmpl_id.id),
                ('pricelist_id', '=', line.order_id.pricelist_id.id),
            ], limit=1)
            if rule and line.product_uom_qty < rule.min_purchase_qty:
                raise ValidationError(_(
                    "La quantité minimale d'achat pour « %(product)s » "
                    "avec la liste de prix « %(pricelist)s » est de %(qty)s unité(s).",
                    product=line.product_id.display_name,
                    pricelist=line.order_id.pricelist_id.name,
                    qty=rule.min_purchase_qty,
                ))
