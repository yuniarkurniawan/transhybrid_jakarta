from odoo import models, fields, api
from odoo import tools, _
from odoo.modules.module import get_module_resource
from odoo.exceptions import ValidationError

class TranshybridHrEmployeeResign(models.Model):
    _name = 'transhybrid.hr.employee.resign'

    resign_date = fields.Date(string="Tanggal Resign", required=True, default=fields.Date.today())
    resign_reason = fields.Text(string="Alasan Terminasi", required=True)
    employee_id = fields.Many2one(
        'hr.employee', string="Nama Karyawan",
        default=lambda self: self._context['employee_id'],
        readonly=True
    )
    sure_inactive = fields.Boolean(string="Non-aktifkan Karyawan")

    @api.model
    def create(self, vals):
        if 'sure_inactive' in vals and vals['sure_inactive']:
            employee = self.env['hr.employee'].search([('id', '=', self._context['employee_id'])])
            user = self.env['res.users'].search([('id', '=', employee.user_id.id)])
            employee.active = False
            employee.job_id = False
            user.active = False
            user.groups_id = [(6, 0, [9])]
        else:
            raise ValidationError("Pastikan anda mencentang kolom Non-aktifkan Karyawan.")
        return super(TranshybridHrEmployeeResign, self).create(vals)