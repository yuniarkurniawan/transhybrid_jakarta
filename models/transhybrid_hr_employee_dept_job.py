from odoo import models, fields, api
from odoo import tools, _
from odoo.modules.module import get_module_resource
from odoo.exceptions import ValidationError

class TranshybridHrEmployeeDeptJob(models.Model):
    _name = 'transhybrid.hr.employee.dept.job'

    name = fields.Char(string="Departemen", compute='_set_name_field')
    employee_id = fields.Many2one('hr.employee', string="Posisi", default=lambda self: self._context['default_employee_id'])

    def _get_current_company_id(self):
        return [('company_id', '=', self.env.user.company_id.id)]

    department = fields.Many2one('hr.department', string="Departemen", domain=lambda self: self._get_current_company_id())
    start_date = fields.Date(string="Tanggal Mulai", required=True, default=fields.Date.today())
    note_choices = [
        ('start_work', 'Mulai Bekerja'),
        ('promotion', 'Promosi'),
        ('mutation', 'Mutasi'),
        ('demotion', 'Demosi')
    ]
    note = fields.Selection(note_choices, string="Keterangan")
    job_id = fields.Many2one('hr.job', string="Jabatan")
    manager_one = fields.Many2one('hr.employee', string="Atasan 1", readonly=True, compute='_set_manager')
    manager_two = fields.Many2one('hr.employee', string="Atasan 2", readonly=True, compute='_set_manager')

    @api.depends('department')
    @api.one
    def _set_name_field(self):
        self.name = self.department.name



    @api.depends('job_id')
    def _set_manager(self):
        for row in self:
            if row.job_id and not row.job_id.top_level:
                manager = self.env['hr.employee'].search([('job_id','=',row.job_id.parent_id.id)])
                if manager:
                    row.manager_one = manager and manager[0] or None
                    man_one_job_id = manager[0].job_id
                    job = self.env['hr.job'].search([('id', '=', man_one_job_id.id)])
                    if job.parent_id:
                        employee = self.env['hr.employee'].search([('job_id', '=', job.parent_id.id)])
                        row.manager_two = employee and employee[0] or None
                    else:
                        row.manager_two = None
                else:
                    row.manager_one = None
                    row.manager_two = None
            else:
                row.manager_one = None
                row.manager_two = None


    @api.constrains('job_id')
    def _check_single_job(self):
        if self.job_id:
            job_position = self.env['hr.job'].sudo().search([('id', '=', self.job_id.id)])
            if job_position.is_single and len(job_position.employee_ids) > 0:
                if not job_position.id == self.employee_id.job_id.id:
                    employee_id = ""
                    for employee in job_position.employee_ids:
                        employee_id += employee.name

                    raise ValidationError("Jabatan %s hanya dapat diisi oleh satu orang dan sudah diisi oleh %s." % (self.job_id.name, employee_id))


    @api.multi
    def update_employee_job(self):
        for row in self:
            
            employee = self.env['hr.employee'].search([('id', '=', self.employee_id.id)])
            res_groups = self.env['res.groups']
            
            if not employee.sudo().job_id.id == row.job_id.id:
                updated_employee = employee.write({
                    'department_id': row.department.id,
                    'job_id': row.job_id.id,
                    'parent_id': self.manager_one.id,
                    'coach_id': self.manager_two.id
                })
            else :
                updated_employee = employee.write({
                    'department_id': row.department.id,
                    # 'job_id': row.job_id.id,
                    'parent_id': self.manager_one.id,
                    'coach_id': self.manager_two.id
                })
            if updated_employee:
                res_groups.sudo().change_group_by_job(self.employee_id.id, self.job_id.id, employee.job_id.id)
            
            return updated_employee
