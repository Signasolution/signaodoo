
from odoo import http
from odoo.http import request
from odoo.tools.misc import formatLang

class WebsiteProductController(http.Controller):

    @http.route(['/product_pricelist_qty_table/<model("product.product"):product>'], type='json', auth="public", website=True)
    def get_pricelist_table(self, product, **kwargs):
        pricelist = request.website.get_current_pricelist()
        quantity_steps = [1, 5, 10, 20, 50, 100]

        pricelist_items = []
        for qty in quantity_steps:
            price = product._get_display_price(product, pricelist=pricelist, quantity=qty)
            pricelist_items.append({
                'min_quantity': qty,
                'price': price,
                'currency': pricelist.currency_id,
            })

        return request.env['ir.ui.view']._render_template("product_pricelist_qty_table.product_pricelist_table", {
            'pricelist_items': pricelist_items or [],
            'product': product,
            'formatLang': lambda value, **kw: formatLang(request.env, value, currency_obj=pricelist.currency_id),
        })
