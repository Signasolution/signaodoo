# -*- coding: utf-8 -*-
{
    'name': "Filigrane des Images Produits par Site Web",
    'summary': "Incruste un filigrane (texte ou image) sur les images des produits, avec une configuration différente par site web.",
    'description': """
Filigrane des Images Produits par Site Web
===========================================

Permet de configurer, pour chaque site web (multi-site Odoo), un filigrane
appliqué sur les images des produits (fiche produit et variantes) :

* Filigrane texte ou image, avec bascule facile entre les deux modes.
* 9 positions (centre, coins, bords).
* Rotation, opacité et ratio de redimensionnement configurables.
* Prévisualisation en temps réel sur une image produit d'exemple.
* Filigranage de toutes les images de chaque produit : image principale et
  images supplémentaires de la galerie (product.image), modèle et variantes.
* Application en lot à tous les produits et variantes du site.
* Filigrane image au format PNG (transparence RGBA) ou JPEG (fond opaque).
* Images produits supportées : PNG, JPEG/JPG (et tout format reconnu par
  Pillow), avec gestion de l'orientation EXIF.
* Police, couleur et taille configurables pour les filigranes texte.

L'application est destructive : les images du produit (image_1920 /
image_variant_1920 et les images de galerie product.image) sont directement
réécrites par le lot d'application. Une sauvegarde de chaque image d'origine
est conservée pour permettre une réapplication propre (sans effet cumulatif)
ou une restauration.
    """,
    'version': '18.0.1.0.0',
    'category': 'Website/Website',
    'author': 'Jean-Louis TROMPF',
    'license': 'LGPL-3',
    'depends': ['website_sale'],
    'data': [
        'security/ir.model.access.csv',
        'views/website_watermark_config_views.xml',
        'views/product_template_views.xml',
    ],
    'installable': True,
    'application': False,
    'auto_install': False,
}
