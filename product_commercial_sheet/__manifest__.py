# -*- coding: utf-8 -*-
{
    'name': 'Fiches Commerciales Produits',
    'version': '18.0.2.0.0',
    'category': 'Sales',
    'summary': 'Génération de fiches commerciales personnalisables pour les produits',
    'description': """
        Fiches Commerciales Produits
        ============================
        
        Ce module permet de créer des fiches commerciales personnalisables pour les produits.
        
        Fonctionnalités:
        * Bouton de génération de fiche dans le backend des produits
        * Champs configurables via Odoo Studio
        * Réorganisation facile des champs par glisser-déposer
        * Export PDF des fiches commerciales
        * Intégration native avec les produits Odoo
        
        Compatible avec Odoo Studio pour la personnalisation des vues.
    """,
    'author': 'Jean-Louis TROMPF',
    'website': 'https://www.votre-site.com',
    'depends': ['product', 'sale', 'base'],
    'data': [
        'security/ir.model.access.csv',
        'data/ir_ui_view.xml',
        'views/product_commercial_sheet_views.xml',
        'views/product_template_views.xml',
        'reports/product_commercial_sheet_report.xml',
    ],
    'i18n': [
        'i18n/fr.po',
        'i18n/en.po',
    ],
    'assets': {
        'web.assets_backend': [
            'product_commercial_sheet/static/src/css/commercial_sheet.css',
        ],
    },
    'installable': True,
    'application': False,
    'auto_install': False,
    'license': 'LGPL-3',
}
