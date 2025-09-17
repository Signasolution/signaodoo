from odoo import models

class ProductTemplate(models.Model):
    _inherit = "product.template"

    def action_print_product_sheet(self):
        self.ensure_one()
        # Appelle le rapport QWeb par son XMLID et imprime la fiche pour ce produit
        return self.env.ref("product_product_sheet.action_report_product_sheet").report_action(self)