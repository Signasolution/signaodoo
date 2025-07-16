{
    'name': 'Product Price Table',
    'version': '1.0',
    'category': 'Website',
    'summary': 'Affiche un tableau de prix dégressifs sur les pages produit',
    'depends': ['website_sale', 'product'],
    'data': [
        'views/product_template_price_table.xml',
    ],
    'assets': {
        'web.assets_frontend': [
            'product_price_table/static/src/js/price_table.js',
        ],
    },
}