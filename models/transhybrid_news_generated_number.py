from odoo import models, fields, api,  _

class TranshybridNewsGeneratedNumber(models.Model):

	_name 	= 'transhybrid.news.generated.number'
	_order 	= 'id asc'

	is_bas  	=   fields.Boolean('Berita Acara Survey')
	last_number =	fields.Integer('Last Number')
	description	=	fields.Text('Description')