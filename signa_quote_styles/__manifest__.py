# -*- coding: utf-8 -*-
{
    "name": "Signa - Styles de devis par client",
    "version": "18.0.1.0.18",
    "category": "Sales",
    "summary": "Impression et envoi automatique du bon style de devis selon le champ client x_studio_style_de_devis",
    "author": "Jean-Louis",
    "license": "OPL-1",
    "depends": ["sale", "mail"],
    "data": [
        "reports/report_saleorder_styles.xml",
        "reports/report_actions.xml",
        "reports/external_layout_roots.xml",
        "reports/brand_external_layouts.xml",
        "data/mail_templates.xml",
        "views/sale_order_view.xml",
    ],
    "installable": True,
    "application": False,
}
