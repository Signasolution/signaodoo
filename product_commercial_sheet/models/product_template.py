# -*- coding: utf-8 -*-

from odoo import models, fields, api, _


class ProductTemplate(models.Model):
    _inherit = 'product.template'

    commercial_sheet_ids = fields.One2many(
        'product.commercial.sheet',
        'product_id',
        string='Fiches Commerciales',
        help="Fiches commerciales associées à ce produit"
    )
    
    commercial_sheet_count = fields.Integer(
        string='Nombre de fiches',
        compute='_compute_commercial_sheet_count',
        help="Nombre de fiches commerciales pour ce produit"
    )

    @api.depends('commercial_sheet_ids')
    def _compute_commercial_sheet_count(self):
        """Calcule le nombre de fiches commerciales"""
        for product in self:
            product.commercial_sheet_count = len(product.commercial_sheet_ids)

    def action_create_commercial_sheet(self):
        """Action pour créer une fiche commerciale"""
        return self.env['product.commercial.sheet'].create_from_product(self.id)

    def action_view_commercial_sheets(self):
        """Affiche les fiches commerciales du produit"""
        action = self.env['ir.actions.act_window']._for_xml_id('product_commercial_sheet.action_product_commercial_sheet')
        action['domain'] = [('product_id', '=', self.id)]
        action['context'] = {
            'default_product_id': self.id,
            'search_default_product_id': self.id,
        }
        return action
