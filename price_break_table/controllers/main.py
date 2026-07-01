# -*- coding: utf-8 -*-

from odoo import http, _
from odoo.http import request
from odoo.addons.website_sale.controllers.main import WebsiteSale


class WebsiteSalePriceBreak(WebsiteSale):

    @http.route()
    def cart_update_json(self, product_id, line_id=None, add_qty=None, set_qty=None, **kw):
        """Bloque l'ajout au panier si la quantité est inférieure au minimum défini."""
        product = request.env['product.product'].sudo().browse(int(product_id))
        if product.exists():
            pricelist = request.website.get_current_pricelist()
            min_rule = request.env['product.min.purchase.qty'].sudo().search([
                ('product_tmpl_id', '=', product.product_tmpl_id.id),
                ('pricelist_id', '=', pricelist.id),
                ('min_purchase_qty', '>', 0),
            ], limit=1)
            if min_rule:
                # Pour un ajout initial, on vérifie add_qty ; pour une mise à jour, set_qty
                qty_to_check = float(set_qty if set_qty is not None else (add_qty or 1))
                if qty_to_check < min_rule.min_purchase_qty:
                    return {
                        'warning': _(
                            "La quantité minimale de commande pour « %s » est de %g unité(s). "
                            "Veuillez ajuster votre quantité.",
                            product.display_name,
                            min_rule.min_purchase_qty,
                        ),
                    }
        return super().cart_update_json(
            product_id, line_id=line_id, add_qty=add_qty, set_qty=set_qty, **kw
        )
