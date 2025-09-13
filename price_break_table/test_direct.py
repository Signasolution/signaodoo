#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Test direct de la méthode Python pour vérifier le fonctionnement
"""

def test_direct_method():
    """
    Test direct de la méthode get_price_break_table_js_data
    """
    print("=== TEST DIRECT DE LA MÉTHODE PYTHON ===")
    
    # 1. Vérifier qu'il y a des produits
    products = env['product.template'].search([('sale_ok', '=', True)], limit=5)
    print(f"Produits trouvés: {len(products)}")
    
    if not products:
        print("❌ Aucun produit trouvé")
        return False
    
    # 2. Vérifier qu'il y a des listes de prix
    pricelists = env['product.pricelist'].search([], limit=5)
    print(f"Listes de prix trouvées: {len(pricelists)}")
    
    if not pricelists:
        print("❌ Aucune liste de prix trouvée")
        return False
    
    # 3. Vérifier qu'il y a des règles de prix
    rules = env['product.pricelist.item'].search([], limit=10)
    print(f"Règles de prix trouvées: {len(rules)}")
    
    if rules:
        for rule in rules[:3]:
            print(f"   - Règle {rule.id}: Liste {rule.pricelist_id.name}, Produit {rule.product_tmpl_id.name if rule.product_tmpl_id else 'Global'}, Qty {rule.min_quantity}")
    
    # 4. Test avec le premier produit et la première liste de prix
    product = products[0]
    pricelist = pricelists[0]
    
    print(f"\n=== TEST AVEC PRODUIT {product.name} ===")
    print(f"Liste de prix: {pricelist.name}")
    
    try:
        # Test direct de la méthode
        result = product.get_price_break_table_js_data(
            pricelist_id=pricelist.id,
            quantity=1
        )
        
        print(f"✅ Méthode exécutée avec succès")
        print(f"Résultat: {result}")
        
        if result.get('rows'):
            print(f"✅ {len(result['rows'])} ligne(s) de prix dégressif trouvée(s)")
            for row in result['rows']:
                print(f"   - {row['quantity_display']}: {row['price_formatted']}")
        else:
            print("❌ Aucune ligne de prix dégressif")
            
    except Exception as e:
        print(f"❌ Erreur lors de l'exécution: {str(e)}")
        import traceback
        traceback.print_exc()
    
    # 5. Test avec toutes les listes de prix
    print(f"\n=== TEST AVEC TOUTES LES LISTES DE PRIX ===")
    for pricelist in pricelists:
        print(f"\nTest avec {pricelist.name} (ID: {pricelist.id})")
        try:
            result = product.get_price_break_table_js_data(
                pricelist_id=pricelist.id,
                quantity=1
            )
            
            if result.get('rows'):
                print(f"   ✅ {len(result['rows'])} ligne(s)")
                for row in result['rows'][:2]:  # Afficher les 2 premières
                    print(f"      - {row['quantity_display']}: {row['price_formatted']}")
            else:
                print(f"   ❌ Aucune ligne")
                
        except Exception as e:
            print(f"   ❌ Erreur: {str(e)}")
    
    return True

def create_simple_test_rules():
    """
    Crée des règles de test très simples
    """
    print("=== CRÉATION DE RÈGLES DE TEST SIMPLES ===")
    
    # Créer un produit de test
    product = env['product.template'].create({
        'name': 'Test Simple Prix Dégressifs',
        'type': 'consu',
        'sale_ok': True,
        'list_price': 100.0,
    })
    
    print(f"✅ Produit créé: {product.name} (ID: {product.id})")
    
    # Utiliser la première liste de prix
    pricelist = env['product.pricelist'].search([], limit=1)
    if not pricelist:
        pricelist = env['product.pricelist'].create({
            'name': 'Test Simple',
            'currency_id': env.ref('base.EUR').id,
        })
    
    print(f"✅ Liste de prix: {pricelist.name} (ID: {pricelist.id})")
    
    # Créer des règles simples
    rules_data = [
        {'min_quantity': 1, 'compute_price': 'fixed', 'fixed_price': 100.0},
        {'min_quantity': 5, 'compute_price': 'fixed', 'fixed_price': 90.0},
        {'min_quantity': 10, 'compute_price': 'fixed', 'fixed_price': 80.0},
    ]
    
    for rule_data in rules_data:
        rule_data.update({
            'pricelist_id': pricelist.id,
            'product_tmpl_id': product.id,
            'sequence': 1,
        })
        rule = env['product.pricelist.item'].create(rule_data)
        print(f"✅ Règle créée: {rule.min_quantity}+ → {rule.fixed_price}€")
    
    # Test immédiat
    print(f"\n=== TEST IMMÉDIAT ===")
    try:
        result = product.get_price_break_table_js_data(
            pricelist_id=pricelist.id,
            quantity=1
        )
        
        print(f"Résultat: {result}")
        
        if result.get('rows'):
            print(f"✅ SUCCÈS: {len(result['rows'])} ligne(s)")
            for row in result['rows']:
                print(f"   - {row['quantity_display']}: {row['price_formatted']}")
        else:
            print("❌ ÉCHEC: Aucune ligne")
            
    except Exception as e:
        print(f"❌ ERREUR: {str(e)}")
        import traceback
        traceback.print_exc()
    
    return product.id, pricelist.id

# Instructions
print("""
Pour tester directement dans Odoo:

1. Ouvrez le shell Odoo:
   python3 odoo-bin shell -d votre_base -r odoo -w odoo

2. Testez la méthode:
   exec(open('addons/price_break_table/test_direct.py').read())
   test_direct_method()

3. Créez des règles de test:
   create_simple_test_rules()
""")

if __name__ == "__main__":
    print("Ce script doit être exécuté dans le shell Odoo")
