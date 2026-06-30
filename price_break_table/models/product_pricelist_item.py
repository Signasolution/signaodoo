# -*- coding: utf-8 -*-

from odoo import models, fields, api


class ProductPricelistItem(models.Model):
    _inherit = 'product.pricelist.item'

    min_purchase_qty = fields.Float(
        string='Qté min d\'achat',
        digits='Product Unit of Measure',
        default=0.0,
        help="Quantité minimale d'unités que le client doit acheter pour bénéficier de ce tarif.",
    )
    price_computed = fields.Float(
        string='Prix résultant',
        compute='_compute_price_computed',
        digits='Product Price',
    )
    savings_percent = fields.Float(
        string='Économie %',
        compute='_compute_price_computed',
        digits=(5, 1),
    )

    @api.depends('compute_price', 'fixed_price', 'percent_price', 'product_tmpl_id.list_price')
    def _compute_price_computed(self):
        for item in self:
            list_price = item.product_tmpl_id.list_price or 0.0
            if item.compute_price == 'fixed':
                computed = item.fixed_price
            elif item.compute_price == 'percentage':
                computed = list_price * (1.0 - item.percent_price / 100.0)
            else:
                computed = list_price
            item.price_computed = computed
            item.savings_percent = (
                (list_price - computed) / list_price * 100.0
                if list_price else 0.0
            )
