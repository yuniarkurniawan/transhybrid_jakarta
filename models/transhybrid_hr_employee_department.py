from odoo import models, fields, api

class TranshybridHREmployeeDepartment(models.Model):

	_inherit = 'hr.department'
	_order = 'id asc'	


	name 		= fields.Char(string="Nama Departemen")
	parent_id 	= fields.Many2one(string="Departemen Induk")
	start_date 	= fields.Date(string="Tanggal Mulai")

	note = fields.Selection([('start', 'Mulai Bekerja'),
                    ('promotion', 'Promosi'),
                    ('mutation', 'Mutasi'),
                    ('demotion', 'Demosi')
                    ],string="Keterangan")

	@api.one
	def _set_company_id(self):
		self.compnany_id = self.env.user.company_id.id

	@api.one
	@api.constrains('name')
	def _check_name(self):
		check = self.search([('name','=ilike',self.name),('id','!=',self.id)])
		if(len(check)>0):
			raise ValidationError(_('Name must be unique'))


	@api.one
	def _set_company_id(self):
		self.company_id = self.env.user.company_id.id

	@api.model
	def create(self,vals):
		vals['name'] = self.to_title(vals['name'])
		return super(TranshybridHREmployeeDepartment,self).create(vals)

	@api.multi
	def write(self,vals):
		if('name' in vals):
			vals['name'] = self.to_title(vals['name'])

		return super(TranshybridHREmployeeDepartment,self).write(vals)

	
	def to_title(self,value):

		string = value.split(' ')
		new_string = []
		for x in string:
			if(x.islower()):
				x = capwords(x)

			new_string.append(x)

		new_string = ' '.join(new_string)

		return new_string


	def del_dept_wizard(self):

		dept_id = self.id
		return {
			'name': 'Hapus Departemen',
			'type': 'ir.actions.act_window',
			'res_model': 'transhybrid.hr.employee.delete.dept.wizard',
			'view_mode': 'form',
			'view_type': 'form',
			'target': 'new',
			'context':{'default_dept_id': dept_id}
   		}