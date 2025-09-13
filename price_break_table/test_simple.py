#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Test ultra-simple pour vérifier si les règles de prix sont trouvées
Usage: Dans le shell Odoo, exécuter: exec(open('addons/price_break_table/test_simple.py').read())
"""

print("=" * 50)
print("TEST ULTRA-SIMPLE")
print("=" * 50)

# Récupérer l'environnement Odoo
env = env  # Variable globale du shell Odoo

# Test avec le produit ID 2
product_id = 2
print(f"\n🔍 Test du produit ID: {product_id}")

try:
    # Récupérer le produit
    product = env['product.template'].browse(product_id)
    print(f"✅ Produit: {product.name}")
    
    # Test direct de la méthode
    print(f"\n🧪 Test de get_price_break_table_js_data:")
    result = product.get_price_break_table_js_data(1, None, 1)
    print(f"Résultat: {result}")
    
    if result.get('rows'):
        print(f"✅ SUCCÈS: {len(result['rows'])} règles trouvées!")
        for i, row in enumerate(result['rows']):
            print(f"   {i+1}. {row['quantity_display']} → {row['price_formatted']}")
    else:
        print(f"❌ ÉCHEC: Aucune règle trouvée")
        print(f"   - Currency: {result.get('currency')}")
        print(f"   - Current quantity: {result.get('current_quantity')}")
    
except Exception as e:
    print(f"❌ Erreur: {e}")
    import traceback
    traceback.print_exc()

print("\n" + "=" * 50)
