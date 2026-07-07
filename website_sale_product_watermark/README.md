# Filigrane des Images Produits par Site Web

Module Odoo (18.0) qui incruste un filigrane (texte ou image) sur les images des produits (fiche produit et variantes), avec une configuration **différente par site web** sur une installation multi-site Odoo.

## Fonctionnalités

- Filigrane texte ou image, bascule facile entre les deux modes (`Site Web > Site > Filigranes`).
- 9 positions : centre, 4 coins, 4 bords, avec marge configurable.
- Rotation (-180° à 180°), opacité (0-255) et ratio de redimensionnement (par rapport à la largeur de l'image cible).
- Prévisualisation en temps réel sur une image produit d'exemple, sans toucher aux vraies données.
- Police, couleur et taille pour les filigranes texte (police personnalisée possible via upload d'un fichier .ttf).
- Filigrane image au format PNG (transparence RGBA) ou JPEG (fond opaque, sans détourage).
- Images produits : PNG, JPEG/JPG (et tout format reconnu par Pillow), orientation EXIF respectée.
- Application en lot à tous les templates produits et variantes rattachés au site,
  depuis l'écran de configuration du filigrane.
- Onglet "Filigrane" sur la fiche produit (boutons "Appliquer le filigrane" et
  "Restaurer l'image d'origine", état du filigranage) — voir "Note technique"
  ci-dessous pour le choix d'héritage de vue.

## Fonctionnement (application destructive)

Le bouton "Appliquer à tous les produits du site" **réécrit directement** le champ image du produit (`image_1920`, ou `image_variant_1920` pour les variantes qui ont leur propre image). Ce n'est pas un rendu à la volée : l'image stockée en base est modifiée.

Conséquence assumée : un produit rattaché à plusieurs sites ne peut porter qu'un seul filigrane à la fois (le dernier appliqué). Pour limiter ce risque, le lot ne traite **que les produits dont le champ `Site Web` (`website_id`) pointe explicitement vers le site traité** — les produits visibles sur tous les sites (`website_id` vide) sont ignorés par défaut.

Pour éviter tout effet cumulatif (filigrane appliqué sur un filigrane déjà présent), chaque produit conserve une **sauvegarde de son image d'origine** avant le premier filigranage :

- Toute réapplication (changement de configuration puis nouveau passage du lot) repart toujours de cette sauvegarde.
- Si un utilisateur remplace manuellement l'image d'un produit déjà filigrané, la sauvegarde est invalidée automatiquement : la nouvelle image devient la nouvelle référence "originale" pour le prochain filigranage.

## Note technique (héritage de vue)

L'onglet "Filigrane" hérite de `product.product_template_only_form_view` (la vue
PRIMAIRE réservée à la fiche « Modèle de produit ») et **non** de la vue de base
`product.product_template_form_view` partagée avec la fiche variante. Ce choix
est délibéré : sur une installation avec des personnalisations Odoo Studio (cas
fréquent), la vue de base partagée est un point d'extension fragile — un ajout
par un module tiers peut décaler la structure et faire échouer une vue Studio
qui dépend d'une position précise. En ciblant la vue « fiche produit uniquement »
et en ajoutant une page nommée en fin de notebook, l'onglet n'impacte ni les
fiches variantes ni les index positionnels utilisés par d'éventuelles vues
Studio.

Les méthodes `action_apply_watermark` et `action_restore_original_image` existent
aussi bien sur `product.template` que sur `product.product`, donc elles restent
utilisables sur les variantes via une action serveur ou une automatisation, même
sans onglet dédié sur la fiche variante.

## Installation

1. Copier le dossier `website_sale_product_watermark` dans les addons de l'instance Odoo.
2. Mettre à jour la liste des modules, puis installer "Filigrane des Images Produits par Site Web".
3. Configurer un filigrane par site depuis `Site Web > Site > Filigranes`.
4. Lancer "Appliquer à tous les produits du site" depuis la fiche de configuration.

## Structure du module

```
website_sale_product_watermark/
├── __init__.py
├── __manifest__.py
├── models/
│   ├── __init__.py
│   ├── watermark_service.py       # logique Pillow pure (aucune dépendance ORM)
│   ├── website_watermark_config.py
│   ├── product_template.py
│   └── product_product.py
├── views/
│   └── website_watermark_config_views.xml
├── security/
│   └── ir.model.access.csv
└── static/
    ├── description/icon.png
    ├── img/sample_product.png     # image de démonstration pour la prévisualisation
    └── fonts/                     # polices libres de droits embarquées
```
