from odoo import models, fields

class TypeClient(models.Model):
    _name = 'res.partner.type'
    _description = 'Type de client'

    name = fields.Char(required=True)
    discount_rate = fields.Float(string="Remise (%)", default=0.0)
