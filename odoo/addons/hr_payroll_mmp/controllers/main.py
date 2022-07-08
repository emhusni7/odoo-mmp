from odoo import http
from odoo.http import content_disposition, request
import requests, base64


class PDFReport(http.Controller):

    @http.route(['/hr_payroll_mmp/report/<model("hr.payslip.run"):model>',], type='http', auth="user", csrf=False)
    def generate_report(self,model=None,**args):
        base_url = request.env['ir.config_parameter'].get_param('web.base.url')
        # attachment_obj = self.env['ir.attachment']
        url = 'http://localhost:8080/jasperserver/rest_v2/reports'
        # url = 'http://localhost:8080/jasperserver/rest_v2/resource'
        report = '/reports/interactive/MMP/payslip.pdf?id=%s'%(model.id)
        # Authorisation credentials:
        auth = ('jasperadmin', 'jasperadmin')
        s = requests.Session()
        r = s.get(url=url + report, auth=auth)
        return  request.make_response(
            r.content,
            headers=[
                ('Content-Type', 'application/octet-stream'),
                ('Content-Disposition', content_disposition('payslip' + '.pdf'))
            ]
        )