{
    "name": "Product Pricelist Qty Table",
    "version": "1.1",
    "depends": ["website_sale", "product"],
    "category": "Website",
    "summary": "Affiche un tableau des prix dégressifs sur les pages produit du site web",
    "description": "Ce module affiche un tableau dynamique des prix dégressifs selon la quantité sur les fiches produit du site web Odoo.",
    "data": [
        "views/product_template_inherit.xml"
    ],
    "assets": {
        "web.assets_frontend": [
            "product_pricelist_qty_table/static/src/js/pricelist_table.js"
        ]
    },
    "installable": True,
    "application": False,
    "auto_install": False
}
