# -*- coding: utf-8 -*-
{
    "name": "Signa - Styles de devis par client (Odoo 18)",
    "version": "18.0.1.0.0",
    "category": "Sales",
    "summary": "Change le header du devis selon res.partner.x_studio_style_de_devis (4 marques).",
    "author": "Signa",
    "license": "LGPL-3",
    "depends": ["sale", "web"],
    "data": [
        "report/signa_quote_styles.xml",
    ],
    "installable": True,
    "application": False,
}
