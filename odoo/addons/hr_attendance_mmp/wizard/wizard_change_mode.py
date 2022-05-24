from odoo import fields, models

class WizChangeMode(models.TransientModel):
    _name = "wiz.change.mode"

    pwd = fields.Char("Password", required=1)
    mode = fields.Selection([('in','In'),('out','Out')],string="Mode", required=1, default= lambda self: self.env.user.type_kios == 'in' and 'out' or 'in')

    def change_mode(self):
        result = self.env.user._check_credentials(self.pwd, {})
        self.env.user.type_kios = self.mode
        return {
            'type': 'ir.actions.client',
            'tag': 'hr_attendance_kiosk_mode_mmp'
        }


WizChangeMode