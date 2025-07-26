{
    "name": "Remises tarifaires par type de client",
    "version": "1.0",
    "depends": ["sale"],
    "author": "Jean-Louis T.",
    "description": "Applique automatiquement une remise sur les devis en fonction du type de client.",
    "installable": True,
    "application": False,
    "data": [
        "views/type_client_views.xml",
        "views/res_partner_views.xml",
        "views/website_product_templates.xml",
        "views/website_product_list_templates.xml",
        "views/report_invoice_inherit.xml",
        "views/report_saleorder_inherit.xml",
    ],
}
