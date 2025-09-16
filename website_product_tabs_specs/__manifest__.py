# -*- coding: utf-8 -*-















# NOTE: Tested for Odoo 18.3 Enterprise context (website_sale). Keep dependencies minimal.







{'name': 'Website Product Specs Tabs',
 'summary': 'Ajoute un tableau à onglets (Caractéristiques / Dimensions) sur la page produit',
 'version': '18.3.1.0',
 'author': 'Jean-Louis T. & ChatGPT',
 'license': 'LGPL-3',
 'category': 'Website/Website',
 'depends': ['website_sale'],
 'data': ['views/website_sale_templates.xml'],
 'assets': {},  # pas d'assets spécifiques, Bootstrap 5 suffit
 'installable': True,
 'application': False,
 'auto_install': False}