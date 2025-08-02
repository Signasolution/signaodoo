from odoo import models, api


class ProductTemplate(models.Model):
    _inherit = 'product.template'

    @api.model
    def get_pricelist_items_by_quantity(self, pricelist, partner=None):
        """
        Build a price table including all discounts for each quantity threshold.
        It collects all quantity-based price items but computes the final price
        for each threshold via the pricelist engine (percent, fixed, formulas, etc.).
        """
        self.ensure_one()
        partner = partner or self.env.user.partner_id
        # Collect all quantity thresholds applicable to this product or template
        items = pricelist.item_ids.filtered(lambda item: (
            item.applied_on in ['0_product_variant', '1_product'] and
            (item.product_tmpl_id == self or item.product_variant_id.product_tmpl_id == self)
        ))
        # Unique, sorted thresholds
        qty_set = sorted({int(item.min_quantity) for item in items if item.min_quantity >= 0})
        # Build table by computing final price at each threshold
        result = []
        for qty in qty_set:
            # Compute price including all discount rules
            price = pricelist.get_product_price(self.product_variant_id, qty, partner)
            result.append({
                'min_quantity': qty,
                'price': price,
                'currency': pricelist.currency_id,
            })
        return result
