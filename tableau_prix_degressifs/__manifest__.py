{
    "name": "Product Pricelist Quantity Table",
    "version": "1.0",
    "depends": ["website_sale"],
    "category": "Website",
    "summary": "Display quantity-based price table on product pages",
    "data": [
        "views/product_template_inherit.xml"
    ],
    "assets": {
        "web.assets_frontend": [
            "product_pricelist_qty_table/static/src/js/pricelist_qty_table.js",
            "product_pricelist_qty_table/static/src/css/pricelist_qty_table.css",
        ]
    },
    "installable": True,
    "application": False,
}
