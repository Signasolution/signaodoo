from odoo import models, api, _
from odoo.exceptions import UserError

class ProductTemplate(models.Model):
    _inherit = "product.template"

    def action_print_product_sheet(self):
        self.ensure_one()
        try:
            return self.env.ref("product_product_sheet.action_report_product_sheet").report_action(self)
        except Exception as e:
            raise UserError(_("Erreur lors de la génération de la fiche produit : %s") % str(e))