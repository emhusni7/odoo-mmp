from odoo import fields, models, api

class BPJSKesehatan(models.Model):
    _name = "bpjs.kesehatan.mmp"
    _inherit = ['mail.thread']

    name         = fields.Char("Name", required=1)
    company_rate = fields.Float("Rate Perusahaan (%)", digits=(16,2), default=0)
    employee_rate = fields.Float("Rate Pegawai (%)", digits=(16, 2), default=0)
    max_salary = fields.Float("Max. Gaji Bulanan", digits=(16,2), default=0)

BPJSKesehatan

class BPJSKetenagakerjaan(models.Model):
    _name = "bpjs.ketenagakerjaan.mmp"
    _inherit = ['mail.thread']

    name = fields.Char("Name", required=1)
    rate_jht = fields.Float("Rate JHT Perusahaan (%)",digits=(16,2))
    rate_jp  = fields.Float("Rate JP Perusahaan (%)", digits=(16,2))
    rate_jkk = fields.Float("Rate JKK (%)", digits=(16,2))
    rate_jkm = fields.Float("Rate JKM (%)", digits=(16,2))
    rate_jht_emp = fields.Float("Rate JHT Peserta(%)", digits=(16,2))
    rate_jp_emp = fields.Float("Rate JP Peserta(%)", digits=(16,2))
    max_tot_tunjangan = fields.Float("Max Total Tunjangan", digits=(16,2))
BPJSKetenagakerjaan