# -*- coding: utf-8 -*-

from odoo import models, fields


class ProductMinPurchaseQty(models.Model):
    _name = 'product.min.purchase.qty'
    _description = "Quantité minimale d'achat par liste de prix"
    _order = 'pricelist_id, min_purchase_qty'

    product_tmpl_id = fields.Many2one(
        'product.template',
        string='Produit',
        required=True,
        ondelete='cascade',
        index=True,
    )
    pricelist_id = fields.Many2one(
        'product.pricelist',
        string='Liste de prix',
        required=True,
        ondelete='cascade',
    )
    min_purchase_qty = fields.Float(
        string="Qté min d'achat",
        required=True,
        default=1.0,
        digits='Product Unit of Measure',
        help="Quantité minimale que le client doit commander pour ce produit avec cette liste de prix.",
    )
