from odoo import models

class ProductTemplate(models.Model):
    _inherit = 'product.template'

    def get_pricelist_items_by_quantity(self):
        self.ensure_one()
        pricelist_id = self.env.context.get('pricelist')
        if not pricelist_id:
            return []
        items = self.env['product.pricelist.item'].search([
            ('pricelist_id', '=', pricelist_id),
            '|',
                '&', ('applied_on', '=', '0_product_variant'), ('product_id', '=', self.id),
                '&', ('applied_on', '=', '1_product'), ('product_tmpl_id', '=', self.product_tmpl_id.id),
            ('min_quantity', '>', 1),
        ], order='min_quantity')
        # Retourne dicts prêts pour QWeb
        return [{
            'min_quantity': item.min_quantity,
            'price': item.fixed_price,
            'currency': item.pricelist_id.currency_id,
        } for item in items]
