# -*- coding: utf-8 -*-

from odoo import models, fields, api


class ProductPricelistDiscount(models.Model):
    _name = 'product.pricelist.discount'
    _description = "Remise par catégorie de client"
    _order = 'base_pricelist_id, target_pricelist_id'
    _sql_constraints = [(
        'unique_product_pricelist_pair',
        'UNIQUE(product_tmpl_id, base_pricelist_id, target_pricelist_id)',
        "Une remise existe déjà pour cette combinaison liste de base / liste cible.",
    )]

    product_tmpl_id = fields.Many2one(
        'product.template',
        required=True,
        ondelete='cascade',
        index=True,
    )
    base_pricelist_id = fields.Many2one(
        'product.pricelist',
        string='Liste de prix de base',
        required=True,
        ondelete='restrict',
    )
    target_pricelist_id = fields.Many2one(
        'product.pricelist',
        string='Liste de prix cible',
        required=True,
        ondelete='restrict',
    )
    discount_percent = fields.Float(
        string='Remise %',
        digits=(5, 2),
        default=0.0,
    )
    tier_preview = fields.Char(
        string='Aperçu des paliers',
        compute='_compute_tier_preview',
    )

    @api.depends('base_pricelist_id', 'discount_percent', 'product_tmpl_id.list_price',
                 'product_tmpl_id.price_break_item_ids.fixed_price',
                 'product_tmpl_id.price_break_item_ids.percent_price',
                 'product_tmpl_id.price_break_item_ids.min_quantity')
    def _compute_tier_preview(self):
        PricelistItem = self.env['product.pricelist.item']
        for rec in self:
            if not rec.base_pricelist_id or not rec.product_tmpl_id:
                rec.tier_preview = ''
                continue
            items = PricelistItem.search([
                ('pricelist_id', '=', rec.base_pricelist_id.id),
                ('product_tmpl_id', '=', rec.product_tmpl_id.id),
                ('min_quantity', '>', 0),
            ], order='min_quantity')
            if not items:
                rec.tier_preview = "Aucun palier sur la liste de base"
                continue
            currency_symbol = rec.base_pricelist_id.currency_id.symbol or ''
            parts = []
            for item in items:
                base = rec._get_item_base_price(item, rec.product_tmpl_id.list_price)
                price = base * (1.0 - rec.discount_percent / 100.0)
                parts.append("≥%g : %s%.2f" % (item.min_quantity, currency_symbol, price))
            rec.tier_preview = '  |  '.join(parts)

    def _get_item_base_price(self, item, list_price):
        if item.compute_price == 'fixed':
            return item.fixed_price
        if item.compute_price == 'percentage':
            return list_price * (1.0 - item.percent_price / 100.0)
        return list_price
