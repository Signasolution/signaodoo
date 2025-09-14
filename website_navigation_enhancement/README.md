# Amélioration Navigation Site Web Odoo

## 📋 **Description**

Module Odoo qui améliore la navigation et la lisibilité des menus de catégories sur le site web. Il ajoute un fil d'Ariane intelligent, met en évidence l'élément de menu actif, et améliore la hiérarchie visuelle des catégories.

## ✨ **Fonctionnalités**

- ✅ **Fil d'Ariane automatique** basé sur la hiérarchie des catégories
- ✅ **Surbrillance de l'élément actif** avec couleurs et effets visuels
- ✅ **Hiérarchie visuelle améliorée** avec indentation et icônes
- ✅ **Effets interactifs** (hover, transitions fluides)
- ✅ **Design responsive** pour tous les appareils
- ✅ **Support des thèmes sombres** et accessibilité
- ✅ **Compatible** avec tous les thèmes Odoo

## 🚀 **Installation**

1. **Télécharger le module** dans le dossier `addons` de votre Odoo
2. **Mettre à jour la liste des modules** dans Odoo
3. **Installer le module** "Amélioration Navigation Site Web"
4. **Activer le mode développeur** si nécessaire pour les personnalisations

## ⚙️ **Configuration**

### Activation Automatique

Le module s'active automatiquement après installation. Aucune configuration supplémentaire n'est nécessaire.

### Personnalisation

Les styles peuvent être personnalisés en modifiant le fichier CSS :
```
website_navigation_enhancement/static/src/css/navigation_enhancement.css
```

## 🎯 **Utilisation**

### Pour les Utilisateurs

1. **Navigation améliorée** : Le fil d'Ariane indique clairement la position
2. **Élément actif visible** : L'élément de menu actuel est mis en évidence
3. **Hiérarchie claire** : Les sous-catégories sont visuellement distinctes
4. **Effets interactifs** : Survol et transitions pour une meilleure UX

### Pour les Administrateurs

- Le module s'intègre **automatiquement** dans le thème existant
- **Aucune configuration** supplémentaire nécessaire
- Compatible avec **tous les thèmes** Odoo
- **Personnalisable** via CSS

## 🔧 **Personnalisation**

### Styles CSS

Le module utilise des classes CSS spécifiques qui peuvent être personnalisées :

```css
/* Fil d'Ariane */
.website-breadcrumb {
    /* Personnaliser l'apparence du fil d'Ariane */
}

/* Navigation active */
.website-navigation .nav-item.active .nav-link {
    /* Personnaliser l'élément actif */
}

/* Menu des catégories */
.category-menu .category-item.active .category-link {
    /* Personnaliser la catégorie active */
}
```

### Couleurs par Défaut

- **Couleur principale** : #79C8BD (vert-bleu)
- **Couleur secondaire** : #2c3e50 (bleu foncé)
- **Couleur de fond** : #ffffff (blanc)
- **Couleur de texte** : #495057 (gris foncé)

## 📊 **Compatibilité**

- **Odoo** : Toutes versions (testé sur Odoo 18.0)
- **Thèmes** : Compatible avec tous les thèmes
- **Modules** : Compatible avec website_sale, website
- **Navigateurs** : Chrome, Firefox, Safari, Edge
- **Appareils** : Desktop, tablette, mobile

## 🐛 **Dépannage**

### Le fil d'Ariane ne s'affiche pas

1. **Vérifier** que le module est installé et activé
2. **Vérifier** que vous êtes sur une page de catégorie ou produit
3. **Vider le cache** du navigateur

### Les styles ne s'appliquent pas

1. **Vérifier** que les assets sont chargés
2. **Vérifier** la console du navigateur pour les erreurs
3. **Recharger** la page en mode développeur

### La navigation active ne fonctionne pas

1. **Vérifier** que JavaScript est activé
2. **Vérifier** la console pour les erreurs JavaScript
3. **Vérifier** que les classes CSS sont correctement appliquées

## 📋 **Structure du Module**

```
website_navigation_enhancement/
├── __init__.py
├── __manifest__.py
├── views/
│   ├── website_templates.xml
│   └── website_sale_templates.xml
├── static/
│   └── src/
│       ├── css/
│       │   └── navigation_enhancement.css
│       └── js/
│           └── navigation_enhancement.js
└── README.md
```

## 🎨 **Exemples d'Utilisation**

### Fil d'Ariane
```
Accueil › Boutique › Jeux & Plein air › Accessoires - Pièces détachées
```

### Navigation Active
- L'élément de menu correspondant à la page actuelle est surligné
- Couleur de fond distinctive et bordure gauche
- Police en gras pour une meilleure visibilité

### Hiérarchie des Catégories
- **Catégories principales** : Police plus grande, couleur plus foncée
- **Sous-catégories** : Indentation, bordure gauche, police plus petite
- **Catégorie active** : Surbrillance complète avec couleur distinctive

## 🔄 **Mises à Jour**

Le module est conçu pour être compatible avec les mises à jour d'Odoo. En cas de problème après une mise à jour :

1. **Désinstaller** le module
2. **Mettre à jour** le code si nécessaire
3. **Réinstaller** le module

## 📞 **Support**

Pour toute question ou problème :
- Vérifier la documentation Odoo
- Consulter les logs d'erreur
- Tester en mode développeur

## 📄 **Licence**

Ce module est distribué sous licence LGPL-3, compatible avec Odoo.
