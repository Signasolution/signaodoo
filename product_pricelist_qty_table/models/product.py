from odoo import models

class ProductProduct(models.Model):
    _inherit = 'product.product'

    def get_pricelist_items_qty(self, pricelist):
        self.ensure_one()
        return self.env['product.pricelist.item'].search([
            ('pricelist_id', '=', pricelist.id),
            '|',
                '&',
                    ('applied_on', '=', '0_product_variant'),
                    ('product_id', '=', self.id),
                '&',
                    ('applied_on', '=', '1_product'),
                    ('product_tmpl_id', '=', self.product_tmpl_id.id),
            ('min_quantity', '>', 1),
        ], order='min_quantity')