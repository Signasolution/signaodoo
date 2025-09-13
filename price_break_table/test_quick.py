#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Test rapide pour diagnostiquer le problème
"""

def quick_test():
    """
    Test rapide pour le produit ID 2
    """
    print("=== TEST RAPIDE PRODUIT ID 2 ===")
    
    # 1. Vérifier le produit
    product = env['product.template'].browse(2)
    if not product.exists():
        print("❌ Produit ID 2 n'existe pas")
        return
    
    print(f"✅ Produit: {product.name}")
    print(f"   - Prix: {product.list_price}€")
    print(f"   - Vendu: {product.sale_ok}")
    
    # 2. Vérifier les règles de prix globales
    print(f"\n=== RECHERCHE DE RÈGLES ===")
    
    # Toutes les règles
    all_rules = env['product.pricelist.item'].search([('min_quantity', '>', 0)])
    print(f"Total des règles avec min_quantity > 0: {len(all_rules)}")
    
    # Règles spécifiques au produit 2
    product_rules = env['product.pricelist.item'].search([
        ('product_tmpl_id', '=', 2),
        ('min_quantity', '>', 0)
    ])
    print(f"Règles spécifiques au produit 2: {len(product_rules)}")
    
    # Règles globales (sans produit)
    global_rules = env['product.pricelist.item'].search([
        ('product_tmpl_id', '=', False),
        ('product_id', '=', False),
        ('min_quantity', '>', 0)
    ])
    print(f"Règles globales: {len(global_rules)}")
    
    # 3. Afficher quelques règles pour debug
    if all_rules:
        print(f"\n=== EXEMPLES DE RÈGLES ===")
        for rule in all_rules[:5]:
            print(f"Règle {rule.id}:")
            print(f"   - Liste: {rule.pricelist_id.name}")
            print(f"   - Produit: {rule.product_tmpl_id.name if rule.product_tmpl_id else 'Global'}")
            print(f"   - Qty min: {rule.min_quantity}")
            print(f"   - Type: {rule.compute_price}")
            if rule.compute_price == 'fixed':
                print(f"   - Prix fixe: {rule.fixed_price}")
    
    # 4. Test de la méthode avec la première liste de prix
    pricelist = env['product.pricelist'].search([], limit=1)
    if pricelist:
        print(f"\n=== TEST MÉTHODE AVEC {pricelist.name} ===")
        try:
            result = product.get_price_break_table_data(
                pricelist_id=pricelist.id,
                quantity=1
            )
            print(f"Résultat: {result}")
        except Exception as e:
            print(f"❌ Erreur: {str(e)}")
    
    # 5. Créer des règles de test si nécessaire
    if len(product_rules) == 0 and len(global_rules) == 0:
        print(f"\n=== CRÉATION DE RÈGLES DE TEST ===")
        create_simple_rules()
    
    return True

def create_simple_rules():
    """
    Crée des règles simples pour le produit 2
    """
    product = env['product.template'].browse(2)
    pricelist = env['product.pricelist'].search([], limit=1)
    
    if not pricelist:
        print("❌ Aucune liste de prix trouvée")
        return
    
    print(f"Création de règles pour {product.name} avec {pricelist.name}")
    
    # Règles simples
    rules = [
        {'min_quantity': 1, 'fixed_price': product.list_price},
        {'min_quantity': 5, 'fixed_price': product.list_price * 0.9},
        {'min_quantity': 10, 'fixed_price': product.list_price * 0.8},
    ]
    
    for rule_data in rules:
        env['product.pricelist.item'].create({
            'pricelist_id': pricelist.id,
            'product_tmpl_id': product.id,
            'compute_price': 'fixed',
            'fixed_price': rule_data['fixed_price'],
            'min_quantity': rule_data['min_quantity'],
            'sequence': 1,
        })
        print(f"✅ Règle créée: {rule_data['min_quantity']}+ → {rule_data['fixed_price']}€")
    
    # Test immédiat
    print(f"\n=== TEST IMMÉDIAT ===")
    result = product.get_price_break_table_data(pricelist_id=pricelist.id, quantity=1)
    print(f"Résultat: {result}")
    
    if result.get('rows'):
        print(f"✅ SUCCÈS: {len(result['rows'])} ligne(s)")
        for row in result['rows']:
            print(f"   - {row['quantity_display']}: {row['price_formatted']}")
    else:
        print("❌ Toujours aucune ligne")

# Test rapide
quick_test()
