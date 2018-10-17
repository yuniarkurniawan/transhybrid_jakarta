# -*- coding: utf-8 -*-

from odoo import models, fields, api, _


class TranshybridHREmployeeReligion(models.Model):
	_name = 'transhybrid.hr.employee.religion'
	_description = 'Data Master Agama'

	@api.model
	def _default_company_id(self):
		return self.env.user.company_id

	name = fields.Char(string="Nama Agama", required=True)
	company_id = fields.Many2one('res.company', string="Perusahaan", required=True, default=_default_company_id)
	description = fields.Text('Keterangan')