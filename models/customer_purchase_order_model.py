from odoo import api, fields, models, tools, _
import time
from datetime import datetime, date

class CustomerPurchaseOrderModel(models.Model):

	_name="customer.purchase.order.model"
	_description = "Customer Purchase Order Model"
	_order = "id asc"

	name 									=	fields.Char('Purchase Order Name',required=True)
	purchase_order         					=   fields.Many2one('purchase.order.model','Purchaes Order',required=True)
	product_catalogue						=	fields.Many2one('product.template','Product Catalogue',required=True)
	
	price_per_unit          	 			= 	fields.Float('Price Per Unit',default=0.0,required=True)
	quantity_buy            	 			= 	fields.Float('Quantity Buy',default=0.0,required=True)

	purchase_order_date	 					=	fields.Datetime('Purchase Order Date',related='purchase_order.purchase_order_date',required=True)
	state									=	fields.Selection([(1,'Prospect'),
													(2,'Deal'),
													(3,'New'),
													(4,'In Progress'),
													(5,'Monitoring'),
													],'State', related='purchase_order.state',default=1)
	total                   	 			=	fields.Float('Total',default=0.0,required=True)
	description             				=   fields.Text('Description',size=100)
	color 									= 	fields.Integer('Color Index', compute="change_colore_on_kanban")

	customer         						=   fields.Many2one('res.partner','Customer',domain=[('supplier','=',False)],required=True)
	customer_purchase_order_line_image_ids	=	fields.One2many('customer.purchase.order.line.image.model','customer_purchase_order_id','Customer Purchase Order Line Image')


	def change_colore_on_kanban(self):
	 
		for record in self:
			 color = 0
			 if record.state == 1:
				 color = 1
			 elif record.state == 2:
				 color = 2
			 elif record.state == 3:
				 color = 3
			 elif record.state == 4:
				 color = 4
			 else:
				 color=5

			 record.color = color


class CustomerPurchaseOrderLineImageModel(models.Model):
	
	_name = 'customer.purchase.order.line.image.model'
	_description = 'Customer Purchase Order Line Image Model'
	_order = 'id asc'

	customer_purchase_order_id 	= 	fields.Many2one('customer.purchase.order.model',ondelete="cascade")	
	name 						=  	fields.Char('Name')
	image 						=  	fields.Binary('Image')
	filename 					=  	fields.Char('Filename')