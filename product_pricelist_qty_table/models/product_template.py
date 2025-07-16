from odoo import models, fields, api

class ProductTemplate(models.Model):
    _inherit = 'product.template'

    def get_pricelist_items_by_quantity(self, pricelist=None):
        self.ensure_one()
        pricelist = pricelist or self.env['product.pricelist'].get_partner_pricelist(self.env.user.partner_id)

        product_variants = self.product_variant_ids
        items = self.env['product.pricelist.item'].search([
            ('pricelist_id', '=', pricelist.id),
            '|',
            ('product_id', 'in', product_variants.ids),
            '&',
            ('applied_on', '=', '1_product'),
            ('product_tmpl_id', '=', self.id),
        ])

        results = []
        for item in items.sorted(key=lambda r: r.min_quantity):
            currency = pricelist.currency_id
            price = item.fixed_price if item.compute_price == 'fixed' else item.price
            results.append({
                'min_quantity': item.min_quantity,
                'price': price,
                'currency': currency,
            })
        return results
