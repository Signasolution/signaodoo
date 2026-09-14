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

### Cartes produit des pages de liste

Sur la boutique, les pages de catégorie, les listes de souhaits et les snippets « produits recommandés » — tout ce qui passe par `website_sale.products_item` — un produit à paliers annonce son meilleur tarif au lieu de son prix unitaire :

```
À partir de 66,67 €
dès 100 unités
```

Le prix retenu est le **plus bas de tous les paliers** de la liste de prix du visiteur (pas nécessairement celui du dernier palier, si la grille tarifaire n'est pas strictement décroissante), et la quantité affichée est celle à atteindre pour l'obtenir. Le bloc de prix standard d'Odoo reprend sa place dès qu'il n'y a rien à annoncer : produit sans palier, palier unique, ou paliers n'apportant aucun gain par rapport au premier.

Attention : la carte n'affiche alors plus le prix à l'unité. Un visiteur qui n'achète qu'une pièce paiera le prix du premier palier, visible sur la fiche produit.

### Fiche produit (backend), onglet "Prix et quantités"

- **Paliers de prix dégressifs** : une ligne par liste de prix et palier de quantité (`min_quantity`), avec type de calcul Fixe ou Remise (%), et aperçu du prix résultant et de l'économie réalisée par rapport au prix de vente du produit. Attention : cette colonne « Économie % » du backend se calcule par rapport au prix de vente du produit, contrairement à la colonne « Remise » du site qui se calcule par rapport au premier palier.
- **Remises par catégorie de client** : définit une remise en % à appliquer aux paliers d'une liste de prix de base pour générer automatiquement les mêmes paliers dans une liste de prix cible (ex. installateurs = tarif public − 15 %). Le bouton *Générer les tarifs* crée ou met à jour les règles correspondantes dans la liste cible.
- **Quantités minimales d'achat** : quantité minimale par liste de prix (0 = pas de restriction). Le bouton *Synchroniser les listes de prix* crée une ligne à 0 pour chaque liste de prix active qui n'en a pas encore.

### Multi-site

Le module est conçu pour fonctionner correctement sur une installation Odoo multi-site (plusieurs sites web partageant la même base de données, chacun avec ses propres listes de prix). `ProductTemplate._get_price_break_pricelist` retient la liste de prix du panier du visiteur (`website.sale_get_order().pricelist_id`) — la même que celle appliquée au minimum de commande — **mais seulement si ce panier appartient au site courant**. Sinon elle retombe sur `website.pricelist_id`.

Cette garde est indispensable : une session de navigateur ne conserve qu'un seul `sale_order_id` pour tous les sites. Un panier resté ouvert sur un autre site imposerait donc sa liste de prix ici, et les paliers seraient cherchés dans une grille qui n'est pas celle du site affiché — tableau vide sur la fiche produit et disparition du « à partir de » sur les cartes, alors qu'un visiteur anonyme, sans panier inter-sites, verrait l'affichage correct.

L'application du minimum de commande à l'ajout au panier passe par la même résolution : `WebsiteSalePriceBreak._get_min_qty_pricelist` délègue à `_get_price_break_pricelist`, de sorte que le minimum appliqué au panier est toujours celui annoncé sur la fiche produit. Cette liste de prix ne sert qu'à choisir la règle de minimum ; le prix de la ligne, lui, reste calculé par Odoo depuis la liste de prix du panier.

## Règles prises en compte dans le tableau

`ProductTemplate._get_price_break_rules` retient les règles de la liste de prix ayant `min_quantity > 0` et portant sur : ce modèle de produit, une de ses variantes, sa catégorie (ou une catégorie parente), ou aucun produit en particulier (règle globale de la liste).

## Notes d'implémentation

**Mémoïsation par requête.** Une page de liste rend des dizaines de cartes produit, chacune demandant le meilleur palier. `_price_break_cache()` stocke sur l'objet `request` la liste de prix résolue et les règles à palier de cette liste, de sorte qu'une page entière ne coûte qu'une résolution et une recherche, quel que soit le nombre de produits affichés. Le cache vit le temps de la requête HTTP et se désactive hors contexte web (appels backend, crons).

**Pas de scrutation côté client.** Le sélecteur de quantité de la page produit est un composant Owl (`sale.QuantityButtons`) qui réécrit la valeur de l'input en patchant le DOM, sans émettre d'évènement — d'où la scrutation périodique des premières versions du module. `price_break_table.js` intercepte désormais la propriété `value` de l'input (plus un observateur sur l'attribut `value`, et les évènements habituels), et découvre les modales de variantes via un `MutationObserver`. Il ne reste qu'un `setInterval`, en filet de sécurité si l'interception ne peut pas être posée.

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
    └── website_sale_templates.xml     # Tableau, contraintes de quantité, « à partir de »
```

Le JS et le CSS sont chargés via `web.assets_frontend` sur toutes les pages du site ; `price_break_table.js` ne fait rien tant que le markup de la page produit n'est pas présent.

## Dépendances

`product`, `sale`, `website_sale`.

## Licence

LGPL-3.
