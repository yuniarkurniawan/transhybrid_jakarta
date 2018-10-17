from odoo import models, fields, api
from odoo import tools, _
from odoo.modules.module import get_module_resource
from odoo.exceptions import ValidationError
from string import capwords

import datetime


class TranshybridHREmployeeJob(models.Model):

    _inherit = 'hr.job'

    @api.model
    def _get_current_company_id(self):
        return [('company_id', '=', self.env.user.company_id.id)]
    

    parent_id = fields.Many2one('hr.job', string="Jabatan Atasan")
    child_ids = fields.One2many('hr.job', 'parent_id', string="Jabatan Bawahan", readonly=True)
    manager_id = fields.Many2one('hr.employee', string="Nama Atasan Langsung", readonly=True, compute='_set_manager_id')
    
    is_single = fields.Boolean(string="Jabatan hanya diisi satu orang", compute='_set_is_single')
    top_level = fields.Boolean(string="Jabatan Teratas")
    cross_department = fields.Boolean(string="Lintas Departemen", default=False)
    
    #group_id = fields.Many2one('res.groups', string="Hak Akses" ,domain=_get_current_company_id, )
    department_id = fields.Many2one('hr.department', domain=_get_current_company_id)

    _sql_constraints = [('job_name_unique', 'unique(name,company_id)', 'Nama Jabatan tidak boleh sama.')]


    @api.constrains('parent_id')
    def _constraint_parent_id(self):
        if self.parent_id == self.id: raise ValidationError(_('Jabatan atasan tidak boleh sama dengan jabatan ini'))

    @api.model
    def get_lowest_job(self):
        return self.search([('child_ids','=',False)]).ids

    @api.model
    def get_top(self,model_id):
        list_ids = []
        list_ids.append(model_id)
        
        department_id = self.env['hr.department'].browse(model_id)
        if department_id.parent_id:
            
            list_ids = list_ids + self.get_top(department_id.parent_id.id)
            
        return list_ids

    @api.one
    def get_child_job(self, depth = 0):
        depth += 1
        list_job_ids = []
        
        for job_id in self.child_ids:
            
            if len(job_id.child_ids):
                
                for deep_job_id in job_id.get_child_job(depth):
                    list_job_ids.append(deep_job_id[0])
            else :
                list_job_ids.append(job_id.id)
                

        return list_job_ids

    @api.one
    def get_clean_child_job(self):
        return self.ids + self.get_child_job()[0]

    @api.onchange('department_id')
    def onchange_department_id(self):
        
        department_ids = []
        department_ids = self.get_top(self.department_id.id)
        
        return {'domain': {'parent_id': ['|', '|',
            ('department_id', 'in', department_ids),
            ('top_level', '=', True),
            ('cross_department', '=', True),
        ]}}

    @api.one
    @api.depends('parent_id')
    def _set_manager_id(self):
        if self.parent_id:
            employee = self.env['hr.employee'].search([('job_id', '=', self.parent_id.id)])
            if len(employee.ids) > 1:
                employee = self.env['hr.employee'].search([('job_id', '=', self.parent_id.id)],limit=1)
            self.manager_id = employee.id

    @api.one
    @api.depends('child_ids')
    def _set_is_single(self):
        if self.child_ids and len(self.child_ids) > 0:
            self.is_single = True

    def to_title(self, value):
        string = value.split(' ')
        new_string = []
        for x in string:
            if x.islower():
                x = capwords(x)
            new_string.append(x)
        new_string = ' '.join(new_string)
        return new_string
    
    @api.model
    def create(self, vals):
        vals['name'] = self.to_title(vals['name'])
        return super(TranshybridHREmployeeJob, self).create(vals)

    @api.multi
    def write(self, vals):
        if 'name' in vals:
            vals['name'] = self.to_title(vals['name'])
        return super(TranshybridHREmployeeJob, self).write(vals)

    @api.model
    def get_m2m_job_list(self):
    # ambil job list, digroup-by department, untuk widget m2m job
        company_id = self.env.user.company_id.id
        result = {}
        departments = self.env['hr.department'].search([('company_id','=',company_id)])
        if len(departments) == 0: return result
        for department in departments:
            if len(department.jobs_ids) == 0: continue # hanya ambil department "daun" dari pohon department
            result[department.id] = {
                'name': department.name,
                'jobs': []
            }
            for job in department.jobs_ids:
                result[department.id]['jobs'].append([job.id,job.name])

        # Ambil jabatan yang tidak memiliki departemen
        job_dept_none_ids = self.search([('department_id', '=', False), ('company_id', '=', company_id)])
        result[0] = {
                'name': '',
                'jobs': []
            }
        for job in job_dept_none_ids:
            result[0]['jobs'].append([job.id, job.name])

        return result
