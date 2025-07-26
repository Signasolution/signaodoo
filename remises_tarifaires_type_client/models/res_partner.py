from odoo import models, fields

class ResPartner(models.Model):
    _inherit = 'res.partner'

    type_client_id = fields.Many2one('res.partner.type', string="Type de client")
