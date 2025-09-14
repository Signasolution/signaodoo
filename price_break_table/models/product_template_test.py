# -*- coding: utf-8 -*-

from odoo import models, fields, api

class ProductTemplateTest(models.Model):
    _inherit = 'product.template'

    def get_price_break_table_js_data_test(self, pricelist_id, partner_id=None, quantity=1):
        """
        Version de test qui utilise EXACTEMENT la même logique que la méthode debug
        """
        self.ensure_one()
        
        print(f"[TEST] get_price_break_table_js_data_test - Produit: {self.name}")
        
        try:
            # Récupérer la pricelist
            pricelist = self.env['product.pricelist'].browse(pricelist_id)
            print(f"[TEST] Pricelist: {pricelist.name}")
            
            # Recherche des règles (même logique que debug)
            all_rules = self.env['product.pricelist.item'].search([
                ('pricelist_id', '=', pricelist.id),
                ('min_quantity', '>', 0),
            ])
            
            print(f"[TEST] Total des règles trouvées: {len(all_rules)}")
            
            applicable_rules = []
            
            for rule in all_rules:
                print(f"[TEST] Règle {rule.id}:")
                print(f"   - Produit: {rule.product_tmpl_id.name if rule.product_tmpl_id else 'Global'}")
                print(f"   - Variante: {rule.product_id.name if rule.product_id else 'Aucune'}")
                print(f"   - Qty min: {rule.min_quantity}")
                print(f"   - Type: {rule.compute_price}")
                
                # Vérification simple d'applicabilité (même logique que debug)
                is_applicable = False
                
                # Règle spécifique au produit
                if rule.product_tmpl_id and rule.product_tmpl_id.id == self.id:
                    is_applicable = True
                    print(f"   ✅ APPLICABLE: Spécifique au produit")
                
                # Règle globale
                elif not rule.product_tmpl_id and not rule.product_id:
                    is_applicable = True
                    print(f"   ✅ APPLICABLE: Règle globale")
                
                else:
                    print(f"   ❌ NON APPLICABLE")
                
                if is_applicable:
                    # Calcul du prix (même logique que debug)
                    if rule.compute_price == 'fixed':
                        price = rule.fixed_price
                    elif rule.compute_price == 'percentage':
                        price = self.list_price * (1 - rule.percent_price / 100)
                    else:
                        price = self.list_price
                    
                    applicable_rules.append({
                        'id': rule.id,
                        'min_quantity': rule.min_quantity,
                        'max_quantity': 999999,  # Valeur JSON valide au lieu d'infinity
                        'price': price,
                        'sequence': rule.id,
                    })
                    
                    print(f"   ✅ AJOUTÉE: {rule.min_quantity}+ → {price}€")
            
            print(f"[TEST] Règles applicables finales: {len(applicable_rules)}")
            
            # Tri par quantité minimale
            applicable_rules.sort(key=lambda x: x['min_quantity'])
            
            # Construction du résultat final
            rows = []
            for rule in applicable_rules:
                # Déterminer si cette règle est active pour la quantité actuelle
                is_active = quantity >= rule['min_quantity']
                
                rows.append({
                    'min_quantity': rule['min_quantity'],
                    'max_quantity': rule['max_quantity'],
                    'quantity_display': f"{rule['min_quantity']}+",
                    'price': rule['price'],
                    'price_formatted': f"{rule['price']:,.2f} €".replace(',', ' '),
                    'is_active': is_active,
                    'rule_id': rule['id']
                })
            
            print(f"[TEST] Rows finales: {len(rows)}")
            
            return {
                'rows': rows,
                'currency': pricelist.currency_id,
                'current_quantity': quantity,
                'pricelist_id': pricelist_id
            }
            
        except Exception as e:
            print(f"[TEST] Erreur: {e}")
            import traceback
            traceback.print_exc()
            return {
                'rows': [],
                'currency': self.env['res.currency'].browse(1),
                'current_quantity': quantity,
                'pricelist_id': pricelist_id
            }
