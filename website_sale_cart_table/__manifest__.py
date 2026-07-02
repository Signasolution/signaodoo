{
    'name': 'Panier personnalisé',
    'version': '18.0.2.0.0',
    'summary': "Aligne les colonnes de la page panier (/shop/cart) en conservant les lignes flex natives",
    'description': """
Réorganise l'affichage des lignes du panier eCommerce (website_sale) en
colonnes alignées (image, produit + référence/attributs, prix unitaire,
quantité, total, suppression), sans utiliser de <table> HTML : la structure
native en lignes flex (o_cart_product) de website_sale est conservée, seules
la quantité, le prix total et le bouton supprimer sont extraits de leur
wrapper commun pour devenir des colonnes indépendantes.

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
            'website_sale_cart_table/static/src/scss/cart_lines.scss',
        ],
    },
    'installable': True,
    'application': False,
    'auto_install': False,
}
