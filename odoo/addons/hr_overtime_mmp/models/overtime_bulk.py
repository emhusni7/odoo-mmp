from odoo import models, fields, _, api
from odoo.exceptions import UserError

class OvertimeBulk(models.Model):
    _name = "hr.overtime.bulk"
    _inherit = ['mail.thread']
    _order = "date_from desc"

    name = fields.Char("Ref", default="/")
    department_id = fields.Many2one("hr.department", "Department", required=1)
    divisi_id = fields.Many2one("hr.divisi.mmp", "Division", domain="[('department_id','=',department_id)]")
    section_id = fields.Many2one("hr.job", "Section", domain="[('divisi_id','=', divisi_id)]")
    ov_type = fields.Many2one("overtime.type","Overtime Type", required=1)
    aplicant = fields.Many2one("hr.employee","Aplicant")
    manager_id = fields.Many2one("hr.employee","Manager")
    desc = fields.Text("Description")
    rest_hours = fields.Float("Rest Hours", default=0.0)
    date_from = fields.Datetime("Date From", default= fields.Datetime.now(), required=1)
    date_to = fields.Datetime("Date To", default= fields.Datetime.now(), required=1)
    overtime_ids = fields.One2many("hr.overtime", "overtime_bulk_id", "Overtime")
    type = fields.Selection([('cash', 'Cash'), ('leave', 'Time Off')], default="cash", required=True, string="Type")
    leave_id = fields.Many2one('hr.leave.allocation', string="Leave ID")
    state = fields.Selection([("draft", "New"),("confirm", "To Approve"), ("approved", "Approved"),("cancel","Reject")], string="State", default="draft", tracking=True)



    def calculate_overtime_amount(self):
        for x in self.overtime_ids:
            x._get_hour_amount()


    def action_confirm(self):
        if self.name == "/":
            self.name = self.env['ir.sequence'].next_by_code("hr.overtime.bulk")
        self.state = 'confirm'

    def action_reset(self):
        self.state = 'draft'

    def action_approve(self):
        self.state = 'approved'

    def action_cancel(self):
        self.state = "cancel"

    def unlink(self):
        for overtime in self.filtered(
                lambda overtime: overtime.state != 'draft'):
            raise UserError(
                _('You cannot delete TIL request which is not in draft state.'))
        return super(OvertimeBulk, self).unlink()


OvertimeBulk