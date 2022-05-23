from odoo import models, fields

class Users(models.Model):
    _inherit = "res.users"
    type_kios = fields.Selection([("in","Check In"),("out","Check Out")],"In/Out")

Users