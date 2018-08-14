from odoo import api, fields, models, tools, _
import time
from datetime import datetime, date

class PurchaseOrderModel(models.Model):

	_name="purchase.order.model"
	_description = "Purchase Order Model"
	_order = "id asc"


	name 					=	fields.Char('Purchase Order Name',required=True)
	number					=	fields.Char('Purchase Order Number')
	purchase_order_date	 	=	fields.Datetime('Purchase Order Date',default=lambda *a: time.strftime('%Y-%m-%d'),required=True)
	customer         		=   fields.Many2one('res.partner','Vendor',domain=[('supplier','=',False)],required=True)
	
	state					=	fields.Selection([(1,'Prospect'),
											(2,'Deal'),
											(3,'New'),
											(4,'In Progress'),
											(5,'Monitoring'),
											],'State', default=1)
	description             =   fields.Text('Description',size=100)
	purchase_order_line_ids =   fields.One2many('purchase.order.line.model','purchase_order_id','Purchase Order Line',required=True)
	color 					= 	fields.Integer('Color Index', compute="change_colore_on_kanban")

	deal_state_date			=	fields.Datetime('Deal State Date')
	new_state_date			=	fields.Datetime('New State Date')
	in_progress_state_date	=	fields.Datetime('In Progress State Date')
	monitoring_state_date	=	fields.Datetime('Monitoring State Date')
	

	


	@api.model
	def create(self, values):

		customerPurchaseOrder = self.env['customer.purchase.order.model']
		purchaseOrderModel = self.env['purchase.order.model']
		idPurchaseOrder = super(PurchaseOrderModel, self).create(values)

		listImage = []
		customer_model_value = {}
		dataPool = purchaseOrderModel.search([('id','=',idPurchaseOrder.id)])
		
		for out in dataPool:	
			for outProduct in out.purchase_order_line_ids:
				for outImage in outProduct.purchase_order_line_image_ids:
					
					listImage.append((0,0,{
					
						'name':outImage.name,
						'image':outImage.image,
						'filename':outImage.filename,
					
					}))


				customer_model_value = {
						'name' : out.name + " - " + out.customer.name,
						'purchase_order' : out.id,
						'customer' : out.customer.id,
						'product_catalogue' : outProduct.product_thc.id,
						'price_per_unit':outProduct.price_per_unit,
						'quantity_buy':outProduct.quantity_buy,
						'total':outProduct.total,
						'customer_purchase_order_line_image_ids':listImage,
					}

				customerPurchaseOrder.create(customer_model_value)

				listImage[:] = []
				customer_model_value = {}

		return idPurchaseOrder


	@api.multi
	def action_deal(self):

		self.write({
				'state':2,
				'deal_state_date':date.today().strftime('%Y-%m-%d'),
			})

	@api.multi
	def action_new(self):

		self.write({
				'state':3,
				'new_state_date':date.today().strftime('%Y-%m-%d'),
			})

	@api.multi
	def action_in_progress(self):

		self.write({
				'state':4,
				'in_progress_state_date':date.today().strftime('%Y-%m-%d'),
			})


	@api.multi
	def action_in_monitoring(self):

		self.write({
				'state':5,
				'monitoring_state_date':date.today().strftime('%Y-%m-%d'),
			})

	
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
	

class PurchaseOrderLineModel(models.Model):

	_name="purchase.order.line.model"
	_description = "Purchase Order Line Model"
	_order = "id asc"


	name                    	 	= 	fields.Char('Purchase Order Line',size=50)
	purchase_order_id       	 	= 	fields.Many2one('purchase.order.model','Purchase Order',ondelete='cascade',required=True)

	product_thc             	 	= 	fields.Many2one('product.template','Product',required=True)
	price_per_unit          	 	= 	fields.Float('Price Per Unit',default=0.0,required=True)
	quantity_buy            	 	= 	fields.Float('Quantity Buy',default=0.0,required=True)

	total                   	 	=	fields.Float('Total',default=0.0,required=True)
	description             		=   fields.Text('Description',size=100)
	service_id						=	fields.Many2one('product.thc.service',required=True)

	total_service 					=	fields.Integer('Total Service',required=True)


	#purchase_order_line_item_ids 	= 	fields.One2many('purchase.order.line.item.model','purchase_order_line_id','Purchase Order Line Item',required=True)
	purchase_order_line_service_ids = 	fields.One2many('purchase.order.line.service.model','purchase_order_line_id','Purchase Order Line Item',required=True)
	

	purchase_order_line_image_ids	=	fields.One2many('purchase.order.line.image.model','purchase_order_line_id','Purchase Order Line Image')



	@api.onchange('total_service','service_id')
	def onchange_total_core(self):

		val = {}
		
		if(self.total_service):

			index = 1
			listDetailServicePickup = []

			while(index<=self.total_service):

				listDetailServicePickup.append((0,0,{
						'service_id' : self.service_id.id,
						'total_item_service' : 1,
						'state':1,
						#'address':,
					}))

				index+=1
				

			val = {
				'purchase_order_line_service_ids':listDetailServicePickup,
			}
			
		return {
			'value': val			
		}



	@api.onchange('product_thc')
	def get_unit_price(self):
		
		for obj in self.product_thc:
			self.price_per_unit = obj.revenue_year



	@api.onchange('quantity_buy')
	def get_total_value(self):

		for obj in self.product_thc:
			self.total = obj.revenue_year * self.quantity_buy


class PurchaseOrderLineServiceModel(models.Model):

	_name="purchase.order.line.service.model"
	_description = "Purchase Order Line Service Model"
	_order = "id asc"


	purchase_order_line_id 		= 	fields.Many2one('purchase.order.line.model','Purchase Order Line',ondelete='cascade',required=True)
	service_id					=	fields.Many2one('product.thc.service')
	address						=	fields.Text('Address')

	pic 						=	fields.Char('PIC')
	total_item_service     		= 	fields.Float('Total',required=True)



	@api.onchange('total_item_service')
	def onchange_total_core(self):

		val = {}
		
		if(self.total_item_service):

			index = 1
			listDetailServicePickup = []

			while(index<=self.total_item_service):

				listDetailServicePickup.append((0,0,{
						'service_id' : self.service_id.id,
						'total_item_service' : 1,
						'state':1,
						#'address':,
					}))

				index+=1
				

			val = {
				'purchase_order_line_id.purchase_order_line_service_ids':listDetailServicePickup,
			}
			
		return {
			'value': val			
		}



class PurchaseOrderLineImageModel(models.Model):
	
	_name = 'purchase.order.line.image.model'
	_description = 'Purchase Order Line Image Model'
	_order = 'id asc'

	purchase_order_line_id 	= 	fields.Many2one('purchase.order.line.model',ondelete="cascade")	
	name 					=  	fields.Char('Name')
	image 					=  	fields.Binary('Image')
	filename 				=  	fields.Char('Filename')




class PurchaseOrderLineItemModel(models.Model):

	_name="purchase.order.line.item.model"
	_description = "Purchase Order Line Item Model"
	_order = "id asc"


	purchase_order_line_id 		= 	fields.Many2one('purchase.order.line.model','Purchase Order Line',ondelete='cascade',required=True)
	item_model_id				=	fields.Many2one('item.model')

	price_per_item          	= 	fields.Float('Price Per Unit',required=True)
	quantity_item_buy           = 	fields.Float('Quantity Buy',required=True)

	total_item                 	= 	fields.Float('Total',required=True)


	@api.onchange('price_per_item','quantity_item_buy')
	def get_total_value(self):

		self.total_item = self.price_per_item * self.quantity_item_buy
	