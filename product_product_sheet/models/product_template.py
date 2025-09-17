from odoo import models, _
from odoo.exceptions import UserError

class ProductTemplate(models.Model):
    _inherit = "product.template"

    def _ensure_product_sheet_report(self):
        Report = self.env['ir.actions.report']
        IrModelData = self.env['ir.model.data']

        # 0) Vérifie que le template QWeb existe
        tmpl = self.env.ref('product_product_sheet.report_product_sheet_document_wrapper', raise_if_not_found=False)
        if not tmpl:
            raise UserError(_("Le template QWeb 'product_product_sheet.report_product_sheet_document_wrapper' est introuvable. Mettez à jour / réinstallez le module 'product_product_sheet'."))

        # 1) Tente via XMLID
        action = self.env.ref('product_product_sheet.action_report_product_sheet', raise_if_not_found=False)

        # 2) Cherche par report_name + model
        if not action:
            action = Report.search([
                ('report_name', '=', 'product_product_sheet.report_product_sheet_document_wrapper'),
                ('model', '=', 'product.template'),
            ], limit=1)

        # 3) Crée l'action si absente + enregistre l'XMLID pour la pérenniser
        if not action:
            action = Report.create({
                'name': 'Fiche produit',
                'model': 'product.template',
                'report_type': 'qweb-pdf',
                'report_name': 'product_product_sheet.report_product_sheet_document_wrapper',
                'report_file': 'product_product_sheet.report_product_sheet_document_wrapper',
                'print_report_name': "('Fiche_%s') % (object.display_name.replace('/', '_'))",
            })
            IrModelData.create({
                'name': 'action_report_product_sheet',
                'module': 'product_product_sheet',
                'model': 'ir.actions.report',
                'res_id': action.id,
                'noupdate': True,
            })
        return action

    def action_print_product_sheet(self):
        self.ensure_one()
        action = self._ensure_product_sheet_report()
        return action.report_action(self)