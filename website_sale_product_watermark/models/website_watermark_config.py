# -*- coding: utf-8 -*-
import base64
import logging
import os

from odoo import api, fields, models, _
from odoo.exceptions import ValidationError

from . import watermark_service

_logger = logging.getLogger(__name__)

_SAMPLE_IMAGE_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'static', 'img', 'sample_product.png')

_BATCH_SIZE = 50

_POSITION_SELECTION = [
    ('top_left', "Haut gauche"),
    ('top_center', "Haut centre"),
    ('top_right', "Haut droite"),
    ('middle_left', "Milieu gauche"),
    ('center', "Centre"),
    ('middle_right', "Milieu droite"),
    ('bottom_left', "Bas gauche"),
    ('bottom_center', "Bas centre"),
    ('bottom_right', "Bas droite"),
]


class WebsiteWatermarkConfig(models.Model):
    _name = 'website.watermark.config'
    _description = "Configuration du filigrane pour un site web"

    website_id = fields.Many2one(
        'website', string="Site Web", required=True, ondelete='cascade',
        default=lambda self: self.env['website'].get_current_website().id,
    )

    watermark_type = fields.Selection(
        [('text', "Texte"), ('image', "Image")],
        string="Type de filigrane", default='text', required=True,
    )
    text_content = fields.Char(string="Texte du filigrane", default="© Votre Marque")
    font_family = fields.Selection(
        [
            ('dejavu_sans', "DejaVu Sans"),
            ('dejavu_sans_bold', "DejaVu Sans (Gras)"),
            ('custom', "Police personnalisée"),
        ],
        string="Police", default='dejavu_sans_bold', required=True,
    )
    custom_font_file = fields.Binary(string="Fichier de police (.ttf)", attachment=True)
    custom_font_filename = fields.Char(string="Nom du fichier de police")
    font_color = fields.Char(string="Couleur du texte", default='#FFFFFF')

    watermark_image = fields.Image(
        string="Image du filigrane (PNG ou JPEG)", max_width=0, max_height=0, attachment=True,
        help="PNG recommandé pour un détourage avec transparence (RGBA). Un JPEG est "
             "aussi accepté, mais son fond (opaque) sera visible sur le produit.",
    )

    position = fields.Selection(_POSITION_SELECTION, string="Position", default='bottom_right', required=True)
    margin = fields.Integer(string="Marge (px)", default=20)
    rotation = fields.Float(string="Rotation (degrés)", default=0.0)
    opacity = fields.Integer(string="Opacité (0-255)", default=180)
    resize_ratio = fields.Float(
        string="Ratio de redimensionnement",
        default=0.25,
        help="Largeur du filigrane en proportion de la largeur de l'image cible (ex : 0.25 = 25%).",
    )

    preview_image = fields.Binary(
        string="Aperçu", compute='_compute_preview_image',
        help="Filigrane appliqué à une image produit d'exemple, recalculé à chaque modification.",
    )

    _sql_constraints = [
        ('website_id_uniq', 'unique(website_id)', "Une configuration de filigrane existe déjà pour ce site web."),
    ]

    @api.depends(
        'watermark_type', 'text_content', 'font_family', 'custom_font_file', 'font_color',
        'watermark_image', 'position', 'margin', 'rotation', 'opacity', 'resize_ratio',
    )
    def _compute_preview_image(self):
        with open(_SAMPLE_IMAGE_PATH, 'rb') as sample_file:
            sample_b64 = base64.b64encode(sample_file.read())
        for record in self:
            try:
                config = record._get_watermark_config_dict()
                record.preview_image = watermark_service.apply_watermark_to_image(sample_b64, config)
            except watermark_service.WatermarkError:
                record.preview_image = sample_b64

    @api.constrains('watermark_image')
    def _check_watermark_image_format(self):
        for record in self:
            if record.watermark_image:
                try:
                    watermark_service.validate_watermark_image(base64.b64decode(record.watermark_image))
                except watermark_service.WatermarkError as exc:
                    raise ValidationError(str(exc)) from exc

    def _get_watermark_config_dict(self):
        self.ensure_one()
        return {
            'watermark_type': self.watermark_type,
            'text_content': self.text_content,
            'font_family': self.font_family,
            'custom_font_file': base64.b64decode(self.custom_font_file) if self.custom_font_file else None,
            'font_color': self.font_color,
            'watermark_image_bytes': base64.b64decode(self.watermark_image) if self.watermark_image else None,
            'position': self.position,
            'margin': self.margin,
            'rotation': self.rotation,
            'opacity': self.opacity,
            'resize_ratio': self.resize_ratio,
        }

    def action_apply_to_website_products(self):
        self.ensure_one()
        config = self._get_watermark_config_dict()

        templates = self.env['product.template'].search([('website_id', '=', self.website_id.id)])
        processed, skipped = 0, 0
        for index, template in enumerate(templates, start=1):
            try:
                template._apply_watermark(config)
                processed += 1
            except watermark_service.WatermarkError as exc:
                skipped += 1
                _logger.info("Filigrane ignoré pour %s : %s", template.display_name, exc)
            if index % _BATCH_SIZE == 0:
                self.env.cr.commit()
        self.env.cr.commit()

        # Variantes ayant soit une image propre, soit une galerie propre :
        # les deux sont filigranées par variant._apply_watermark.
        variants = self.env['product.product'].search([
            ('product_tmpl_id', 'in', templates.ids),
            '|',
            ('image_variant_1920', '!=', False),
            ('product_variant_image_ids', '!=', False),
        ])
        variants_processed = 0
        for index, variant in enumerate(variants, start=1):
            try:
                variant._apply_watermark(config)
                variants_processed += 1
            except watermark_service.WatermarkError as exc:
                _logger.info("Filigrane ignoré pour la variante %s : %s", variant.display_name, exc)
            if index % _BATCH_SIZE == 0:
                self.env.cr.commit()
        self.env.cr.commit()

        message = _(
            "Filigrane appliqué à %(processed)s produit(s) et %(variants)s variante(s) "
            "(%(skipped)s produit(s) ignoré(s), sans image)."
        ) % {'processed': processed, 'variants': variants_processed, 'skipped': skipped}
        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': _("Application du filigrane terminée"),
                'message': message,
                'type': 'success',
                'sticky': False,
            },
        }
