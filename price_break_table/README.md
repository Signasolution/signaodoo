# Module Tableau de Prix Dégressifs pour Odoo 18.3

## Description

Ce module ajoute un tableau interactif de prix dégressifs sur toutes les pages produits d'Odoo, permettant aux utilisateurs de visualiser les prix par quantité et d'interagir avec eux de manière bidirectionnelle.

## Fonctionnalités

### 🎯 Affichage automatique
- **Tableau de prix dégressifs** sur toutes les pages produits
- **Support des listes de prix multiples** avec respect de la logique de priorité Odoo
- **Affichage responsive** adapté aux différents écrans

### 🔄 Interaction bidirectionnelle
- **Clic sur une ligne** → Mise à jour automatique de la quantité dans le panier
- **Modification de la quantité** → Surbrillance automatique de la ligne correspondante
- **Synchronisation en temps réel** entre le tableau et les champs de quantité

### 📍 Intégration complète
- **Pages e-commerce** (website_sale)
- **Formulaires backend** (produits, commandes, factures, achats)
- **Lignes de commande** dans les formulaires de vente
- **Compatibilité totale** avec l'interface Odoo

## Installation

1. Copiez le dossier `price_break_table` dans le répertoire `addons` de votre instance Odoo
2. Redémarrez le serveur Odoo
3. Activez le mode développeur
4. Allez dans Applications > Mettre à jour la liste des applications
5. Recherchez "Tableau de Prix Dégressifs" et installez-le

## Configuration

### Prérequis
- Module `product` (inclus dans Odoo)
- Module `sale` (pour les commandes)
- Module `website_sale` (pour l'e-commerce)

### Configuration des prix dégressifs
1. Allez dans **Ventes > Configuration > Listes de prix**
2. Créez ou modifiez une liste de prix
3. Ajoutez des règles avec des quantités minimales différentes
4. Le tableau s'affichera automatiquement sur les pages produits

## Utilisation

### Pour les clients (e-commerce)
1. Naviguez vers une page produit
2. Le tableau de prix dégressifs s'affiche automatiquement
3. Cliquez sur une ligne pour ajuster la quantité
4. La quantité dans le panier se met à jour automatiquement

### Pour les utilisateurs backend
1. Ouvrez un produit, une commande ou une facture
2. Le tableau s'affiche dans la section appropriée
3. Utilisez l'interaction bidirectionnelle pour optimiser les quantités

## Structure du module

```
price_break_table/
├── __init__.py
├── __manifest__.py
├── README.md
├── models/
│   ├── __init__.py
│   └── product_template.py
├── views/
│   ├── product_template_views.xml
│   └── website_sale_templates.xml
├── static/
│   └── src/
│       ├── js/
│       │   ├── price_break_table.js
│       │   └── price_break_table_backend.js
│       └── css/
│           └── price_break_table.css
└── security/
    └── ir.model.access.csv
```

## Licence

Ce module est distribué sous licence LGPL-3.

## Changelog

### Version 18.3.1.0.0
- Version initiale
- Support complet des prix dégressifs
- Interaction bidirectionnelle
- Intégration e-commerce et backend
- Support des listes de prix multiples
