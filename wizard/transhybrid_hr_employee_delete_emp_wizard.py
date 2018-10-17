from odoo import models, fields, api


class TranshybridHREmployeeDeleteEMPWizard(models.TransientModel):
    _name = 'transhybrid.hr.employee.delete.emp.wizard'

    empl_id = fields.Many2one('hr.employee', string="Nama Karyawan")
    
    def del_empl(self):
        self.empl_id.unlink()