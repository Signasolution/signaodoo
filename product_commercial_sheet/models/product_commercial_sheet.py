# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import UserError
import base64
import io


class ProductCommercialSheet(models.Model):
    _name = 'product.commercial.sheet'
    _description = 'Fiche Commerciale Produit'
    _order = 'create_date desc'

    name = fields.Char(
        string='Nom de la fiche',
        required=True,
        help="Nom de la fiche commerciale"
    )
    
    product_id = fields.Many2one(
        'product.template',
        string='Produit',
        required=True,
        ondelete='cascade',
        help="Produit associé à cette fiche commerciale"
    )
    
    # Champs de base du produit (automatiquement remplis)
    product_name = fields.Char(
        string='Nom du produit',
        related='product_id.name',
        store=True,
        readonly=True
    )
    
    product_reference = fields.Char(
        string='Référence',
        related='product_id.default_code',
        store=True,
        readonly=True
    )
    
    product_description = fields.Html(
        string='Description',
        related='product_id.description_sale',
        readonly=True
    )
    
    # Champs personnalisables (à configurer via Studio)
    custom_field_1 = fields.Char(
        string='Champ personnalisé 1',
        help="Champ personnalisable via Odoo Studio"
    )
    
    custom_field_2 = fields.Char(
        string='Champ personnalisé 2',
        help="Champ personnalisable via Odoo Studio"
    )
    
    custom_field_3 = fields.Text(
        string='Champ personnalisé 3',
        help="Champ personnalisable via Odoo Studio"
    )
    
    custom_field_4 = fields.Selection([
        ('option1', 'Option 1'),
        ('option2', 'Option 2'),
        ('option3', 'Option 3'),
    ], string='Champ personnalisé 4', help="Champ personnalisable via Odoo Studio")
    
    custom_field_5 = fields.Float(
        string='Champ personnalisé 5',
        help="Champ personnalisable via Odoo Studio"
    )
    
    custom_field_6 = fields.Date(
        string='Champ personnalisé 6',
        help="Champ personnalisable via Odoo Studio"
    )
    
    custom_field_7 = fields.Datetime(
        string='Champ personnalisé 7',
        help="Champ personnalisable via Odoo Studio"
    )
    
    custom_field_8 = fields.Boolean(
        string='Champ personnalisé 8',
        help="Champ personnalisable via Odoo Studio"
    )
    
    # Champs techniques
    state = fields.Selection([
        ('draft', 'Brouillon'),
        ('confirmed', 'Confirmée'),
        ('published', 'Publiée'),
    ], string='État', default='draft', required=True)
    
    user_id = fields.Many2one(
        'res.users',
        string='Créé par',
        default=lambda self: self.env.user,
        readonly=True
    )
    
    create_date = fields.Datetime(
        string='Date de création',
        readonly=True
    )
    
    # PDF généré
    pdf_file = fields.Binary(
        string='Fichier PDF',
        readonly=True,
        help="Fichier PDF de la fiche commerciale"
    )
    
    pdf_filename = fields.Char(
        string='Nom du fichier PDF',
        readonly=True
    )

    @api.model
    def create_from_product(self, product_id):
        """
        Crée une fiche commerciale à partir d'un produit
        """
        product = self.env['product.template'].browse(product_id)
        if not product.exists():
            raise UserError(_("Le produit sélectionné n'existe pas."))
        
        # Vérifier s'il existe déjà une fiche pour ce produit
        existing_sheet = self.search([
            ('product_id', '=', product_id),
            ('state', 'in', ['draft', 'confirmed'])
        ], limit=1)
        
        if existing_sheet:
            return {
                'type': 'ir.actions.act_window',
                'name': _('Fiche Commerciale Existante'),
                'res_model': 'product.commercial.sheet',
                'res_id': existing_sheet.id,
                'view_mode': 'form',
                'target': 'current',
            }
        
        # Créer la nouvelle fiche
        sheet_data = {
            'name': f"Fiche commerciale - {product.name}",
            'product_id': product_id,
            'state': 'draft',
        }
        
        sheet = self.create(sheet_data)
        
        return {
            'type': 'ir.actions.act_window',
            'name': _('Nouvelle Fiche Commerciale'),
            'res_model': 'product.commercial.sheet',
            'res_id': sheet.id,
            'view_mode': 'form',
            'target': 'current',
        }

    def action_confirm(self):
        """Confirme la fiche commerciale"""
        self.write({'state': 'confirmed'})
        return True

    def action_publish(self):
        """Publie la fiche commerciale"""
        self.write({'state': 'published'})
        return True

    def action_draft(self):
        """Remet en brouillon"""
        self.write({'state': 'draft'})
        return True

    def action_generate_pdf(self):
        """Génère le PDF de la fiche commerciale"""
        # Cette méthode sera implémentée avec le rapport
        return {
            'type': 'ir.actions.report',
            'report_name': 'product_commercial_sheet.report_commercial_sheet',
            'report_type': 'qweb-pdf',
            'data': {'ids': self.ids},
            'context': self.env.context,
        }

    @api.model
    def get_custom_fields_config(self):
        """
        Retourne la configuration des champs personnalisés
        Utile pour Odoo Studio
        """
        return {
            'custom_field_1': {
                'type': 'char',
                'string': 'Champ personnalisé 1',
                'help': 'Champ personnalisable via Odoo Studio'
            },
            'custom_field_2': {
                'type': 'char', 
                'string': 'Champ personnalisé 2',
                'help': 'Champ personnalisable via Odoo Studio'
            },
            'custom_field_3': {
                'type': 'text',
                'string': 'Champ personnalisé 3', 
                'help': 'Champ personnalisable via Odoo Studio'
            },
            'custom_field_4': {
                'type': 'selection',
                'string': 'Champ personnalisé 4',
                'help': 'Champ personnalisable via Odoo Studio'
            },
            'custom_field_5': {
                'type': 'float',
                'string': 'Champ personnalisé 5',
                'help': 'Champ personnalisable via Odoo Studio'
            },
            'custom_field_6': {
                'type': 'date',
                'string': 'Champ personnalisé 6',
                'help': 'Champ personnalisable via Odoo Studio'
            },
            'custom_field_7': {
                'type': 'datetime',
                'string': 'Champ personnalisé 7',
                'help': 'Champ personnalisable via Odoo Studio'
            },
            'custom_field_8': {
                'type': 'boolean',
                'string': 'Champ personnalisé 8',
                'help': 'Champ personnalisable via Odoo Studio'
            },
        }
