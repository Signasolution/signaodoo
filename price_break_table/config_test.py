#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Configuration de test pour le module Tableau de Prix Dégressifs
Ce script crée des données de test pour vérifier le fonctionnement du module
"""

def create_test_data():
    """
    Crée des données de test pour le module
    """
    print("=== Création des données de test ===")
    
    # 1. Créer un produit de test
    print("\n1. Création d'un produit de test...")
    product = env['product.template'].search([('name', '=', 'Produit Test Prix Dégressifs')])
    if not product:
        product = env['product.template'].create({
            'name': 'Produit Test Prix Dégressifs',
            'type': 'consu',
            'sale_ok': True,
            'list_price': 100.0,
            'default_code': 'TEST-PRICE-BREAK',
        })
        print(f"✅ Produit créé: {product.name} (ID: {product.id})")
    else:
        print(f"✅ Produit existant: {product.name} (ID: {product.id})")
    
    # 2. Créer une liste de prix de test
    print("\n2. Création d'une liste de prix de test...")
    pricelist = env['product.pricelist'].search([('name', '=', 'Test Prix Dégressifs')])
    if not pricelist:
        pricelist = env['product.pricelist'].create({
            'name': 'Test Prix Dégressifs',
            'active': True,
            'currency_id': env.ref('base.EUR').id,
        })
        print(f"✅ Liste de prix créée: {pricelist.name} (ID: {pricelist.id})")
    else:
        print(f"✅ Liste de prix existante: {pricelist.name} (ID: {pricelist.id})")
    
    # 3. Créer des règles de prix dégressifs
    print("\n3. Création des règles de prix dégressifs...")
    
    # Supprimer les anciennes règles de test
    old_rules = env['product.pricelist.item'].search([
        ('pricelist_id', '=', pricelist.id),
        ('product_tmpl_id', '=', product.id)
    ])
    if old_rules:
        old_rules.unlink()
        print("✅ Anciennes règles supprimées")
    
    # Créer les nouvelles règles
    rules_data = [
        {'min_quantity': 1, 'compute_price': 'fixed', 'fixed_price': 100.0, 'sequence': 1},
        {'min_quantity': 5, 'compute_price': 'fixed', 'fixed_price': 90.0, 'sequence': 2},
        {'min_quantity': 10, 'compute_price': 'fixed', 'fixed_price': 80.0, 'sequence': 3},
        {'min_quantity': 25, 'compute_price': 'fixed', 'fixed_price': 70.0, 'sequence': 4},
        {'min_quantity': 50, 'compute_price': 'fixed', 'fixed_price': 60.0, 'sequence': 5},
    ]
    
    for rule_data in rules_data:
        rule_data.update({
            'pricelist_id': pricelist.id,
            'product_tmpl_id': product.id,
            'active': True,
        })
        rule = env['product.pricelist.item'].create(rule_data)
        print(f"✅ Règle créée: {rule.min_quantity}+ → {rule.fixed_price}€")
    
    # 4. Test des données
    print("\n4. Test des données créées...")
    data = product.get_price_break_table_data(pricelist_id=pricelist.id, quantity=1)
    print(f"✅ {len(data.get('rows', []))} ligne(s) de prix dégressif")
    
    for row in data.get('rows', []):
        print(f"   - {row['quantity_display']}: {row['price_formatted']}")
    
    print("\n=== Données de test créées avec succès ===")
    print(f"Produit ID: {product.id}")
    print(f"Liste de prix ID: {pricelist.id}")
    print("\nPour tester le module:")
    print("1. Allez dans Ventes > Produits")
    print("2. Ouvrez le produit 'Produit Test Prix Dégressifs'")
    print("3. Le tableau de prix dégressifs devrait apparaître")
    print("\nOu pour l'e-commerce:")
    print("1. Allez sur le site web")
    print("2. Naviguez vers le produit")
    print("3. Le tableau devrait s'afficher sur la page produit")

def cleanup_test_data():
    """
    Supprime les données de test
    """
    print("=== Suppression des données de test ===")
    
    # Supprimer les produits de test
    products = env['product.template'].search([('name', '=', 'Produit Test Prix Dégressifs')])
    if products:
        products.unlink()
        print("✅ Produits de test supprimés")
    
    # Supprimer les listes de prix de test
    pricelists = env['product.pricelist'].search([('name', '=', 'Test Prix Dégressifs')])
    if pricelists:
        pricelists.unlink()
        print("✅ Listes de prix de test supprimées")
    
    print("✅ Nettoyage terminé")

# Instructions d'utilisation
print("""
Pour créer des données de test dans Odoo:

1. Ouvrez le shell Odoo:
   python3 odoo-bin shell -d votre_base -r odoo -w odoo

2. Créez les données de test:
   exec(open('addons/price_break_table/config_test.py').read())
   create_test_data()

3. Pour nettoyer:
   cleanup_test_data()
""")

if __name__ == "__main__":
    print("Ce script doit être exécuté dans le shell Odoo")
