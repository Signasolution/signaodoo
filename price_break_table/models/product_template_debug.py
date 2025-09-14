# -*- coding: utf-8 -*-

from odoo import models, fields, api

class ProductTemplate(models.Model):
    _inherit = 'product.template'

    def get_price_break_table_data_debug(self, pricelist_id=None, partner_id=None, quantity=1.0):
        """
        Version debug simplifiée pour diagnostiquer le problème
        """
        self.ensure_one()
        
        print(f"[DEBUG] === DÉBUT DEBUG PRODUIT {self.name} (ID: {self.id}) ===")
        
        # Récupération de la liste de prix
        if not pricelist_id:
            pricelist_id = 1  # Liste par défaut
        
        pricelist = self.env['product.pricelist'].browse(pricelist_id)
        print(f"[DEBUG] Liste de prix: {pricelist.name if pricelist.exists() else 'NON TROUVÉE'}")
        
        if not pricelist.exists():
            return {'rows': [], 'currency': False, 'current_quantity': quantity}
        
        # Recherche SIMPLE de toutes les règles
        print(f"[DEBUG] Recherche de toutes les règles...")
        all_rules = self.env['product.pricelist.item'].search([
            ('pricelist_id', '=', pricelist.id),
            ('min_quantity', '>', 0),
        ])
        
        print(f"[DEBUG] Total des règles trouvées: {len(all_rules)}")
        
        applicable_rules = []
        
        for rule in all_rules:
            print(f"[DEBUG] Règle {rule.id}:")
            print(f"   - Produit: {rule.product_tmpl_id.name if rule.product_tmpl_id else 'Global'}")
            print(f"   - Variante: {rule.product_id.name if rule.product_id else 'Aucune'}")
            print(f"   - Qty min: {rule.min_quantity}")
            print(f"   - Type: {rule.compute_price}")
            
            # Vérification simple d'applicabilité
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
                # Calcul du prix
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
                    'sequence': rule.id,  # Utiliser l'ID comme séquence
                })
                
                print(f"   ✅ AJOUTÉE: {rule.min_quantity}+ → {price}€")
        
        print(f"[DEBUG] Règles applicables finales: {len(applicable_rules)}")
        
        # Construction du résultat
        table_rows = []
        for rule in applicable_rules:
            min_qty = rule['min_quantity']
            max_qty = rule['max_quantity']
            price = rule['price']
            
            # Formatage de la quantité
            if max_qty and max_qty != float('inf'):
                qty_display = f"{min_qty}+ à {max_qty}"
            else:
                qty_display = f"{min_qty}+"
            
            # Détermination si cette ligne est active
            is_active = min_qty <= quantity and (not max_qty or max_qty >= quantity)
            
            table_rows.append({
                'min_quantity': min_qty,
                'max_quantity': max_qty,
                'quantity_display': qty_display,
                'price': price,
                'price_formatted': pricelist.currency_id.format(price),
                'is_active': is_active,
                'rule_id': rule['id'],
            })
            
            print(f"[DEBUG] Ligne ajoutée: {qty_display} → {price}€")
        
        result = {
            'rows': table_rows,
            'currency': pricelist.currency_id,
            'current_quantity': quantity,
            'pricelist_id': pricelist.id,
        }
        
        print(f"[DEBUG] === FIN DEBUG - {len(table_rows)} ligne(s) ===")
        return result

    @api.model
    def get_price_break_table_js_data_debug(self, product_id, pricelist_id=None, partner_id=None, quantity=1.0):
        """
        Version debug de la méthode appelée par JavaScript
        """
        product = self.browse(product_id)
        if not product.exists():
            return {}
        
        return product.get_price_break_table_data_debug(pricelist_id, partner_id, quantity)
