from odoo import models, fields, api

class TranshybridHREmployeeDeleteDeptWizard(models.TransientModel):
    
    _name = 'transhybrid.hr.employee.delete.dept.wizard'

    dept_id = fields.Many2one('hr.department', string="Nama Department")

    def del_dept(self):
        self.dept_id.active = False