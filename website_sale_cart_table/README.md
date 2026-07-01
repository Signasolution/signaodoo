# Panier personnalisé (affichage tableau) pour Odoo

## 📋 **Description**

Module Odoo 18 qui réorganise la page panier eCommerce (`/shop/cart`, module
`website_sale`) en un tableau HTML classique (`<table>`/`<thead>`/`<tbody>`)
au lieu de la mise en page en lignes flex par défaut d'Odoo 18.

Colonnes affichées :

1. Image du produit
2. Nom du produit + description de vente
3. Prix unitaire (recalculé dynamiquement selon la quantité, paliers de
   pricelist inclus)
4. Quantité (contrôles +/- existants)
5. Total de la ligne
6. Icône de suppression

## ✨ **Fonctionnalités**

- ✅ Hérite les templates QWeb de `website_sale` via xpath (`position="move"`)
  sans dupliquer aucun `t-field`/`t-esc`/`t-out` existant
- ✅ Aucune réécriture du JavaScript de gestion du panier
  (`/shop/cart/update_json`, suppression de ligne) : uniquement les blocs
  existants sont déplacés dans la nouvelle structure
- ✅ Compatible avec `website_sale.suggested_products_list` (le conteneur
  `#cart_products` d'origine n'est jamais renommé ni supprimé)
- ✅ Responsive : la description est masquée et l'image réduite sous 768px

## 🚀 **Installation**

1. Le module est déployé avec le reste du dépôt `signaodoo`
2. Mettre à jour la liste des modules puis installer/mettre à jour
   `website_sale_cart_table` (`-u website_sale_cart_table` ou depuis Apps)
3. Vider le cache des assets si le CSS ne se recharge pas (mode développeur
   > Regenerate Assets Bundles)

## ⚠️ **Points d'attention**

- Le module cible des templates QWeb standard de `website_sale` (image via
  `style="width: 64px"`, bloc nom/description via la classe `flex-grow-1`).
  Si un patch Odoo ou un module tiers renomme ces éléments, l'upgrade échoue
  avec une erreur xpath explicite (pas de casse silencieuse) — voir
  `views/cart_templates.xml` pour le détail des xpath.
- Si un autre module tiers (transporteur, assurance produit, etc.) hérite
  aussi `website_sale.cart_lines` en ciblant le `<div>` de ligne d'origine
  (`.o_cart_product`) plutôt que le conteneur `#cart_products`, il faudra
  vérifier sa compatibilité après activation.
