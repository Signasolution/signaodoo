from odoo import models

class ProductTemplate(models.Model):
    _inherit = "product.template"

    def action_print_product_sheet(self):
        self.ensure_one()
        return self.env.ref("product_product_sheet.action_report_product_sheet").report_action(self)