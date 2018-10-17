from odoo import models, fields, api
from dateutil.parser import parse

class TranshybridHREmployeeContract(models.Model):
    _inherit = 'hr.employee.category'

    description 		=	fields.Text('Description')
    employee_line_ids 	= 	fields.One2many('hr.employee', 'category_employee', string='Employees')