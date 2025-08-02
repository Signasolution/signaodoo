from odoo import models, api


class ProductTemplate(models.Model):
    _inherit = 'product.template'

    @api.model
    def get_pricelist_items_by_quantity(self, pricelist):
        """
        Return all pricelist items for this product template or its variants
        that have a minimum quantity > 0, ignoring application priority.
        """
        self.ensure_one()
        # Fetch all items on this pricelist that apply to this template or its variants
        items = pricelist.item_ids.filtered(lambda item: (
            # Applied on template or product
            item.applied_on in ['0_product_variant', '1_product'] and
            # Belongs to this template or one of its variants
            (item.product_tmpl_id == self or item.product_variant_id.product_tmpl_id == self) and
            # Only items with quantity thresholds
            item.min_quantity > 0
        ))
        # Sort by ascending min_quantity
        items = items.sorted(key=lambda i: i.min_quantity)
        # Build a list of dicts for QWeb
        result = []
        for item in items:
            result.append({
                'min_quantity': item.min_quantity,
                'price': item.fixed_price,
                'currency': item.currency_id,
            })
        return result
