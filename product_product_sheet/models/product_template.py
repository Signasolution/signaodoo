from odoo import models, _, api
from odoo.exceptions import UserError

class ProductTemplate(models.Model):
    _inherit = "product.template"

    def action_print_product_sheet(self):
        self.ensure_one()
        # 1) Essai direct via XMLID
        report = self.env.ref("product_product_sheet.action_report_product_sheet", raise_if_not_found=False)
        # 2) Cherche via ir.model.data si absent (cas d'incohérence de registre)
        if not report:
            irmd = self.env['ir.model.data'].search([
                ('module', '=', 'product_product_sheet'),
                ('name', '=', 'action_report_product_sheet'),
            ], limit=1)
            if irmd and irmd.model == 'ir.actions.report' and irmd.res_id:
                report = self.env['ir.actions.report'].browse(irmd.res_id)
        # 3) Fallback final: recherche par report_name + model
        if not report:
            report = self.env['ir.actions.report'].search([
                ('report_name', '=', 'product_product_sheet.report_product_sheet_document_wrapper'),
                ('model', '=', 'product.template'),
            ], limit=1)
        if not report:
            raise UserError(_("Le rapport 'Fiche produit' est introuvable. Veuillez réinstaller/mettre à jour le module 'product_product_sheet'."))
        return report.report_action(self)