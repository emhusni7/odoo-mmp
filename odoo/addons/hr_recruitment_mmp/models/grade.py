from odoo import models, fields, api, _

class Deparment(models.Model):
    _inherit = "hr.department"
    code = fields.Char("Code", size=2, required=1)

Deparment
class Grade(models.Model):
    _inherit = "hr.recruitment.degree"
    _rec_name = "sequence"
    name = fields.Char("Grade Code", required=True, translate=True)
    sequence = fields.Integer("Grade Name", default=1, required=True)

class Level(models.Model):
    _name = "hr.level"

    code = fields.Char("Level Code", required=1)
    name = fields.Char("Level Name", required=1)
    grade_categ = fields.Many2one("hr.recruitment.degree", "Grade Categ", required=1)

class FasilitasIT(models.Model):
    _name = "fasilitas.it.mmp"
    _rec_name = "complete_name"
    _order = "category,name"
    name = fields.Char("Nama", required=1)
    complete_name = fields.Char("Complete Name", compute='_get_name_func')
    category = fields.Selection([('hard','Hardware'),('soft','Software')],"Category", required=1)

    @api.depends('category', 'name')
    def _get_name_func(self):
        for x in self:
            val = _(dict(x.fields_get(allfields=['category'])['category']['selection'])[x.category])
            x.complete_name = '%s (%s)'%(x.name,val)

class WorkLokasi(models.Model):
    _inherit = "hr.work.location"
    _order = "category"

    name = fields.Char("Work Lokasi", required=1)
    category = fields.Selection([("do","Direct (Produksi) - Operator"),
                                 ("ds","Direct (Produksi) - Service"),
                                 ("ila","Indirect (Non-Produksi) - Lapangan A"),
                                 ("ilb","Indirect (Non-Produksi) - Lapangan B"),
                                 ("ik", "Indirect (Non-Produksi) - Kantor"),
                                 ], "Category", required=1)
    address_id = fields.Many2one('res.partner', required=False, string="Work Address",
                                 domain="['|', ('company_id', '=', False), ('company_id', '=', company_id)]")

