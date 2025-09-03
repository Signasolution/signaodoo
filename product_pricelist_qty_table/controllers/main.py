from odoo import http
from odoo.http import request

class ProductController(http.Controller):
    @http.route(['/product_pricelist_qty_table/<model("product.template"):product>'], type='json', auth="public", website=True)
    def product_pricelist_qty_table(self, product):
        pricelist = request.website.get_current_pricelist()
        product_variant = product.product_variant_id or product
        pricelist_items = product_variant.get_pricelist_items_qty(pricelist)
        return request.render("product_pricelist_qty_table.product_pricelist_table", {
            "pricelist_items": pricelist_items,
            "pricelist": pricelist,
        })