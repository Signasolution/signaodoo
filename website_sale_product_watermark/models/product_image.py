# -*- coding: utf-8 -*-
from odoo import fields, models, _

from . import watermark_service


class ProductImage(models.Model):
    """Images supplémentaires (galerie) d'un produit ou d'une variante.

    Modèle `product.image` (défini par website_sale), hérité de `image.mixin`
    et donc porteur d'un champ `image_1920`. Même logique de filigranage que
    l'image principale : sauvegarde de l'original, réapplication propre,
    restauration.
    """
    _inherit = 'product.image'

    x_watermark_original_image = fields.Binary(
        string="Image d'origine (avant filigrane)", attachment=True, copy=False,
        help="Sauvegarde de l'image de galerie avant tout filigranage.",
    )
    x_watermark_applied = fields.Boolean(string="Filigrane appliqué", copy=False, default=False)

    def write(self, vals):
        reset_records = self.browse()
        if 'image_1920' in vals and not self.env.context.get('apply_watermark'):
            reset_records = self.filtered('x_watermark_applied')
        res = super().write(vals)
        if reset_records:
            reset_records.write({'x_watermark_applied': False, 'x_watermark_original_image': False})
        return res

    def _apply_watermark(self, config):
        self.ensure_one()
        if not self.image_1920:
            raise watermark_service.WatermarkError(_("Image de galerie vide, filigrane ignoré."))
        source_image = (
            self.x_watermark_original_image
            if self.x_watermark_applied and self.x_watermark_original_image
            else self.image_1920
        )
        new_image = watermark_service.apply_watermark_to_image(source_image, config)
        vals = {'image_1920': new_image, 'x_watermark_applied': True}
        if not self.x_watermark_applied:
            vals['x_watermark_original_image'] = self.image_1920
        self.with_context(apply_watermark=True).write(vals)

    def action_restore_original_image(self):
        for image in self:
            if image.x_watermark_original_image:
                image.with_context(apply_watermark=True).write({
                    'image_1920': image.x_watermark_original_image,
                    'x_watermark_applied': False,
                })
