# -*- coding: utf-8 -*-
{
    'name': "Référence produit dans les listes eCommerce",
    'summary': "Affiche la référence interne du produit devant son nom sur les pages de liste du site eCommerce.",
    'description': """
Ajoute la référence interne (default_code) devant le nom du produit, sous la
forme "(référence) Nom du produit", sur toutes les vues de type liste de
produits du site eCommerce (page boutique, catégories, listes de souhaits,
snippets "produits recommandés", etc.).

Si un produit n'a pas de référence renseignée, seul le nom est affiché
(comportement inchangé).
    """,
    'version': '18.0.1.0.0',
    'category': 'Website/Website',
    'author': 'Jean-Louis',
    'license': 'LGPL-3',
    'depends': ['website_sale'],
    'data': [
        'views/website_sale_templates.xml',
    ],
    'installable': True,
    'application': False,
    'auto_install': False,
}
