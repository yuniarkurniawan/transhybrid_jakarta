from odoo import models, fields, api,  _

class TranshybridRoleManagement(models.Model):

	_name     = "res.groups"
	_inherit  = "res.groups"

	description		=	fields.Text('Description')