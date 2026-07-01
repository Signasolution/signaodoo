# Panier personnalisé (colonnes alignées) pour Odoo

## 📋 **Description**

Module Odoo 18 qui aligne l'affichage des lignes de la page panier eCommerce
(`/shop/cart`, module `website_sale`) en colonnes, **sans** utiliser de
`<table>` HTML : la structure native en lignes flex (`o_cart_product`) de
website_sale est conservée telle quelle, seuls certains blocs sont extraits
de leur wrapper commun pour devenir des colonnes indépendantes.

Colonnes affichées :

1. Image du produit
2. Nom du produit + description de vente + référence interne et attributs
   de la variante commandée (`Réf.: XXX • Matériau: ... • Finition: ...`)
3. Prix unitaire (recalculé dynamiquement selon la quantité, paliers de
   pricelist inclus)
4. Quantité (contrôles +/- existants, inchangés)
5. Total de la ligne
6. Icône de suppression

## ✨ **Fonctionnalités**

- ✅ Garde le `<div t-foreach>` d'origine de `website_sale.cart_lines`
  intact (jamais recréé) ; seuls la quantité, le prix total et le bouton
  supprimer sont extraits de leur wrapper commun (`d-flex flex-column
  align-items-end`) via xpath `position="move"`, sans dupliquer aucun
  `t-field`/`t-esc`/`t-out` existant
- ✅ Aucune réécriture du JavaScript de gestion du panier
  (`/shop/cart/update_json`, suppression de ligne) : uniquement les blocs
  existants sont déplacés dans la nouvelle structure
- ✅ Compatible avec `website_sale.suggested_products_list` (le conteneur
  `#cart_products` d'origine n'est jamais renommé ni supprimé)
- ✅ Compatible avec `website_sale_wishlist` : son bouton "Save for Later"
  est injecté dans le même conteneur que le bouton supprimer et suit donc
  automatiquement le déplacement ; les deux sont affichés en icône seule,
  côte à côte
- ✅ Réduit la largeur de la colonne "Récapitulatif de la commande"
  (`#o_cart_summary`, uniquement sur `/shop/cart`) pour laisser plus de
  place au panier et éviter le débordement horizontal
- ✅ Responsive : la description de vente et le prix unitaire sont masqués
  et l'image réduite sous 768px

## 🚀 **Installation**

1. Le module est déployé avec le reste du dépôt `signaodoo`
2. Mettre à jour la liste des modules puis installer/mettre à jour
   `website_sale_cart_table` (`-u website_sale_cart_table` ou depuis Apps)
3. Vider le cache des assets si le CSS ne se recharge pas (mode développeur
   > Regenerate Assets Bundles)

## ⚠️ **Points d'attention**

- Le module cible des templates QWeb standard de `website_sale` (bloc
  nom/description via la classe `flex-grow-1`, wrapper quantité/prix via les
  classes `d-flex flex-column align-items-end`). Si un patch Odoo ou un
  module tiers renomme ces éléments, l'upgrade échoue avec une erreur xpath
  explicite (pas de casse silencieuse) — voir `views/cart_templates.xml`
  pour le détail des xpath.
- Si un autre module tiers (transporteur, assurance produit, etc.) hérite
  aussi `website_sale.cart_lines` en ciblant le wrapper quantité/prix
  d'origine plutôt que le conteneur `#cart_products`, il faudra vérifier sa
  compatibilité après activation.
- La colonne "Réf. • attributs" utilise `product_id.default_code` et
  `product_id.product_template_attribute_value_ids` (champs standard du
  module `product`) ; elle ne s'affiche que si l'un des deux est renseigné.
  Si la référence n'apparaît pas, vérifiez que le champ "Référence interne"
  est bien renseigné sur la variante commandée (pas seulement sur le
  produit générique).
- La réduction de largeur de `#o_cart_summary` touche `website_sale.checkout_layout`,
  un template partagé avec les étapes livraison/paiement. Elle est scopée à
  `/shop/cart` en ciblant `div[@id='o_cart_summary']`, qui ne s'affiche
  (`t-if="show_shorter_cart_summary"`) que sur cette page — mais si un
  module tiers modifie cette condition, vérifiez que les autres étapes du
  checkout restent correctement dimensionnées.
