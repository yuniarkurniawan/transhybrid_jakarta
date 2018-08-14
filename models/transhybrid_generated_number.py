from odoo import models, fields, api,  _

class TranshybridGeneratedNumber(models.Model):

	_name 	= 'transhybrid.generated.number'
	_order 	= 'id asc'

	is_po  	=   fields.Boolean('Is Purchase Order Number')
	is_cust =	fields.Boolean('Is Customer Number')
	
	year 	=	fields.Integer('Year')
	month	=	fields.Integer('Month')

	last_number =	fields.Integer('Last Number')
	description	=	fields.Text('Description')