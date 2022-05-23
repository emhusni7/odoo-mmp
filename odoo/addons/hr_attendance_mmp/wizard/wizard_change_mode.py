from odoo import fields, models

class WizChangeMode(models.Model):
    _name = "wiz.change.mode"

    pwd = fields.Char("Password", required=1)
    mode = fields.Selection([('in','In'),('out','Out')],string="Mode", required=1)

    def change_mode(self):
        result = self.env.user._check_credentials(self.pwd, {})
        self.env.user.type_kios = self.mode
        return {
            'type': 'ir.actions.client',
            'tag': 'hr_attendance_kiosk_mode'
        }


WizChangeMode