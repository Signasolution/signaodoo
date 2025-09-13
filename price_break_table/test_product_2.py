#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Test spécifique pour le produit ID 2
"""

def test_product_2():
    """
    Test spécifique pour le produit ID 2
    """
    print("=== TEST PRODUIT ID 2 ===")
    
    # 1. Vérifier que le produit existe
    product = env['product.template'].browse(2)
    if not product.exists():
        print("❌ Produit ID 2 n'existe pas")
        return False
    
    print(f"✅ Produit trouvé: {product.name}")
    print(f"   - Type: {product.type}")
    print(f"   - Vendu: {product.sale_ok}")
    print(f"   - Prix: {product.list_price}")
    print(f"   - Catégorie: {product.categ_id.name if product.categ_id else 'Aucune'}")
    
    # 2. Vérifier les listes de prix
    pricelists = env['product.pricelist'].search([], limit=5)
    print(f"\n=== LISTES DE PRIX DISPONIBLES ===")
    for pricelist in pricelists:
        print(f"✅ {pricelist.name} (ID: {pricelist.id})")
    
    # 3. Vérifier les règles de prix pour ce produit
    print(f"\n=== RÈGLES DE PRIX POUR LE PRODUIT ===")
    
    all_rules = env['product.pricelist.item'].search([
        ('min_quantity', '>', 0),
    ])
    
    print(f"Total des règles de prix: {len(all_rules)}")
    
    applicable_rules = []
    for rule in all_rules:
        print(f"\nRègle {rule.id}:")
        print(f"   - Liste: {rule.pricelist_id.name}")
        print(f"   - Produit: {rule.product_tmpl_id.name if rule.product_tmpl_id else 'Global'}")
        print(f"   - Variante: {rule.product_id.name if rule.product_id else 'Aucune'}")
        print(f"   - Catégorie: {rule.categ_id.name if rule.categ_id else 'Aucune'}")
        print(f"   - Qty min: {rule.min_quantity}")
        print(f"   - Type: {rule.compute_price}")
        
        # Vérifier si applicable
        is_applicable = False
        
        if rule.product_tmpl_id and rule.product_tmpl_id.id == 2:
            is_applicable = True
            print(f"   ✅ APPLICABLE: Spécifique au produit")
        elif rule.product_id and rule.product_id.product_tmpl_id.id == 2:
            is_applicable = True
            print(f"   ✅ APPLICABLE: Spécifique à la variante")
        elif not rule.product_tmpl_id and not rule.product_id:
            is_applicable = True
            print(f"   ✅ APPLICABLE: Règle globale")
        elif rule.categ_id and product.categ_id and rule.categ_id in product.categ_id.parent_path.split('/'):
            is_applicable = True
            print(f"   ✅ APPLICABLE: Règle par catégorie")
        else:
            print(f"   ❌ NON APPLICABLE")
        
        if is_applicable:
            applicable_rules.append(rule)
    
    print(f"\n=== RÈGLES APPLICABLES: {len(applicable_rules)} ===")
    
    # 4. Test avec la première liste de prix
    if pricelists:
        test_pricelist = pricelists[0]
        print(f"\n=== TEST AVEC {test_pricelist.name} ===")
        
        try:
            result = product.get_price_break_table_data(
                pricelist_id=test_pricelist.id,
                quantity=1
            )
            
            print(f"Résultat de la méthode:")
            print(f"   - Lignes: {len(result.get('rows', []))}")
            print(f"   - Devise: {result.get('currency', {}).get('name', 'N/A')}")
            print(f"   - Données complètes: {result}")
            
        except Exception as e:
            print(f"❌ Erreur: {str(e)}")
            import traceback
            traceback.print_exc()
    
    # 5. Créer des règles de test si aucune n'existe
    if not applicable_rules:
        print(f"\n=== CRÉATION DE RÈGLES DE TEST ===")
        create_test_rules_for_product_2()
    
    return True

def create_test_rules_for_product_2():
    """
    Crée des règles de test pour le produit 2
    """
    product = env['product.template'].browse(2)
    if not product.exists():
        print("❌ Produit ID 2 n'existe pas")
        return
    
    # Utiliser la première liste de prix
    pricelist = env['product.pricelist'].search([], limit=1)
    if not pricelist:
        print("❌ Aucune liste de prix trouvée")
        return
    
    print(f"Création de règles pour {product.name} avec {pricelist.name}")
    
    # Créer des règles simples
    rules_data = [
        {'min_quantity': 1, 'compute_price': 'fixed', 'fixed_price': product.list_price},
        {'min_quantity': 5, 'compute_price': 'fixed', 'fixed_price': product.list_price * 0.9},
        {'min_quantity': 10, 'compute_price': 'fixed', 'fixed_price': product.list_price * 0.8},
        {'min_quantity': 25, 'compute_price': 'fixed', 'fixed_price': product.list_price * 0.7},
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
        result = product.get_price_break_table_data(
            pricelist_id=pricelist.id,
            quantity=1
        )
        
        if result.get('rows'):
            print(f"✅ SUCCÈS: {len(result['rows'])} ligne(s)")
            for row in result['rows']:
                print(f"   - {row['quantity_display']}: {row['price_formatted']}")
        else:
            print("❌ ÉCHEC: Aucune ligne")
            
    except Exception as e:
        print(f"❌ ERREUR: {str(e)}")

# Instructions
print("""
Pour tester le produit ID 2 dans Odoo:

1. Ouvrez le shell Odoo:
   python3 odoo-bin shell -d votre_base -r odoo -w odoo

2. Testez le produit 2:
   exec(open('addons/price_break_table/test_product_2.py').read())
   test_product_2()

3. Créez des règles de test:
   create_test_rules_for_product_2()
""")

if __name__ == "__main__":
    print("Ce script doit être exécuté dans le shell Odoo")
