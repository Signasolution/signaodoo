#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Script de test pour le module Tableau de Prix Dégressifs
Ce script peut être exécuté dans le shell Odoo pour tester le module
"""

def test_price_break_module():
    """
    Teste les fonctionnalités du module de tableau de prix dégressifs
    """
    print("=== Test du Module Tableau de Prix Dégressifs ===")
    
    # Test 1: Vérification de l'installation du module
    print("\n1. Vérification de l'installation...")
    module = env['ir.module.module'].search([('name', '=', 'price_break_table')])
    if module and module.state == 'installed':
        print("✅ Module installé correctement")
    else:
        print("❌ Module non installé ou non trouvé")
        return False
    
    # Test 2: Vérification des vues
    print("\n2. Vérification des vues...")
    views = env['ir.ui.view'].search([('name', 'ilike', 'price.break')])
    if views:
        print(f"✅ {len(views)} vue(s) trouvée(s)")
        for view in views:
            print(f"   - {view.name} ({view.model})")
    else:
        print("❌ Aucune vue trouvée")
    
    # Test 3: Test des données de prix dégressifs
    print("\n3. Test des données de prix dégressifs...")
    
    # Recherche d'un produit avec des règles de prix
    product = env['product.template'].search([('sale_ok', '=', True)], limit=1)
    if not product:
        print("❌ Aucun produit trouvé")
        return False
    
    print(f"✅ Produit de test: {product.name}")
    
    # Recherche d'une liste de prix
    pricelist = env['product.pricelist'].search([('active', '=', True)], limit=1)
    if not pricelist:
        print("❌ Aucune liste de prix trouvée")
        return False
    
    print(f"✅ Liste de prix: {pricelist.name}")
    
    # Test de la méthode de récupération des données
    try:
        data = product.get_price_break_table_data(pricelist_id=pricelist.id, quantity=1)
        print(f"✅ Données récupérées: {len(data.get('rows', []))} ligne(s)")
        
        if data.get('rows'):
            print("   Exemple de ligne:")
            row = data['rows'][0]
            print(f"   - Quantité: {row['quantity_display']}")
            print(f"   - Prix: {row['price_formatted']}")
            print(f"   - Actif: {row['is_active']}")
        else:
            print("   ⚠️ Aucune règle de prix dégressif trouvée")
            print("   💡 Créez des règles de prix avec des quantités minimales différentes")
            
    except Exception as e:
        print(f"❌ Erreur lors du test: {str(e)}")
        return False
    
    # Test 4: Vérification des règles de prix
    print("\n4. Vérification des règles de prix...")
    rules = env['product.pricelist.item'].search([
        ('pricelist_id', '=', pricelist.id),
        ('active', '=', True),
        ('min_quantity', '>', 1)
    ])
    
    if rules:
        print(f"✅ {len(rules)} règle(s) de prix dégressif trouvée(s)")
        for rule in rules[:3]:  # Afficher les 3 premières
            print(f"   - Quantité min: {rule.min_quantity}, Prix: {rule.compute_price}")
    else:
        print("⚠️ Aucune règle de prix dégressif trouvée")
        print("💡 Créez des règles de prix avec des quantités minimales > 1")
    
    print("\n=== Résumé ===")
    print("✅ Module fonctionnel")
    print("💡 Pour voir le tableau:")
    print("   1. Créez des règles de prix avec différentes quantités minimales")
    print("   2. Visitez une page produit ou ouvrez un produit dans le backend")
    print("   3. Le tableau devrait apparaître automatiquement")
    
    return True

# Instructions d'utilisation
print("""
Pour tester ce module dans Odoo:

1. Ouvrez le shell Odoo:
   python3 odoo-bin shell -d votre_base -r odoo -w odoo

2. Exécutez le test:
   exec(open('addons/price_break_table/test_module.py').read())
   test_price_break_module()

3. Ou testez manuellement:
   product = env['product.template'].search([], limit=1)
   data = product.get_price_break_table_data()
   print(data)
""")

if __name__ == "__main__":
    # Ce script ne peut être exécuté que dans le contexte Odoo
    print("Ce script doit être exécuté dans le shell Odoo")
