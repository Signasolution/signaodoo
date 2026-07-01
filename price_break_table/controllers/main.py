# -*- coding: utf-8 -*-

from odoo import http, _
from odoo.http import request
from odoo.addons.website_sale.controllers.main import WebsiteSale


class WebsiteSalePriceBreak(WebsiteSale):

    @http.route()
    def cart_update_json(self, product_id, line_id=None, add_qty=None, set_qty=None, **kw):
        """
        Si la quantité demandée est inférieure au minimum défini, on la corrige
        automatiquement au minimum et on ajoute un avertissement dans la réponse.
        La suppression (set_qty=0) est toujours autorisée.
        """
        # Suppression d'une ligne du panier → toujours autoriser
        if set_qty is not None and float(set_qty) == 0:
            return super().cart_update_json(
                product_id, line_id=line_id, add_qty=add_qty, set_qty=set_qty, **kw
            )

        product = request.env['product.product'].sudo().browse(int(product_id))
        warning_msg = None

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
                        # Correction silencieuse au minimum
                        set_qty = min_rule.min_purchase_qty
                        add_qty = None
                        warning_msg = _(
                            "La quantité minimale de commande pour ce produit est de %g unité(s).",
                            min_rule.min_purchase_qty,
                        )

        result = super().cart_update_json(
            product_id, line_id=line_id, add_qty=add_qty, set_qty=set_qty, **kw
        )

        if warning_msg and isinstance(result, dict):
            result['warning'] = warning_msg

        return result

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
