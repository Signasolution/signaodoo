# Fiches Commerciales Produits pour Odoo

## 📋 **Description**

Module Odoo qui permet de créer des fiches commerciales personnalisables pour les produits. Compatible avec Odoo Studio pour une personnalisation facile des vues et des champs.

## ✨ **Fonctionnalités**

- ✅ **Bouton dans le backend** des produits pour créer une fiche
- ✅ **Champs personnalisables** via Odoo Studio
- ✅ **Réorganisation facile** des champs par glisser-déposer
- ✅ **Génération PDF** des fiches commerciales
- ✅ **États de workflow** (Brouillon, Confirmé, Publié)
- ✅ **Intégration native** avec les produits Odoo
- ✅ **Compatible Studio** pour la personnalisation

## 🚀 **Installation**

1. **Télécharger le module** dans le dossier `addons` de votre Odoo
2. **Mettre à jour la liste des modules** dans Odoo
3. **Installer le module** "Fiches Commerciales Produits"
4. **Activer Odoo Studio** si ce n'est pas déjà fait

## ⚙️ **Configuration**

### 1. Utilisation de Base

1. **Aller dans** : Ventes > Produits > Produits
2. **Sélectionner un produit**
3. **Cliquer sur** "Créer Fiche Commerciale"
4. **Remplir les champs** personnalisés
5. **Confirmer et publier** la fiche

### 2. Personnalisation avec Odoo Studio

#### Activation d'Odoo Studio

1. **Aller dans** : Paramètres > Général > Studio
2. **Activer Studio** si ce n'est pas déjà fait
3. **Sélectionner** "Fiches Commerciales" dans le menu

#### Personnalisation des Champs

1. **Ouvrir Studio** sur une fiche commerciale
2. **Modifier les champs** existants :
   - Renommer les labels
   - Changer les types de champs
   - Ajouter des contraintes
3. **Ajouter de nouveaux champs** :
   - Cliquer sur "Ajouter un champ"
   - Choisir le type de champ
   - Configurer les propriétés
4. **Réorganiser les champs** :
   - Glisser-déposer les champs
   - Créer des groupes
   - Modifier la mise en page

#### Personnalisation des Vues

1. **Modifier la vue formulaire** :
   - Réorganiser les sections
   - Ajouter des séparateurs
   - Modifier les couleurs
2. **Personnaliser la vue liste** :
   - Ajouter des colonnes
   - Modifier les filtres
   - Créer des vues personnalisées

## 🎯 **Utilisation**

### Pour les Utilisateurs

1. **Créer une fiche** :
   - Aller dans un produit
   - Cliquer sur "Créer Fiche Commerciale"
   - Remplir les informations
   - Confirmer la fiche

2. **Modifier une fiche** :
   - Aller dans Ventes > Fiches Commerciales
   - Sélectionner la fiche à modifier
   - Apporter les modifications
   - Sauvegarder

3. **Générer un PDF** :
   - Ouvrir une fiche confirmée
   - Cliquer sur "Générer PDF"
   - Télécharger le fichier

### Pour les Administrateurs

1. **Configurer les champs** via Studio
2. **Personnaliser les vues** selon les besoins
3. **Créer des workflows** personnalisés
4. **Configurer les droits d'accès**

## 🔧 **Personnalisation Avancée**

### Ajout de Nouveaux Types de Champs

```python
# Dans le modèle product_commercial_sheet.py
custom_field_9 = fields.Many2one(
    'res.partner',
    string='Client associé',
    help="Champ personnalisable via Odoo Studio"
)
```

### Personnalisation du Rapport PDF

1. **Modifier le template** dans `reports/product_commercial_sheet_report.xml`
2. **Ajouter des styles CSS** personnalisés
3. **Créer des sections** supplémentaires

### Intégration avec d'Autres Modules

Le module est compatible avec :
- **Website Sale** : Affichage des fiches sur le site web
- **CRM** : Intégration avec les opportunités
- **Inventory** : Informations de stock
- **Accounting** : Données financières

## 📊 **Structure du Module**

```
product_commercial_sheet/
├── __init__.py
├── __manifest__.py
├── models/
│   ├── __init__.py
│   ├── product_commercial_sheet.py
│   └── product_template.py
├── views/
│   ├── product_commercial_sheet_views.xml
│   └── product_template_views.xml
├── data/
│   └── ir_ui_view.xml
├── reports/
│   └── product_commercial_sheet_report.xml
├── security/
│   └── ir.model.access.csv
├── static/
│   └── src/
│       ├── css/
│       │   └── commercial_sheet.css
│       └── js/
│           └── commercial_sheet.js
└── README.md
```

## 🎨 **Personnalisation avec Studio**

### Champs Disponibles

- **Texte** : Champs courts et longs
- **Numérique** : Entiers et décimaux
- **Date/Heure** : Dates et heures
- **Sélection** : Listes déroulantes
- **Booléen** : Cases à cocher
- **Relation** : Liens vers d'autres modèles

### Groupes de Champs

1. **Informations Produit** : Données de base du produit
2. **Champs Personnalisés** : Champs configurables
3. **Description** : Description du produit
4. **Fichier PDF** : Document généré

### Workflow Personnalisé

1. **Brouillon** : Fiche en cours de création
2. **Confirmé** : Fiche validée
3. **Publié** : Fiche disponible

## 🔄 **Versions**

### Version 18.0.8.0.0 - Version Actuelle
- ✅ **Création du module** de base
- ✅ **Intégration** avec les produits Odoo
- ✅ **Compatibilité Studio** complète
- ✅ **Génération PDF** des fiches
- ✅ **Workflow** des états
- ✅ **Champs personnalisables**

## 📞 **Support**

Pour toute question ou problème :
- **Vérifier** ce README
- **Consulter** les logs Odoo
- **Tester** sur un environnement de développement
- **Utiliser Studio** pour la personnalisation

## 📄 **Licence**

Ce module est sous licence LGPL-3 comme Odoo.

---

**Module développé pour Odoo - Compatible Studio - Version 18.0.8.0.0**
