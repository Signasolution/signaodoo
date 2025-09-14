# Tableau de Prix Dégressifs pour Odoo

## 📋 **Description**

Module Odoo qui affiche un tableau interactif des prix dégressifs par quantité sur les pages produits. Permet aux clients de voir les prix selon la quantité commandée et d'ajuster automatiquement la quantité en cliquant sur les lignes du tableau.

## ✨ **Fonctionnalités**

- ✅ **Affichage intelligent** des prix dégressifs avec formatage propre (1+, 3+, 5+, 7+)
- ✅ **Clic interactif** sur les lignes pour ajuster la quantité
- ✅ **Ligne active intelligente** qui se met à jour selon la quantité saisie
- ✅ **Détection des boutons +/-** pour la mise à jour automatique
- ✅ **Tableau compact** (40% moins large)
- ✅ **Restriction aux pages produit** uniquement
- ✅ **Message de confirmation** lors de la mise à jour de la quantité
- ✅ **Compatible** avec toutes les versions d'Odoo

## 🚀 **Installation**

1. **Télécharger le module** dans le dossier `addons` de votre Odoo
2. **Mettre à jour la liste des modules** dans Odoo
3. **Installer le module** "Tableau de Prix Dégressifs"
4. **Configurer les règles de prix** dans les listes de prix Odoo

## ⚙️ **Configuration**

### Règles de Prix

Le module utilise les règles de prix dégressifs configurées dans Odoo :

1. **Aller dans** : Ventes > Configuration > Listes de Prix
2. **Créer ou modifier** une liste de prix
3. **Ajouter des règles** avec :
   - **Quantité minimum** : 1, 3, 5, 7, etc.
   - **Type de prix** : Prix fixe ou Pourcentage
   - **Produit** : Spécifique ou Global

### Types de Règles Supportés

- **Prix fixe** : Prix unitaire fixe pour la quantité
- **Pourcentage** : Réduction en pourcentage sur le prix de base
- **Règles globales** : Appliquées à tous les produits
- **Règles spécifiques** : Appliquées à un produit particulier
- **Règles par catégorie** : Appliquées aux produits d'une catégorie

## 🎯 **Utilisation**

### Pour les Clients

1. **Naviguer** vers une page produit
2. **Voir le tableau** des prix dégressifs
3. **Cliquer sur une ligne** pour ajuster la quantité
4. **Utiliser les boutons +/-** pour voir la ligne active se mettre à jour

### Pour les Administrateurs

- Le tableau s'affiche **automatiquement** sur les pages produit
- **Aucune configuration** supplémentaire nécessaire
- Compatible avec **tous les thèmes** Odoo

## 🔧 **Personnalisation**

### Styles CSS

Le tableau utilise des classes CSS standard d'Odoo et peut être personnalisé :

```css
.price-break-table-widget {
    /* Personnaliser l'apparence du tableau */
}
```

### JavaScript

Le code JavaScript est modulaire et peut être étendu :

```javascript
// Accéder au widget global
window.PriceBreak.widget

// Réinitialiser manuellement
window.PriceBreak.init()
```

## 📊 **Compatibilité**

- **Odoo** : Toutes versions (testé sur Odoo 18.0)
- **Thèmes** : Compatible avec tous les thèmes
- **Modules** : Compatible avec website_sale, sale, product
- **Navigateurs** : Chrome, Firefox, Safari, Edge

## 🐛 **Dépannage**

### Le tableau ne s'affiche pas

1. **Vérifier** que le module est installé et activé
2. **Vérifier** qu'il y a des règles de prix dégressifs configurées
3. **Vérifier** que vous êtes sur une page produit (pas liste ou panier)

### Les prix ne sont pas corrects

1. **Vérifier** la configuration des règles de prix
2. **Vérifier** que les règles sont actives
3. **Vérifier** que la liste de prix est correcte

### Le clic sur les lignes ne fonctionne pas

1. **Vérifier** la console du navigateur pour les erreurs JavaScript
2. **Vérifier** que le champ de quantité existe sur la page
3. **Recharger** la page si nécessaire

## 📋 **Structure du Module**

```
price_break_table/
├── __init__.py
├── __manifest__.py
├── models/
│   ├── __init__.py
│   └── product_template.py
├── views/
│   ├── product_template_views.xml
│   └── website_sale_templates.xml
├── static/
│   ├── src/
│   │   ├── css/
│   │   │   └── price_break_table.css
│   │   └── js/
│   │       └── price_break_table.js
│   └── security/
│       └── ir.model.access.csv
└── README.md
```

## 🔄 **Versions**

### Version 18.0.2.0.0 - Version de Production
- ✅ **Nettoyage complet du code** - Suppression de tous les fichiers de test et debug
- ✅ **Code JavaScript optimisé** - Suppression des logs de debug et commentaires inutiles
- ✅ **Code Python nettoyé** - Suppression des print() de debug
- ✅ **Version finale** prête pour la production

### Versions précédentes
- ✅ Développement initial et corrections de compatibilité
- ✅ Résolution des erreurs d'intégration Odoo
- ✅ Optimisation des performances et de l'affichage

## 📞 **Support**

Pour toute question ou problème :
- **Vérifier** ce README
- **Consulter** les logs Odoo
- **Tester** sur un environnement de développement

## 📄 **Licence**

Ce module est sous licence LGPL-3 comme Odoo.

---

**Module développé pour Odoo - Version de Production 18.0.2.0.0**