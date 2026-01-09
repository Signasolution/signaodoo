# -*- coding: utf-8 -*-
from odoo import api, models

class SaleOrder(models.Model):
    _inherit = "sale.order"

    def _get_signa_style_key(self):
        """Retourne la valeur du champ Studio sur le client."""
        self.ensure_one()
        # Champ Studio sur res.partner
        return (self.partner_id.x_studio_style_de_devis or "").strip()

    def _get_signa_report_xmlid(self):
        """Choisit le rapport (ir.actions.report) à utiliser selon le style client."""
        self.ensure_one()
        style = self._get_signa_style_key()

        xmlid_map = {
            "SignaSolution": "signa_quote_styles.action_report_saleorder_signasolution",
            "SignaParc": "signa_quote_styles.action_report_saleorder_signaparc",
            "SignaGolf": "signa_quote_styles.action_report_saleorder_signagolf",
            "SignaIndustrie": "signa_quote_styles.action_report_saleorder_signaindustrie",
        }
        return xmlid_map.get(style, "signa_quote_styles.action_report_saleorder_signasolution")

    def _get_signa_mail_template_xmlid(self):
        """Choisit le modèle d'email à utiliser dans l'assistant d'envoi de devis."""
        self.ensure_one()
        style = self._get_signa_style_key()

        xmlid_map = {
            "SignaSolution": "signa_quote_styles.email_template_sale_quotation_signasolution",
            "SignaParc": "signa_quote_styles.email_template_sale_quotation_signaparc",
            "SignaGolf": "signa_quote_styles.email_template_sale_quotation_signagolf",
            "SignaIndustrie": "signa_quote_styles.email_template_sale_quotation_signaindustrie",
        }
        return xmlid_map.get(style, "signa_quote_styles.email_template_sale_quotation_signasolution")

    def action_print_quotation(self):
        """Remplace l'impression standard (bouton Imprimer/Devis).

        Important : on garde le même nom de méthode que le standard,
        donc tout appel (bouton, action, automatisme) passera ici.
        """
        self.ensure_one()
        report_action = self.env.ref(self._get_signa_report_xmlid())
        lang = self.partner_id.lang or self.env.context.get('lang')
        return report_action.with_context(lang=lang).report_action(self)

    def action_quotation_send(self):
        """Remplace automatiquement le modèle d'email utilisé par 'Envoyer par email' (option 1)."""
        self.ensure_one()
        action = super().action_quotation_send()
        template = self.env.ref(self._get_signa_mail_template_xmlid())
        # Force le template dans l'assistant d'email
        action_ctx = dict(action.get("context", {}) or {})
        action_ctx.update({
            "default_template_id": template.id,
            "default_use_template": True,
        })
        action["context"] = action_ctx
        return action
