from odoo import models, fields, api

class PTKP(models.Model):
    _name = "ptkp"
    _inherit = ["mail.thread"]
    name = fields.Char("Kode", required=1)
    gol = fields.Selection([
        ('TK','Tidak Kawin(TK)'),
        ('K','Kawin (K)'),
        ('K/I','Kawin dg penghasilan istri digabung(K/I)')],'Golongan', required=1)
    tarif_ptkp = fields.Float("Tarif PTKP", digits=(16,2), default=0, required=1)

PTKP