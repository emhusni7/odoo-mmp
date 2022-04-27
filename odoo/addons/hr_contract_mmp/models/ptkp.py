from odoo import models, fields, api
from odoo.exceptions import UserError

class PTKP(models.Model):
    _name = "ptkp"
    _inherit = ["mail.thread"]
    name = fields.Char("Kode", required=1)
    gol = fields.Selection([
        ('TK','Tidak Kawin(TK)'),
        ('K','Kawin (K)'),
        ('K/I','Kawin dg penghasilan istri digabung(K/I)')],'Golongan', required=1)
    tarif_ptkp = fields.Float("Tarif PTKP", digits=(16,2), default=0, required=1)

    def unlink(self):
        emp = self.sudo().env['hr.employee'].search([('ptk_id','in', self.ids)])
        if emp:
            raise UserError("Record Related with Master Employee")
        super(PTKP,self).unlink()
PTKP