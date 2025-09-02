from odoo import models

class ProductTemplate(models.Model):
    _inherit = "product.template"

    def get_pricelist_items_qty(self):
        self.ensure_one()
        product = self.product_variant_id or self
        pricelist = self.env.context.get('pricelist')

        if not pricelist:
            return []

        pricelist = self.env['product.pricelist'].browse(pricelist)
        items = pricelist.item_ids.filtered(lambda r: (
            r.applied_on in ['0_product_variant', '1_product'] and
            (
                r.product_id == product or
                r.product_tmpl_id == self
            ) and
            r.min_quantity > 1
        ))

        result = []
        for item in sorted(items, key=lambda r: r.min_quantity):
            result.append({
                'min_quantity': int(item.min_quantity),
                'price': item.fixed_price or 0.0,
                'currency': item.currency_id,
            })
        return result
