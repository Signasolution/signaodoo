from odoo import models

class ProductProduct(models.Model):
    _inherit = 'product.product'

    def get_pricelist_items(self):
        self.ensure_one()
        pricelist = self.env['product.pricelist'].get_current_pricelist()
        return self.env['product.pricelist.item'].search([
            ('pricelist_id', '=', pricelist.id),
            ('applied_on', '=', '1_product'),
            ('product_id', '=', self.id)
        ])
