#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Script de debug pour diagnostiquer les problèmes du module Tableau de Prix Dégressifs
"""

def debug_price_break():
    """
    Debug complet du module de prix dégressifs
    """
    print("=== DEBUG MODULE PRIX DÉGRESSIFS ===")
    
    # 1. Vérifier les produits avec des règles de prix
    print("\n1. Recherche des produits avec règles de prix...")
    
    # Chercher toutes les règles de prix actives
    price_rules = env['product.pricelist.item'].search([
        ('active', '=', True),
        ('min_quantity', '>', 1)
    ])
    
    print(f"✅ {len(price_rules)} règle(s) de prix dégressif trouvée(s)")
    
    if price_rules:
        for rule in price_rules[:5]:  # Afficher les 5 premières
            print(f"   - Règle {rule.id}: Produit {rule.product_tmpl_id.name if rule.product_tmpl_id else 'Tous'}, Qty min: {rule.min_quantity}")
    
    # 2. Vérifier les listes de prix
    print("\n2. Recherche des listes de prix...")
    
    pricelists = env['product.pricelist'].search([('active', '=', True)])
    print(f"✅ {len(pricelists)} liste(s) de prix trouvée(s)")
    
    for pricelist in pricelists[:3]:
        print(f"   - {pricelist.name} (ID: {pricelist.id})")
    
    # 3. Tester avec un produit spécifique
    print("\n3. Test avec un produit spécifique...")
    
    # Chercher un produit avec des règles
    if price_rules:
        test_product = price_rules[0].product_tmpl_id
        test_pricelist = price_rules[0].pricelist_id
        
        print(f"✅ Produit de test: {test_product.name} (ID: {test_product.id})")
        print(f"✅ Liste de prix: {test_pricelist.name} (ID: {test_pricelist.id})")
        
        # Tester la méthode
        try:
            result = test_product.get_price_break_table_data(
                pricelist_id=test_pricelist.id,
                quantity=1
            )
            
            print(f"✅ Résultat de la méthode:")
            print(f"   - Nombre de lignes: {len(result.get('rows', []))}")
            print(f"   - Devise: {result.get('currency', {}).get('name', 'N/A')}")
            
            if result.get('rows'):
                for row in result['rows']:
                    print(f"   - {row['quantity_display']}: {row['price_formatted']}")
            else:
                print("   ❌ Aucune ligne trouvée!")
                
        except Exception as e:
            print(f"❌ Erreur lors du test: {str(e)}")
    
    # 4. Vérifier les règles pour un produit sans règles spécifiques
    print("\n4. Test avec un produit générique...")
    
    # Chercher un produit quelconque
    any_product = env['product.template'].search([('sale_ok', '=', True)], limit=1)
    if any_product:
        print(f"✅ Produit générique: {any_product.name} (ID: {any_product.id})")
        
        # Chercher les règles applicables à ce produit
        applicable_rules = env['product.pricelist.item'].search([
            ('active', '=', True),
            ('min_quantity', '>', 1),
            '|',
            ('product_tmpl_id', '=', any_product.id),
            ('product_id', 'in', any_product.product_variant_ids.ids),
            ('product_tmpl_id', '=', False),  # Règles globales
            ('categ_id', 'in', any_product.categ_id.parent_path.split('/') if any_product.categ_id.parent_path else []),
        ])
        
        print(f"✅ {len(applicable_rules)} règle(s) applicable(s) trouvée(s)")
        
        if applicable_rules:
            for rule in applicable_rules:
                print(f"   - Règle {rule.id}: Qty {rule.min_quantity}, Prix {rule.compute_price}")
        
        # Tester avec la première liste de prix
        if pricelists:
            test_pricelist = pricelists[0]
            try:
                result = any_product.get_price_break_table_data(
                    pricelist_id=test_pricelist.id,
                    quantity=1
                )
                
                print(f"✅ Test avec {test_pricelist.name}:")
                print(f"   - Lignes trouvées: {len(result.get('rows', []))}")
                
            except Exception as e:
                print(f"❌ Erreur: {str(e)}")
    
    # 5. Vérifier la méthode _get_price_break_rules
    print("\n5. Test de la méthode _get_price_break_rules...")
    
    if any_product and pricelists:
        test_pricelist = pricelists[0]
        try:
            rules = any_product._get_price_break_rules(test_pricelist)
            print(f"✅ Méthode _get_price_break_rules: {len(rules)} règle(s)")
            
            for rule in rules:
                print(f"   - Qty: {rule['min_quantity']}, Prix: {rule['price']}")
                
        except Exception as e:
            print(f"❌ Erreur dans _get_price_break_rules: {str(e)}")
    
    print("\n=== FIN DU DEBUG ===")

def create_test_rules():
    """
    Crée des règles de test pour vérifier le fonctionnement
    """
    print("=== CRÉATION DE RÈGLES DE TEST ===")
    
    # Créer un produit de test
    test_product = env['product.template'].create({
        'name': 'Produit Debug Prix Dégressifs',
        'type': 'consu',
        'sale_ok': True,
        'list_price': 50.0,
        'default_code': 'DEBUG-PRICE',
    })
    
    print(f"✅ Produit créé: {test_product.name} (ID: {test_product.id})")
    
    # Créer une liste de prix de test
    test_pricelist = env['product.pricelist'].create({
        'name': 'Debug Prix Dégressifs',
        'active': True,
        'currency_id': env.ref('base.EUR').id,
    })
    
    print(f"✅ Liste de prix créée: {test_pricelist.name} (ID: {test_pricelist.id})")
    
    # Créer des règles de prix
    rules_data = [
        {'min_quantity': 1, 'compute_price': 'fixed', 'fixed_price': 50.0},
        {'min_quantity': 5, 'compute_price': 'fixed', 'fixed_price': 45.0},
        {'min_quantity': 10, 'compute_price': 'fixed', 'fixed_price': 40.0},
        {'min_quantity': 25, 'compute_price': 'fixed', 'fixed_price': 35.0},
    ]
    
    for rule_data in rules_data:
        rule_data.update({
            'pricelist_id': test_pricelist.id,
            'product_tmpl_id': test_product.id,
            'active': True,
            'sequence': 1,
        })
        rule = env['product.pricelist.item'].create(rule_data)
        print(f"✅ Règle créée: {rule.min_quantity}+ → {rule.fixed_price}€")
    
    # Tester immédiatement
    print("\n=== TEST IMMÉDIAT ===")
    try:
        result = test_product.get_price_break_table_data(
            pricelist_id=test_pricelist.id,
            quantity=1
        )
        
        print(f"✅ Test réussi: {len(result.get('rows', []))} ligne(s)")
        for row in result.get('rows', []):
            print(f"   - {row['quantity_display']}: {row['price_formatted']}")
            
    except Exception as e:
        print(f"❌ Test échoué: {str(e)}")
    
    return test_product.id, test_pricelist.id

# Instructions d'utilisation
print("""
Pour utiliser ce script de debug dans Odoo:

1. Ouvrez le shell Odoo:
   python3 odoo-bin shell -d votre_base -r odoo -w odoo

2. Exécutez le debug:
   exec(open('addons/price_break_table/debug_price_break.py').read())
   debug_price_break()

3. Créez des règles de test:
   create_test_rules()
""")

if __name__ == "__main__":
    print("Ce script doit être exécuté dans le shell Odoo")
