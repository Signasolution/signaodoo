#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Script de comparaison des trois méthodes
Usage: Dans le shell Odoo, exécuter: exec(open('addons/price_break_table/test_compare.py').read())
"""

print("=" * 60)
print("COMPARAISON DES TROIS MÉTHODES")
print("=" * 60)

# Récupérer l'environnement Odoo
env = env  # Variable globale du shell Odoo

# Test avec le produit ID 2
product_id = 2
print(f"\n🔍 Test du produit ID: {product_id}")

try:
    # Récupérer le produit
    product = env['product.template'].browse(product_id)
    print(f"✅ Produit: {product.name}")
    
    # Test 1: Méthode principale
    print(f"\n🧪 TEST 1: Méthode principale (get_price_break_table_js_data)")
    print("-" * 50)
    try:
        result1 = product.get_price_break_table_js_data(1, None, 1)
        print(f"Résultat: {len(result1.get('rows', []))} règles")
        if result1.get('rows'):
            for i, row in enumerate(result1['rows']):
                print(f"   {i+1}. {row.get('quantity_display', 'N/A')} → {row.get('price_formatted', 'N/A')}")
        else:
            print("   ❌ Aucune règle trouvée")
    except Exception as e:
        print(f"   ❌ Erreur: {e}")
    
    # Test 2: Méthode debug
    print(f"\n🧪 TEST 2: Méthode debug (get_price_break_table_js_data_debug)")
    print("-" * 50)
    try:
        result2 = product.get_price_break_table_js_data_debug(1, None, 1)
        print(f"Résultat: {len(result2.get('rows', []))} règles")
        if result2.get('rows'):
            for i, row in enumerate(result2['rows']):
                print(f"   {i+1}. {row.get('quantity_display', 'N/A')} → {row.get('price_formatted', 'N/A')}")
        else:
            print("   ❌ Aucune règle trouvée")
    except Exception as e:
        print(f"   ❌ Erreur: {e}")
    
    # Test 3: Méthode test
    print(f"\n🧪 TEST 3: Méthode test (get_price_break_table_js_data_test)")
    print("-" * 50)
    try:
        result3 = product.get_price_break_table_js_data_test(1, None, 1)
        print(f"Résultat: {len(result3.get('rows', []))} règles")
        if result3.get('rows'):
            for i, row in enumerate(result3['rows']):
                print(f"   {i+1}. {row.get('quantity_display', 'N/A')} → {row.get('price_formatted', 'N/A')}")
        else:
            print("   ❌ Aucune règle trouvée")
    except Exception as e:
        print(f"   ❌ Erreur: {e}")
    
    # Comparaison
    print(f"\n📊 COMPARAISON:")
    print("-" * 50)
    print(f"   Méthode principale: {len(result1.get('rows', []))} règles")
    print(f"   Méthode debug:      {len(result2.get('rows', []))} règles")
    print(f"   Méthode test:       {len(result3.get('rows', []))} règles")
    
    if len(result1.get('rows', [])) != len(result2.get('rows', [])):
        print(f"\n⚠️  PROBLÈME DÉTECTÉ!")
        print(f"   La méthode principale ne trouve pas les mêmes règles que la méthode debug!")
        print(f"   Cela confirme qu'il y a encore un problème dans la méthode principale.")
    
except Exception as e:
    print(f"❌ Erreur générale: {e}")
    import traceback
    traceback.print_exc()

print("\n" + "=" * 60)
print("FIN DE LA COMPARAISON")
print("=" * 60)
