# Tableau de Prix Dégressifs pour Odoo

Module Odoo (18.0) qui affiche un tableau de prix par palier de quantité sur les pages produits de la boutique en ligne, et fournit un onglet de gestion dans la fiche produit pour configurer ces paliers, des remises par catégorie de client et des quantités minimales de commande.

## Fonctionnalités

### Site web (website_sale)

- Tableau de prix dégressifs affiché sur la page produit, calculé à partir des règles de la liste de prix (`product.pricelist.item`) applicable au visiteur/panier courant.
- Colonne **Remise** : pourcentage de remise de chaque palier **par rapport au prix du premier palier de la même liste de prix**. Le tableau montre donc uniquement le gain lié au volume ; la remise dont le client bénéficie déjà au titre de sa catégorie n'y est pas mélangée. La première ligne affiche « — », de même qu'un palier sans gain (ou plus cher, configuration anormale).
- Clic sur une ligne du tableau pour ajuster automatiquement le champ quantité.
- Mise en surbrillance de la ligne correspondant à la quantité saisie (saisie manuelle, boutons +/-, ou clic sur une ligne).
- Quantité minimale de commande par liste de prix : le champ quantité de la page produit est pré-rempli et contraint à ce minimum, avec un message d'avertissement si l'utilisateur tente de descendre en dessous (page produit et modales de variantes).
- Application côté serveur du minimum de commande à l'ajout au panier (`cart_update_json` surchargé) : la quantité est corrigée automatiquement et un avertissement est renvoyé au client, affiché sans rechargement de page via une interception de `fetch`/`XMLHttpRequest`.
- Contrainte de validation (`sale.order.line`) appliquée en backend uniquement (hors contexte site web, où le contrôleur gère déjà l'expérience utilisateur).

### Fiche produit (backend), onglet "Prix et quantités"

- **Paliers de prix dégressifs** : une ligne par liste de prix et palier de quantité (`min_quantity`), avec type de calcul Fixe ou Remise (%), et aperçu du prix résultant et de l'économie réalisée par rapport au prix de vente du produit. Attention : cette colonne « Économie % » du backend se calcule par rapport au prix de vente du produit, contrairement à la colonne « Remise » du site qui se calcule par rapport au premier palier.
- **Remises par catégorie de client** : définit une remise en % à appliquer aux paliers d'une liste de prix de base pour générer automatiquement les mêmes paliers dans une liste de prix cible (ex. installateurs = tarif public − 15 %). Le bouton *Générer les tarifs* crée ou met à jour les règles correspondantes dans la liste cible.
- **Quantités minimales d'achat** : quantité minimale par liste de prix (0 = pas de restriction). Le bouton *Synchroniser les listes de prix* crée une ligne à 0 pour chaque liste de prix active qui n'en a pas encore.

### Multi-site

Le module est conçu pour fonctionner correctement sur une installation Odoo multi-site (plusieurs sites web partageant la même base de données, chacun avec ses propres listes de prix). La résolution de la liste de prix (`ProductTemplate._get_price_break_pricelist`) suit en priorité la liste de prix réellement attachée au panier du visiteur (`website.sale_get_order().pricelist_id`), la même que celle utilisée pour l'application du minimum de commande — évitant qu'un site récupère par erreur la liste de prix (et donc les règles) d'un autre site.

## Règles prises en compte dans le tableau

`ProductTemplate._get_price_break_rules` retient les règles de la liste de prix ayant `min_quantity > 0` et portant sur : ce modèle de produit, une de ses variantes, sa catégorie (ou une catégorie parente), ou aucun produit en particulier (règle globale de la liste).

## Limitation connue

Le type de calcul **Formule** (`compute_price = 'formula'`) n'est **pas supporté** par le module : les méthodes qui calculent le tableau de prix et l'aperçu backend (`ProductTemplate._get_price_break_rules`, `ProductPricelistItem._compute_price_computed`) ne reconnaissent que Fixe et Remise (%) ; une règle en Formule retombe silencieusement sur le prix plein, sans remise. N'utilisez pas ce type de calcul pour les paliers gérés par ce module.

## Installation

1. Copier le dossier `price_break_table` dans les addons de l'instance Odoo.
2. Mettre à jour la liste des modules, puis installer (ou mettre à niveau après une mise à jour du code) "Tableau de Prix Dégressifs".
3. Configurer les paliers de prix depuis la fiche produit (onglet "Prix et quantités") ou depuis Ventes > Configuration > Listes de prix.

## Structure du module

```
price_break_table/
├── __init__.py
├── __manifest__.py
├── controllers/
│   └── main.py                        # Surcharge cart_update_json pour le minimum de commande
├── models/
│   ├── product_template.py            # get_price_break_table_data, génération des tarifs par remise
│   ├── product_pricelist_item.py      # Champs calculés prix résultant / économie %
│   ├── product_min_purchase_qty.py    # Quantité min d'achat par liste de prix
│   ├── product_pricelist_discount.py  # Remise par catégorie de client (liste base -> liste cible)
│   └── sale_order_line.py             # Contrainte de minimum de commande en backend
├── security/
│   └── ir.model.access.csv
├── static/src/
│   ├── css/price_break_table.css
│   └── js/
│       ├── price_break_table.js        # Page produit : minimum de commande + tableau
│       └── price_break_cart_warning.js # Toast d'avertissement à l'ajout au panier
└── views/
    ├── product_backend_views.xml      # Onglet "Prix et quantités" sur la fiche produit
    └── website_sale_templates.xml     # Markup du tableau et des contraintes de quantité
```

Le JS et le CSS sont chargés via `web.assets_frontend` sur toutes les pages du site ; `price_break_table.js` ne fait rien tant que le markup de la page produit n'est pas présent.

## Dépendances

`product`, `sale`, `website_sale`.

## Licence

LGPL-3.
