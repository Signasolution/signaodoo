from odoo import models

class ProductTemplate(models.Model):
    _inherit = 'product.template'

    def get_pricelist_items_by_quantity(self, pricelist=None):
        self.ensure_one()
        pricelist_id = (
            pricelist
            or self.env.context.get("pricelist")
            or self.env.user.partner_id.property_product_pricelist.id
        )
        pricelist = self.env['product.pricelist'].browse(pricelist_id)

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

from odoo import models, fields

class ProductTemplate(models.Model):
    _inherit = 'product.template'

    pricelist_qty_html = fields.Html(string="Tableau des prix", compute="_compute_pricelist_qty_html", sanitize=False)

    def _compute_pricelist_qty_html(self):
        for rec in self:
            items = rec.get_pricelist_items_by_quantity()
            if len(items) <= 1:
                rec.pricelist_qty_html = ""
            else:
                table = "<table class='table table-sm'><thead><tr><th>Quantité</th><th>Prix</th></tr></thead><tbody>"
                for item in items:
                    table += f"<tr><td>{item['min_quantity']}</td><td>{item['currency'].symbol} {item['price']:.2f}</td></tr>"
                table += "</tbody></table>"
                rec.pricelist_qty_html = table
