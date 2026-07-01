# -*- coding: utf-8 -*-

from odoo import models, api, _
from odoo.exceptions import ValidationError


class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'

    @api.constrains('product_id', 'product_uom_qty')
    def _check_min_purchase_qty(self):
        # Sur le site web, le contrôleur gère déjà la contrainte avec un bon UX.
        # On n'applique la validation stricte qu'en backend.
        if self.env.context.get('website_id'):
            return
        for line in self:
            if not line.product_id or not line.order_id.pricelist_id:
                continue
            rule = self.env['product.min.purchase.qty'].search([
                ('product_tmpl_id', '=', line.product_id.product_tmpl_id.id),
                ('pricelist_id', '=', line.order_id.pricelist_id.id),
            ], limit=1)
            if rule and rule.min_purchase_qty > 0 and line.product_uom_qty < rule.min_purchase_qty:
                raise ValidationError(_(
                    "La quantité minimale de commande pour « %(product)s » "
                    "est de %(qty)s unité(s).",
                    product=line.product_id.display_name,
                    qty=rule.min_purchase_qty,
                ))
