from odoo import http
from odoo.http import content_disposition, request
import requests, base64


class PDFReport(http.Controller):

    @http.route(['/hr_payroll_mmp/report/<model("hr.payslip.run"):model>',], type='http', auth="user", csrf=False)
    def generate_report(self,model=None,**args):
        url = request.env['ir.config_parameter'].get_param('jasper.url')
        us_pwd = eval(request.env['ir.config_parameter'].get_param('jasper.user'))
        # attachment_obj = self.env['ir.attachment']

        # url = 'http://localhost:8080/jasperserver/rest_v2/resource'
        report = '/reports/interactive/MMP/payslip.pdf?id=%s'%(model.id)
        # Authorisation credentials:
        auth = (us_pwd.get('username'), us_pwd.get('password'))
        s = requests.Session()
        r = s.get(url=url + report, auth=auth)
        return  request.make_response(
            r.content,
            headers=[
                ('Content-Type', 'application/octet-stream'),
                ('Content-Disposition', content_disposition('payslip' + '.pdf'))
            ]
        )

    @http.route(['/hr_payroll_mmp/report_payroll/<model("wiz.payroll.report"):model>', ], type='http', auth="user", csrf=False)
    def report_monthly(self,model=None,**args):
        url = request.env['ir.config_parameter'].get_param('jasper.url')
        us_pwd = eval(request.env['ir.config_parameter'].get_param('jasper.user'))
        # url = 'http://localhost:8080/jasperserver/rest_v2/resource'
        report = '/reports/interactive/MMP/payroll_report_mmp.pdf?year=%s&month=%s&struct_id=%s' % (int(model.year),model.month,model.struct_id.id)
        # Authorisation credentials:
        auth = (us_pwd.get('username'), us_pwd.get('password'))
        s = requests.Session()
        r = s.get(url=url + report, auth=auth)
        return request.make_response(
            r.content,
            headers=[
                ('Content-Type', 'application/octet-stream'),
                ('Content-Disposition', content_disposition('monthly_payroll' + '.pdf'))
            ]
        )