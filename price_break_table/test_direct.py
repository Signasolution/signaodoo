#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Script de test direct pour diagnostiquer les règles de prix dégressifs
Usage: Dans le shell Odoo, exécuter: exec(open('addons/price_break_table/test_direct.py').read())
"""

print("=" * 60)
print("DIAGNOSTIC DES RÈGLES DE PRIX DÉGRESSIFS")
print("=" * 60)

# Récupérer l'environnement Odoo
env = env  # Variable globale du shell Odoo

# Test avec le produit ID 2
product_id = 2
print(f"\n🔍 Test du produit ID: {product_id}")

try:
    # Récupérer le produit
    product = env['product.template'].browse(product_id)
    print(f"✅ Produit trouvé: {product.name}")
    print(f"   - Prix de base: {product.list_price}€")
    print(f"   - Catégorie: {product.categ_id.name if product.categ_id else 'Aucune'}")
    
    # Récupérer la pricelist par défaut
    pricelist = env['product.pricelist'].browse(1)
    print(f"✅ Pricelist trouvée: {pricelist.name}")
    
    # Rechercher TOUTES les règles de prix
    all_rules = env['product.pricelist.item'].search([])
    print(f"\n📊 Total des règles de prix dans le système: {len(all_rules)}")
    
    if all_rules:
        print("\n📋 Détail des règles:")
        for rule in all_rules:
            print(f"   - Règle ID {rule.id}:")
            print(f"     * Pricelist: {rule.pricelist_id.name}")
            print(f"     * Min quantité: {rule.min_quantity}")
            print(f"     * Produit: {rule.product_tmpl_id.name if rule.product_tmpl_id else 'Global'}")
            print(f"     * Catégorie: {rule.categ_id.name if rule.categ_id else 'Aucune'}")
            print(f"     * Type: {rule.compute_price}")
            if hasattr(rule, 'percent_price'):
                print(f"     * Pourcentage: {rule.percent_price}%")
            if hasattr(rule, 'fixed_price'):
                print(f"     * Prix fixe: {rule.fixed_price}€")
            print()
    
    # Rechercher les règles spécifiques au produit
    product_rules = env['product.pricelist.item'].search([
        ('product_tmpl_id', '=', product_id)
    ])
    print(f"🎯 Règles spécifiques au produit {product.name}: {len(product_rules)}")
    
    # Rechercher les règles globales
    global_rules = env['product.pricelist.item'].search([
        ('product_tmpl_id', '=', False)
    ])
    print(f"🌐 Règles globales: {len(global_rules)}")
    
    # Rechercher les règles par catégorie
    if product.categ_id:
        category_rules = env['product.pricelist.item'].search([
            ('categ_id', '=', product.categ_id.id)
        ])
        print(f"📁 Règles par catégorie '{product.categ_id.name}': {len(category_rules)}")
    
    # Test de la méthode principale
    print(f"\n🧪 Test de la méthode get_price_break_table_js_data:")
    try:
        result = product.get_price_break_table_js_data(1, None, 1)
        print(f"✅ Résultat: {result}")
    except Exception as e:
        print(f"❌ Erreur: {e}")
    
    # Créer une règle de test si aucune n'existe
    if len(product_rules) == 0 and len(global_rules) == 0:
        print(f"\n🔧 Création d'une règle de test...")
        try:
            test_rule = env['product.pricelist.item'].create({
                'pricelist_id': 1,
                'product_tmpl_id': product_id,
                'min_quantity': 5,
                'compute_price': 'percentage',
                'percent_price': 10.0,
            })
            print(f"✅ Règle de test créée: ID {test_rule.id}")
            print(f"   - 5+ unités = -10% sur le prix de base")
            
            # Test après création
            result = product.get_price_break_table_js_data(1, None, 1)
            print(f"✅ Résultat après création: {result}")
            
        except Exception as e:
            print(f"❌ Erreur création règle: {e}")
    
except Exception as e:
    print(f"❌ Erreur générale: {e}")
    import traceback
    traceback.print_exc()

print("\n" + "=" * 60)
print("FIN DU DIAGNOSTIC")
print("=" * 60)