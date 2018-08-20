from odoo import models, fields, api,  _
from datetime import datetime, date


class TranshybridProductCatalogueModel(models.Model):

	_name     = "product.template"
	_inherit  = "product.template"

	_order = "id asc"

	product_type				=	fields.Selection([(1,'Survey'),
											(2,'Implementation'),
											(3,'Maintenance'),
											],'Type', required=True, default=1)
	
	volume_solution				=	fields.Float('Volume Solution',digits=(0,2),default=0.0)
	price_solution				=	fields.Float('Price Solution',digits=(0,2),default=0.0)

	volume_deployment			=	fields.Float('Volume Deployment',digits=(0,2),default=0.0)
	price_deployment 			=	fields.Float('Price Deployment',digits=(0,2),default=0.0)

	volume_operation_maintenance	=	fields.Float('Volume Operation Maintenance',digits=(0,2),default=0.0)
	price_operation_maintenance	=	fields.Float('Price Operation Maintenance',digits=(0,2),default=0.0)

	revenue_year				=	fields.Float('Revenue Year')

	note						=	fields.Text('Note Product')
	benchmark					=	fields.Text('Benchmark Product')
	product_code				=	fields.Char('Product Code')
	code 						=	fields.Char('Code',required=True)

	product_templete_line_ids	=	fields.One2many('product.thc.service','product_id')
	

	@api.onchange('volume_solution','price_solution','volume_deployment','price_deployment','volume_operation_maintenance','price_operation_maintenance')
	def get_revenue_year_value(self):
		
		self.revenue_year = (self.volume_solution * self.price_solution) + (self.volume_deployment * self.price_deployment) + (self.volume_operation_maintenance * self.price_operation_maintenance)


	@api.model
	def create(self, values):

		productModel = self.env['product.product']
		values['product_code'] = self.generate_product_catalogue_number(values['code'])
		idTemplate = super(TranshybridProductCatalogueModel,self).create(values)


		tmpId = ""
		dataProductPool = productModel.search([('product_tmpl_id','=',idTemplate.id)])
		for outData in dataProductPool:
			tmpId = outData.id
		

		for outDataService in idTemplate.product_templete_line_ids:
			outDataService.product_product = tmpId

		return idTemplate


	@api.multi
	def generate_product_catalogue_number(self,tmpParamProductCode):

		now = datetime.now()
		generatedNumberModel = self.env['transhybrid.generated.number']
		listPoNumber = []

		tmpYear = now.year
		tmpYear = str(tmpYear)
		tmpYear = tmpYear[2:4]

		tmpMonth = now.month 
		dataPool = generatedNumberModel.search([('is_product','=',True),('year','=',int(tmpYear)),('month','=',int(tmpMonth))])


		listPoNumber.append(str(tmpParamProductCode))
		listPoNumber.append(str(tmpYear))
		listPoNumber.append(str(tmpMonth).zfill(2))

		if(len(dataPool)==0):
			
			# data kosong
			dataGenerateValue = {
				'is_product' : True,
				'year'  : int(tmpYear),
				'month' : int(tmpMonth),
				'last_number' : 1
			}
			
			listPoNumber.append(str(1).zfill(5))
			generatedNumberModel.create(dataGenerateValue)
		
		else:

			# data tidak kosong
			tmpOutNumber = 0
			for outData in dataPool:
				tmpOutNumber = outData.last_number

				tmpOutNumber+=1	
				listPoNumber.append(str(tmpOutNumber).zfill(5))
				outData.last_number = tmpOutNumber

		
		return ''.join(listPoNumber) 



	@api.multi
	def write(self, vals):

		productModel = self.env['product.product']
		productTemplateModel = self.env['product.template']
		productThcServiceModel = self.env['product.thc.service']

		if("product_templete_line_ids" in vals):

			tmpIdProduct = ""
			listNewData = []
			
			for outData in vals['product_templete_line_ids']:
				
				if(tmpIdProduct==""):

					dataProductPool = productModel.search([('product_tmpl_id','=',self.id)])
					for outDataIn in dataProductPool:
						tmpIdProduct = outDataIn.id	
					

				# === DATA BARU
				if(outData[0]==0):
					
					#[0, False, {u'name': u'TESTING', u'description': False}]					

					listMe = []
					new_dict = {}
					new_dict['name'] = outData[2]['name']
					new_dict['description'] = outData[2]['description']
					new_dict['product_product'] = tmpIdProduct

					
					listMe.append(0)
					listMe.append(False)
					listMe.append(new_dict)

					listNewData.append(listMe)
				
				else:

					listNewData.append(outData)
				
				
			vals['product_templete_line_ids'] = listNewData

		return super(TranshybridProductCatalogueModel, self).write(vals)


class TranshybridProductServiceModel(models.Model):

	_name = 'product.thc.service'
	_description = "Product Thc Service Model"
	_order = "id asc"


	product_id 					= 	fields.Many2one('product.template',ondelete="cascade")
	product_product			 	=	fields.Many2one('Product.product')
	name 						=  	fields.Char('Name',required=True)
	description					=  	fields.Text('Description')
	