# -*- coding: utf-8 -*-

from odoo import models, fields, api
from odoo.tools import float_round
import json


class ProductTemplate(models.Model):
    _inherit = 'product.template'

    def get_price_break_table_data(self, pricelist_id=None, partner_id=None, quantity=1.0):
        """
        Retourne les données du tableau de prix dégressifs pour un produit donné.
        
        :param pricelist_id: ID de la liste de prix à utiliser
        :param partner_id: ID du partenaire pour les prix spécifiques
        :param quantity: Quantité actuelle pour la surbrillance
        :return: dict avec les données du tableau
        """
        self.ensure_one()
        
        # Debug: Log des paramètres d'entrée
        print(f"[DEBUG] get_price_break_table_data - Produit: {self.name} (ID: {self.id})")
        print(f"[DEBUG] Paramètres: pricelist_id={pricelist_id}, partner_id={partner_id}, quantity={quantity}")
        
        # Récupération de la liste de prix
        if not pricelist_id:
            pricelist_id = self.env.context.get('pricelist_id')
        
        if pricelist_id:
            pricelist = self.env['product.pricelist'].browse(pricelist_id)
            print(f"[DEBUG] Liste de prix trouvée par ID: {pricelist.name if pricelist.exists() else 'NON TROUVÉE'}")
        else:
            pricelist = self.env['product.pricelist'].search([('active', '=', True)], limit=1)
            print(f"[DEBUG] Liste de prix par défaut: {pricelist.name if pricelist else 'AUCUNE'}")
        
        if not pricelist.exists():
            pricelist = self.env['product.pricelist'].search([('active', '=', True)], limit=1)
        
        if not pricelist:
            print(f"[DEBUG] Aucune liste de prix active trouvée")
            return {'rows': [], 'currency': False, 'current_quantity': quantity}
        
        print(f"[DEBUG] Liste de prix utilisée: {pricelist.name} (ID: {pricelist.id})")
        
        # Récupération des règles de prix pour ce produit
        price_rules = self._get_price_break_rules(pricelist, partner_id)
        
        print(f"[DEBUG] Règles trouvées: {len(price_rules)}")
        
        if not price_rules:
            print(f"[DEBUG] Aucune règle de prix dégressif trouvée")
            return {'rows': [], 'currency': pricelist.currency_id, 'current_quantity': quantity}
        
        # Construction des lignes du tableau
        table_rows = []
        for rule in price_rules:
            min_qty = rule.get('min_quantity', 0)
            max_qty = rule.get('max_quantity', 0)
            price = rule.get('price', 0)
            
            # Formatage de la quantité
            if max_qty and max_qty != float('inf'):
                qty_display = f"{min_qty}+ à {max_qty}"
            else:
                qty_display = f"{min_qty}+"
            
            # Détermination si cette ligne est active (correspond à la quantité actuelle)
            is_active = min_qty <= quantity and (not max_qty or max_qty >= quantity)
            
            table_rows.append({
                'min_quantity': min_qty,
                'max_quantity': max_qty,
                'quantity_display': qty_display,
                'price': price,
                'price_formatted': pricelist.currency_id.format(price),
                'is_active': is_active,
                'rule_id': rule.get('id'),
            })
            
            print(f"[DEBUG] Règle ajoutée: {qty_display} → {price}€")
        
        result = {
            'rows': table_rows,
            'currency': pricelist.currency_id,
            'current_quantity': quantity,
            'pricelist_id': pricelist.id,
        }
        
        print(f"[DEBUG] Résultat final: {len(table_rows)} ligne(s)")
        return result

    def _get_price_break_rules(self, pricelist, partner_id=None):
        """
        Récupère les règles de prix dégressifs pour un produit et une liste de prix.
        Utilise la même logique de priorité qu'Odoo.
        """
        self.ensure_one()
        
        print(f"[DEBUG] _get_price_break_rules - Produit: {self.name}, Liste: {pricelist.name}")
        
        # Récupération de toutes les règles applicables
        domain = [
            ('pricelist_id', '=', pricelist.id),
            ('active', '=', True),
            ('min_quantity', '>', 0),  # Seulement les règles avec quantité minimale
        ]
        
        # Recherche des règles spécifiques au produit
        product_domain = domain + [
            '|',
            ('product_tmpl_id', '=', self.id),
            ('product_id', 'in', self.product_variant_ids.ids),
        ]
        
        # Recherche des règles globales (sans produit spécifique)
        global_domain = domain + [
            ('product_tmpl_id', '=', False),
            ('product_id', '=', False),
        ]
        
        # Recherche des règles par catégorie
        category_domain = domain + [
            ('product_tmpl_id', '=', False),
            ('product_id', '=', False),
            ('categ_id', '!=', False),
        ]
        
        print(f"[DEBUG] Recherche des règles spécifiques au produit...")
        product_rules = self.env['product.pricelist.item'].search(product_domain, order='sequence, min_quantity')
        print(f"[DEBUG] Règles spécifiques trouvées: {len(product_rules)}")
        
        print(f"[DEBUG] Recherche des règles globales...")
        global_rules = self.env['product.pricelist.item'].search(global_domain, order='sequence, min_quantity')
        print(f"[DEBUG] Règles globales trouvées: {len(global_rules)}")
        
        print(f"[DEBUG] Recherche des règles par catégorie...")
        category_rules = self.env['product.pricelist.item'].search(category_domain, order='sequence, min_quantity')
        print(f"[DEBUG] Règles par catégorie trouvées: {len(category_rules)}")
        
        # Combiner toutes les règles
        all_rules = product_rules + global_rules + category_rules
        
        print(f"[DEBUG] Total des règles à évaluer: {len(all_rules)}")
        
        # Filtrage et tri selon la logique Odoo
        applicable_rules = []
        for rule in all_rules:
            print(f"[DEBUG] Évaluation de la règle {rule.id}: Qty min={rule.min_quantity}, Produit={rule.product_tmpl_id.name if rule.product_tmpl_id else 'Global'}")
            
            # Vérification des conditions de la règle
            if self._is_rule_applicable(rule, partner_id):
                # Calcul du prix réel avec la méthode Odoo
                price = self._compute_price_with_pricelist(pricelist, rule)
                applicable_rules.append({
                    'id': rule.id,
                    'min_quantity': rule.min_quantity,
                    'max_quantity': rule.max_quantity if rule.max_quantity else float('inf'),
                    'price': price,
                    'sequence': rule.sequence,
                })
                print(f"[DEBUG] Règle {rule.id} ajoutée: {rule.min_quantity}+ → {price}€")
            else:
                print(f"[DEBUG] Règle {rule.id} non applicable")
        
        # Tri par quantité minimale
        applicable_rules.sort(key=lambda x: x['min_quantity'])
        
        print(f"[DEBUG] Règles finales applicables: {len(applicable_rules)}")
        return applicable_rules

    def _is_rule_applicable(self, rule, partner_id=None):
        """Vérifie si une règle de prix est applicable"""
        # Vérification du partenaire
        if rule.partner_id and partner_id and rule.partner_id.id != partner_id:
            return False
        
        # Vérification des dates
        if rule.date_start and rule.date_start > fields.Datetime.now():
            return False
        if rule.date_end and rule.date_end < fields.Datetime.now():
            return False
        
        # Vérification des catégories
        if rule.categ_id and rule.categ_id not in self.categ_id.parent_path.split('/'):
            return False
        
        return True

    def _compute_price_with_pricelist(self, pricelist, rule):
        """Calcule le prix selon la règle avec la méthode Odoo standard"""
        try:
            # Utilisation de la méthode standard d'Odoo pour calculer le prix
            if rule.compute_price == 'fixed':
                return rule.fixed_price
            elif rule.compute_price == 'percentage':
                base_price = self.list_price
                return base_price * (1 - rule.percent_price / 100)
            elif rule.compute_price == 'formula':
                # Logique de formule (simplifiée)
                base_price = self.list_price
                return base_price * (1 + rule.price_discount / 100)
            
            # Fallback : prix de base
            return self.list_price
        except Exception:
            return self.list_price

    @api.model
    def get_price_break_table_js_data(self, product_id, pricelist_id=None, partner_id=None, quantity=1.0):
        """
        Méthode appelée par JavaScript pour récupérer les données du tableau
        """
        product = self.browse(product_id)
        if not product.exists():
            return {}
        
        return product.get_price_break_table_data(pricelist_id, partner_id, quantity)
