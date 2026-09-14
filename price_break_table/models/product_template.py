# -*- coding: utf-8 -*-

import logging

from odoo import models, fields
from odoo.http import request

_logger = logging.getLogger(__name__)


class ProductTemplate(models.Model):
    _inherit = 'product.template'

    price_break_item_ids = fields.One2many(
        'product.pricelist.item',
        'product_tmpl_id',
        domain=[('min_quantity', '>', 0)],
        string='Prix dégressifs',
    )
    min_purchase_qty_ids = fields.One2many(
        'product.min.purchase.qty',
        'product_tmpl_id',
        string="Quantités minimales d'achat",
    )
    pricelist_discount_ids = fields.One2many(
        'product.pricelist.discount',
        'product_tmpl_id',
        string="Remises catégories clients",
    )

    def action_sync_pricelist_min_qty(self):
        """Crée une ligne de qté min pour chaque liste de prix active manquante."""
        self.ensure_one()
        pricelists = self.env['product.pricelist'].search([('active', '=', True)])
        existing_ids = self.min_purchase_qty_ids.mapped('pricelist_id').ids
        to_create = pricelists.filtered(lambda p: p.id not in existing_ids)
        for pricelist in to_create:
            self.env['product.min.purchase.qty'].create({
                'product_tmpl_id': self.id,
                'pricelist_id': pricelist.id,
                'min_purchase_qty': 0.0,
            })
        # Retourner False recharge le formulaire et rafraîchit le tableau sans rechargement de page
        return False

    def action_generate_discount_tarifs(self):
        """Génère/met à jour les règles de prix dans les listes cibles depuis les remises définies."""
        self.ensure_one()
        PricelistItem = self.env['product.pricelist.item']
        count = 0
        for discount in self.pricelist_discount_ids:
            base_items = PricelistItem.search([
                ('pricelist_id', '=', discount.base_pricelist_id.id),
                ('product_tmpl_id', '=', self.id),
                ('min_quantity', '>', 0),
            ], order='min_quantity')
            for item in base_items:
                base_price = discount._get_item_base_price(item, self.list_price)
                target_price = base_price * (1.0 - discount.discount_percent / 100.0)
                existing = PricelistItem.search([
                    ('pricelist_id', '=', discount.target_pricelist_id.id),
                    ('product_tmpl_id', '=', self.id),
                    ('min_quantity', '=', item.min_quantity),
                ], limit=1)
                vals = {
                    'pricelist_id': discount.target_pricelist_id.id,
                    'product_tmpl_id': self.id,
                    'min_quantity': item.min_quantity,
                    'compute_price': 'fixed',
                    'fixed_price': target_price,
                }
                if existing:
                    existing.write(vals)
                else:
                    PricelistItem.create(vals)
                count += 1
        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': 'Tarifs générés',
                'message': '%d règle(s) créée(s) ou mise(s) à jour.' % count,
                'type': 'success',
                'sticky': False,
            },
        }

    @staticmethod
    def _price_break_cache():
        """Cache à l'échelle de la requête HTTP, ou None hors contexte web.

        Les pages de liste (boutique, catégorie, snippets) rendent des dizaines de
        produits : sans mémoïsation, la résolution de la liste de prix et la
        recherche de ses paliers seraient relancées pour chacun d'eux.
        """
        try:
            if not request:
                return None
        except Exception:
            return None
        cache = getattr(request, '_price_break_cache', None)
        if cache is None:
            cache = {}
            try:
                request._price_break_cache = cache
            except Exception:
                return None
        return cache

    @staticmethod
    def _price_break_diag(message, *args):
        """Trace de diagnostic temporaire (voir commit diag). A retirer ensuite.

        Ne doit jamais faire echouer le rendu d'une page : tout est avale.
        """
        try:
            _logger.info('[PRICE_BREAK] ' + message, *args)
        except Exception:
            pass

    def _get_price_break_pricelist(self, pricelist_id=None):
        """Liste de prix à utiliser pour l'affichage site de ce produit.

        Priorité au paramètre explicite, puis au contexte standard Odoo
        ('pricelist' est la clé utilisée par website_sale pour propager la
        pricelist du visiteur, pas 'pricelist_id'), puis à la pricelist du panier
        courant s'il existe déjà (même résolution que
        WebsiteSalePriceBreak.cart_update_json), puis à la pricelist "courante" du
        site web. Sans ça, on peut récupérer une pricelist différente de celle
        réellement appliquée au panier du visiteur sur ce site.

        On ne force pas la création du panier ici : ce serait un effet de bord
        (panier vide créé à chaque simple visite de page produit) pour un cas qui
        n'est plus nécessaire une fois min_purchase_qty calculé correctement.
        """
        if not pricelist_id:
            pricelist_id = self.env.context.get('pricelist') or self.env.context.get('pricelist_id')
        if pricelist_id:
            pricelist = self.env['product.pricelist'].browse(pricelist_id).exists()
            if pricelist:
                return pricelist

        cache = self._price_break_cache()
        if cache is not None and 'pricelist' in cache:
            return cache['pricelist']

        pricelist = False
        source = 'aucune'
        order = None
        website_pricelist = False
        error = None
        try:
            order = request.website.sale_get_order()
            if order and order.pricelist_id:
                pricelist = order.pricelist_id
                source = 'panier'
            else:
                # get_current_pricelist() n'existe plus en Odoo 18 : le champ
                # calcule la liste de prix du visiteur (partenaire, geoip, code
                # promo). Meme resolution que WebsiteSalePriceBreak.
                website_pricelist = request.website.pricelist_id
                pricelist = website_pricelist
                source = 'website.pricelist_id'
        except Exception as exc:
            error = exc
        if not pricelist:
            pricelist = self.env['product.pricelist'].search([('active', '=', True)], limit=1)
            source = 'repli premiere liste active'

        try:
            self._price_break_diag(
                'resolution | uid=%s login=%s share=%s | societe_active=%s (%s) '
                '| site=%s societe_site=%s | partenaire=%s tarif_partenaire=%s '
                '| panier=%s tarif_panier=%s | website.pricelist_id=%s '
                '| ctx_pricelist=%s | erreur=%r | RETENUE=%s (id=%s, source=%s)',
                self.env.uid,
                self.env.user.login,
                self.env.user.share,
                self.env.company.display_name, self.env.company.id,
                request.website.id,
                request.website.company_id.display_name,
                self.env.user.partner_id.display_name,
                self.env.user.partner_id.property_product_pricelist.display_name,
                order and order.id,
                order and order.pricelist_id.display_name,
                website_pricelist and website_pricelist.display_name,
                self.env.context.get('pricelist') or self.env.context.get('pricelist_id'),
                error,
                pricelist and pricelist.display_name,
                pricelist and pricelist.id,
                source,
            )
        except Exception:
            pass

        if cache is not None:
            cache['pricelist'] = pricelist
        return pricelist

    def _get_min_purchase_qty(self, pricelist):
        """Quantité minimale de commande de ce produit pour une liste de prix (0 = aucune)."""
        self.ensure_one()
        if not pricelist:
            return 0
        rule = self.env['product.min.purchase.qty'].sudo().search([
            ('product_tmpl_id', '=', self.id),
            ('pricelist_id', '=', pricelist.id),
            ('min_purchase_qty', '>', 0),
        ], limit=1)
        return rule.min_purchase_qty if rule else 0

    def get_website_min_purchase_qty(self):
        """Quantité minimale d'achat pour la liste de prix active sur le site."""
        self.ensure_one()
        return self._get_min_purchase_qty(self._get_price_break_pricelist())

    def get_price_break_table_data(self, pricelist_id=None):
        """Données du tableau de prix dégressifs pour la page produit du site.

        :param pricelist_id: ID de la liste de prix à forcer (sinon résolution
            automatique via _get_price_break_pricelist)
        :return: dict avec les clés rows, currency, pricelist_id, min_purchase_qty
        """
        self.ensure_one()

        pricelist = self._get_price_break_pricelist(pricelist_id)
        if not pricelist:
            return {'rows': [], 'currency': False, 'pricelist_id': False, 'min_purchase_qty': 0}

        rules = self._get_price_break_rules(pricelist)

        # La remise affichée est relative au premier palier de la même liste de prix :
        # le tableau montre le gain lié au volume, sans y mélanger la remise dont le
        # visiteur bénéficie déjà au titre de sa catégorie de client.
        reference_price = rules[0]['price'] if rules else 0.0

        rows = []
        for rule in rules:
            price = rule['price']
            min_qty = rule['min_quantity']
            discount = (reference_price - price) / reference_price * 100.0 if reference_price else 0.0
            rows.append({
                'min_quantity': min_qty,
                'quantity_display': '%s+' % (int(min_qty) if min_qty == int(min_qty) else min_qty),
                'price': price,
                'price_formatted': pricelist.currency_id.format(price),
                'discount_percent': discount,
                'discount_display': self._format_price_break_discount(discount),
            })

        min_purchase_qty = self._get_min_purchase_qty(pricelist)
        self._price_break_diag(
            'fiche produit | produit=%s (id=%s) categorie=%s | tarif=%s '
            '| %s ligne(s) -> tableau %s | qte_mini=%s',
            self.display_name, self.id, self.categ_id.display_name,
            pricelist.display_name, len(rows),
            'affiche' if len(rows) > 1 else 'MASQUE',
            min_purchase_qty,
        )

        return {
            'rows': rows,
            'currency': pricelist.currency_id,
            'pricelist_id': pricelist.id,
            'min_purchase_qty': min_purchase_qty,
        }

    @staticmethod
    def _format_price_break_discount(discount):
        """« -12,5 % » (espace insécable) ; chaîne vide si la remise est nulle ou négative."""
        rounded = round(discount, 1)
        if rounded <= 0:
            return ''
        return ('-%g %%' % rounded).replace('.', ',')

    def _get_price_break_items(self, pricelist):
        """Toutes les règles à palier de la liste de prix, mémoïsées pour la requête.

        Le filtrage par produit se fait ensuite en Python (voir
        _get_price_break_rules) : une seule recherche sert ainsi tous les produits
        d'une page de liste.
        """
        cache = self._price_break_cache()
        key = ('items', pricelist.id)
        if cache is not None and key in cache:
            return cache[key]

        # sudo() : les paliers relevent du catalogue public, mais
        # product.pricelist.item est filtre par la regle multi-societe. Un
        # utilisateur interne dont la societe active n'est pas celle du site ne
        # verrait aucun palier et le tableau disparaitrait de la fiche produit.
        items = self.env['product.pricelist.item'].sudo().search([
            ('pricelist_id', '=', pricelist.id),
            ('min_quantity', '>', 0),
        ])

        self._price_break_diag(
            'paliers | tarif=%s (id=%s) | %s regle(s) min_quantity>0 dans cette liste',
            pricelist.display_name, pricelist.id, len(items),
        )

        if cache is not None:
            cache[key] = items
        return items

    def get_price_break_from_price(self):
        """Meilleur palier à annoncer sur les cartes produit des pages de liste.

        :return: dict (prix, quantité, libellés) ou False si le produit n'a pas de
            palier avantageux — auquel cas la carte garde son prix habituel.
        """
        self.ensure_one()

        pricelist = self._get_price_break_pricelist()
        if not pricelist:
            return False

        rules = self._get_price_break_rules(pricelist)
        if len(rules) < 2:
            return False

        best = min(rules, key=lambda rule: rule['price'])
        # Rien à annoncer si le meilleur palier ne fait pas mieux que le premier.
        if best['price'] >= rules[0]['price']:
            return False

        min_qty = best['min_quantity']
        qty_display = int(min_qty) if min_qty == int(min_qty) else min_qty
        uom = (self.uom_name or '').lower()

        return {
            'price': round(best['price'], 2),
            'price_formatted': pricelist.currency_id.format(best['price']),
            'currency_name': pricelist.currency_id.name,
            'min_quantity': min_qty,
            'quantity_label': 'dès %s %s' % (qty_display, uom) if uom else 'dès %s' % qty_display,
        }

    def _get_price_break_rules(self, pricelist):
        """Paliers de la liste de prix applicables à ce produit, triés par quantité.

        Ne gère que les types de calcul Fixe et Remise (%) : une règle en Formule
        retombe sur le prix de vente du produit.
        """
        self.ensure_one()

        items = self._get_price_break_items(pricelist)

        # parent_path vaut « 1/5/12/ » : les ids de la catégorie et de ses parents.
        categ_path = (self.categ_id.parent_path or '').split('/')

        rules = []
        for item in items:
            if item.product_tmpl_id:
                applicable = item.product_tmpl_id.id == self.id
            elif item.product_id:
                applicable = item.product_id.product_tmpl_id.id == self.id
            elif item.categ_id:
                applicable = str(item.categ_id.id) in categ_path
            else:
                applicable = True
            if not applicable:
                continue

            if item.compute_price == 'fixed':
                price = item.fixed_price
            elif item.compute_price == 'percentage':
                price = self.list_price * (1 - item.percent_price / 100)
            else:
                price = self.list_price

            rules.append({'min_quantity': item.min_quantity, 'price': price})

        rules.sort(key=lambda rule: rule['min_quantity'])
        return rules
