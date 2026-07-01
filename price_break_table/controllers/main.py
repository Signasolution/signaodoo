# -*- coding: utf-8 -*-

from odoo import http, _
from odoo.http import request
from odoo.addons.website_sale.controllers.main import WebsiteSale


class WebsiteSalePriceBreak(WebsiteSale):

    @http.route()
    def cart_update_json(self, product_id, line_id=None, add_qty=None, set_qty=None, **kw):
        """Bloque la mise à jour du panier si la quantité est inférieure au minimum défini."""
        product = request.env['product.product'].sudo().browse(int(product_id))
        if product.exists():
            pricelist = self._get_current_pricelist_compat()
            if pricelist:
                min_rule = request.env['product.min.purchase.qty'].sudo().search([
                    ('product_tmpl_id', '=', product.product_tmpl_id.id),
                    ('pricelist_id', '=', pricelist.id),
                    ('min_purchase_qty', '>', 0),
                ], limit=1)
                if min_rule:
                    qty_to_check = float(set_qty if set_qty is not None else (add_qty or 1))
                    if qty_to_check < min_rule.min_purchase_qty:
                        return {
                            'warning': _(
                                "La quantité minimale de commande pour ce produit est de %g unité(s). "
                                "Veuillez ajuster votre quantité.",
                                min_rule.min_purchase_qty,
                            ),
                        }
        return super().cart_update_json(
            product_id, line_id=line_id, add_qty=add_qty, set_qty=set_qty, **kw
        )

    def _get_current_pricelist_compat(self):
        """Récupère la liste de prix courante de façon compatible avec Odoo 18."""
        try:
            order = request.website.sale_get_order(force_create=False)
            if order and order.pricelist_id:
                return order.pricelist_id
        except Exception:
            pass
        try:
            return request.website.pricelist_id
        except Exception:
            pass
        return None
