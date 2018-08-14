from odoo import models, fields, api,  _

class TranshybridGroupModel(models.Model):

	_name     = "res.groups"
	_inherit  = "res.groups"

	description		=	fields.Text('Description')
	
	