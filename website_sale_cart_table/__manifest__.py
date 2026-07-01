{
    'name': 'Panier personnalisé',
    'version': '18.0.1.0.0',
    'summary': "Affiche la page panier (/shop/cart) sous forme de tableau HTML",
    'description': """
Réorganise l'affichage des lignes du panier eCommerce (website_sale) en un
tableau HTML classique (image, produit, prix unitaire, quantité, total,
suppression) au lieu de la mise en page en lignes flex par défaut d'Odoo 18.

Aucune logique métier n'est réécrite : tous les champs, contrôles de
quantité et boutons de suppression existants sont simplement déplacés dans
la nouvelle structure via héritage xpath (position="move"), le JavaScript
standard de website_sale continue donc de fonctionner sans modification.
""",
    'category': 'Website/Website',
    'author': 'Jean-Louis TROMPF',
    'website': 'https://www.votre-site.com',
    'license': 'LGPL-3',
    'depends': ['website_sale'],
    'data': [
        'views/cart_templates.xml',
    ],
    'assets': {
        'web.assets_frontend': [
            'website_sale_cart_table/static/src/scss/cart_table.scss',
        ],
    },
    'installable': True,
    'application': False,
    'auto_install': False,
}
