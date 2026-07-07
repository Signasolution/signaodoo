# -*- coding: utf-8 -*-
import logging

from odoo import fields, models, _
from odoo.exceptions import UserError

from . import watermark_service

_logger = logging.getLogger(__name__)


class ProductProduct(models.Model):
    _inherit = 'product.product'

    x_watermark_original_image = fields.Binary(
        string="Image d'origine (avant filigrane)", attachment=True, copy=False,
        help="Sauvegarde de l'image de la variante avant tout filigranage.",
    )
    x_watermark_applied = fields.Boolean(string="Filigrane appliqué", copy=False, default=False)

    def write(self, vals):
        reset_records = self.browse()
        if 'image_variant_1920' in vals and not self.env.context.get('apply_watermark'):
            reset_records = self.filtered('x_watermark_applied')
        res = super().write(vals)
        if reset_records:
            reset_records.write({'x_watermark_applied': False, 'x_watermark_original_image': False})
        return res

    def _get_website_watermark_config(self):
        self.ensure_one()
        website = self.product_tmpl_id.website_id
        if not website:
            return None
        config_rec = self.env['website.watermark.config'].search(
            [('website_id', '=', website.id)], limit=1)
        return config_rec._get_watermark_config_dict() if config_rec else None

    def _apply_watermark_main_image(self, config):
        """Filigrane l'image propre de la variante (image_variant_1920), en
        repartant toujours de la sauvegarde d'origine.
        """
        self.ensure_one()
        source_image = (
            self.x_watermark_original_image
            if self.x_watermark_applied and self.x_watermark_original_image
            else self.image_variant_1920
        )
        new_image = watermark_service.apply_watermark_to_image(source_image, config)
        vals = {'image_variant_1920': new_image, 'x_watermark_applied': True}
        if not self.x_watermark_applied:
            vals['x_watermark_original_image'] = self.image_variant_1920
        self.with_context(apply_watermark=True).write(vals)

    def _apply_watermark(self, config):
        """Filigrane l'image propre de la variante ET ses images de galerie
        spécifiques (product_variant_image_ids).

        Les images de galerie communes au modèle (product_template_image_ids)
        ne sont PAS traitées ici : elles le sont déjà via le template, ce qui
        évite de filigraner deux fois le même enregistrement product.image.
        """
        self.ensure_one()
        applied_any = False
        if self.image_variant_1920:
            self._apply_watermark_main_image(config)
            applied_any = True
        for extra_image in self.product_variant_image_ids:
            try:
                extra_image._apply_watermark(config)
                applied_any = True
            except watermark_service.WatermarkError as exc:
                _logger.info("Filigrane ignoré pour une image de la variante « %s » : %s", self.display_name, exc)
        if not applied_any:
            raise watermark_service.WatermarkError(_("Variante sans image, filigrane ignoré."))

    def action_apply_watermark(self):
        for variant in self:
            config = variant._get_website_watermark_config()
            if not config:
                raise UserError(_(
                    "Aucune configuration de filigrane trouvée pour le site web de « %s ». "
                    "Configurez-en une depuis Site Web > Site > Filigranes."
                ) % variant.display_name)
            try:
                variant._apply_watermark(config)
            except watermark_service.WatermarkError as exc:
                raise UserError(str(exc)) from exc

    def action_restore_original_image(self):
        for variant in self:
            if variant.x_watermark_original_image:
                variant.with_context(apply_watermark=True).write({
                    'image_variant_1920': variant.x_watermark_original_image,
                    'x_watermark_applied': False,
                })
            variant.product_variant_image_ids.action_restore_original_image()
