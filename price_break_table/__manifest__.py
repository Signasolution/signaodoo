# -*- coding: utf-8 -*-
{
    'name': 'Tableau de Prix Dégressifs',
    'version': '18.0.2.0.0',
    'category': 'Sales',
    'summary': 'Affiche un tableau interactif des prix dégressifs par quantité sur les pages produits',
    'description': """
        Tableau de Prix Dégressifs
        ==========================
        
        Ce module ajoute un tableau interactif sur toutes les pages produits
        qui affiche les prix dégressifs par quantité.
        
        Fonctionnalités:
        * Affichage automatique des prix par quantité
        * Support des listes de prix multiples avec priorité Odoo
        * Interaction bidirectionnelle: clic sur ligne = mise à jour quantité
        * Surbrillance automatique de la ligne correspondant à la quantité
        * Intégration native dans les vues e-commerce et backend
    """,
    'author': 'Votre Nom',
    'website': 'https://www.votre-site.com',
    'depends': ['product', 'sale', 'website_sale'],
    'data': [
        'security/ir.model.access.csv',
        'views/product_template_views.xml',
        'views/website_sale_templates.xml',
    ],
    'assets': {
        'web.assets_frontend': [
            'price_break_table/static/src/js/price_break_table.js',
            'price_break_table/static/src/css/price_break_table.css',
        ],
        'web.assets_backend': [
            'price_break_table/static/src/js/price_break_table.js',
            'price_break_table/static/src/css/price_break_table.css',
        ],
    },
    'installable': True,
    'application': False,
    'auto_install': False,
    'license': 'LGPL-3',
}

