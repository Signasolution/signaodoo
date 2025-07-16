from odoo import models, fields, api

class ProductTemplate(models.Model):
    _inherit = 'product.template'

    def get_pricelist_items_by_quantity(self, pricelist=None):
        self.ensure_one()
        # Correction ici : récupération de la liste de prix depuis le contexte
        pricelist = (
            pricelist
            or self.env.context.get('pricelist')
            or self.env.user.partner_id.property_product_pricelist.id
        )
        pricelist = self.env['product.pricelist'].browse(pricelist)

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
