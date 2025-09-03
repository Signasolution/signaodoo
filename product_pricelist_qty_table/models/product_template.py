from odoo import models

class ProductTemplate(models.Model):
    _inherit = 'product.template'

    def get_pricelist_items_by_quantity(self):
        self.ensure_one()
        pricelist_id = self.env.context.get('pricelist')
        if not pricelist_id:
            website = self.env['website'].get_current_website()
            pricelist = website and website._get_current_pricelist() or False
            pricelist_id = pricelist.id if pricelist else False
        if not pricelist_id:
            return []
        product = self.product_variant_id
        items = self.env['product.pricelist.item'].search([
            ('pricelist_id', '=', pricelist_id),
            '|',
                '&', ('applied_on', '=', '0_product_variant'), ('product_id', '=', product.id),
                '&', ('applied_on', '=', '1_product'), ('product_tmpl_id', '=', self.id),
            ('min_quantity', '>', 1),
        ], order='min_quantity')
        return [{
            'min_quantity': int(item.min_quantity or 0),
            'price': float(item.fixed_price or 0.0),
            'currency': item.pricelist_id.currency_id,
        } for item in items]