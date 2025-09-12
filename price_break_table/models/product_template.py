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
        
        # Récupération de la liste de prix
        if not pricelist_id:
            pricelist_id = self.env.context.get('pricelist_id')
        if not pricelist_id:
            pricelist = self.env['product.pricelist'].browse(pricelist_id)
        else:
            pricelist = self.env['product.pricelist'].browse(pricelist_id)
        
        if not pricelist.exists():
            pricelist = self.env['product.pricelist'].search([('active', '=', True)], limit=1)
        
        if not pricelist:
            return {'rows': [], 'currency': False, 'current_quantity': quantity}
        
        # Récupération des règles de prix pour ce produit
        price_rules = self._get_price_break_rules(pricelist, partner_id)
        
        if not price_rules:
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
        
        return {
            'rows': table_rows,
            'currency': pricelist.currency_id,
            'current_quantity': quantity,
            'pricelist_id': pricelist.id,
        }

    def _get_price_break_rules(self, pricelist, partner_id=None):
        """
        Récupère les règles de prix dégressifs pour un produit et une liste de prix.
        Utilise la même logique de priorité qu'Odoo.
        """
        self.ensure_one()
        
        # Récupération de toutes les règles applicables
        domain = [
            ('pricelist_id', '=', pricelist.id),
            ('active', '=', True),
            '|',
            ('product_tmpl_id', '=', self.id),
            ('product_id', 'in', self.product_variant_ids.ids),
        ]
        
        if partner_id:
            domain.extend([
                '|',
                ('partner_id', '=', partner_id),
                ('partner_id', '=', False),
            ])
        
        rules = self.env['product.pricelist.item'].search(domain, order='sequence, min_quantity')
        
        # Filtrage et tri selon la logique Odoo
        applicable_rules = []
        for rule in rules:
            # Vérification des conditions de la règle
            if self._is_rule_applicable(rule, partner_id):
                applicable_rules.append({
                    'id': rule.id,
                    'min_quantity': rule.min_quantity,
                    'max_quantity': rule.max_quantity if rule.max_quantity else float('inf'),
                    'price': self._compute_rule_price(rule, pricelist),
                    'sequence': rule.sequence,
                })
        
        # Tri par quantité minimale
        applicable_rules.sort(key=lambda x: x['min_quantity'])
        
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

    def _compute_rule_price(self, rule, pricelist):
        """Calcule le prix selon la règle"""
        if rule.compute_price == 'fixed':
            return rule.fixed_price
        elif rule.compute_price == 'percentage':
            base_price = self.list_price
            return base_price * (1 - rule.percent_price / 100)
        elif rule.compute_price == 'formula':
            # Logique de formule (simplifiée)
            base_price = self.list_price
            return base_price * (1 + rule.price_discount / 100)
        
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
