# -*- coding: utf-8 -*-
{
    'name': 'Amélioration Navigation Site Web',
    'version': '18.0.1.0.0',
    'category': 'Website',
    'summary': 'Améliore la navigation et la lisibilité des menus de catégories',
    'description': """
        Amélioration Navigation Site Web
        ================================
        
        Ce module améliore la navigation sur le site web Odoo en :
        * Ajoutant un fil d'Ariane (breadcrumb) intelligent
        * Mettant en évidence l'élément de menu actif
        * Améliorant la hiérarchie visuelle des catégories
        * Ajoutant des effets interactifs pour une meilleure UX
        
        Fonctionnalités:
        * Fil d'Ariane automatique basé sur la hiérarchie des catégories
        * Surbrillance de l'élément de menu actif
        * Amélioration de la lisibilité des sous-menus
        * Effets hover et transitions fluides
        * Compatible avec tous les thèmes Odoo
    """,
    'author': 'Jean-Louis TROMPF',
    'website': 'https://www.votre-site.com',
    'depends': ['website', 'website_sale'],
    'data': [
        'views/website_templates_simple.xml',
    ],
    'assets': {
        'web.assets_frontend': [
            'website_navigation_enhancement/static/src/css/navigation_enhancement_simple.css',
            'website_navigation_enhancement/static/src/js/navigation_enhancement_simple.js',
        ],
    },
    'installable': True,
    'application': False,
    'auto_install': False,
    'license': 'LGPL-3',
}
