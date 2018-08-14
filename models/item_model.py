from odoo import models, fields, api,  _

class ItemModel(models.Model):

	_name="item.model"
	_description = "Item Model"
	_order = "id asc"

	name 				=	fields.Char('Item Name',required=True)
	image_small			=	fields.Binary('Item Image',required=True)
	brand				=	fields.Char('Item Brand')
	description			=	fields.Text('Item Description')
	
	
	