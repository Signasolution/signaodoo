{
    "name": "Product Pricelist Qty Table",
    "version": "1.0",
    "depends": ["website_sale", "product"],
    "category": "Website",
    "summary": "Display quantity-based price breaks on website product pages",
    "data": [
        "views/product_template_inherit.xml"
    ],
    "installable": True,
    "auto_install": False
    "assets": {
        "web.assets_frontend": [
            "product_pricelist_qty_table/static/src/js/pricelist_table.js"
        ]
    },
}
