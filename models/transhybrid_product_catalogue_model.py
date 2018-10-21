from odoo import models, fields, api,  _
from datetime import datetime, date
from odoo.exceptions import ValidationError


class TranshybridProductCatalogueModel(models.Model):

	_name     = "product.template"
	_inherit  = "product.template"

	_order = "id asc"

	product_type				=	fields.Selection([(1,'Survey'),
											(2,'Implementation'),
											(3,'Maintenance'),
											],'Type', required=True, default=1)

	mrc_otp						=	fields.Selection([(1,'MRC'),
											(2,'OTP'),
											],'MRC/OTP', required=True, default=1)
	
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
	
	list_price_compute     		=   fields.Float('Compute New Price',compute='_compute_list_new_price',store=True)

	product_templete_line_ids	=	fields.One2many('product.thc.service','product_id')
	'''
	category_acceptance 		=	fields.Selection([(1,'Out Task'),
											(2,'Connectivity'),
											(3,'CPE'),
											],'Type', required=True, default=1)
	'''


	#flag_template_line_ids 		=	fields.Char('Flag Tempalte',compute='_compute_flag_template_ids')
	#flag_childs = fields.Char('Label XXX', compute='_compute_flag_childs')


	#@api.depends(product_templete_line_ids)


	@api.multi
	@api.depends('product_templete_line_ids')
	def _compute_list_new_price(self):

		tmpNewPrice = 0
		for row in self:
			for rowOrderline in row.product_templete_line_ids:
				for rowPrice in rowOrderline.product_service_line_ids:
					#print "CC"
					tmpNewPrice+=rowPrice.price

			row.list_price = tmpNewPrice
			row.list_price_compute = tmpNewPrice

    
	@api.onchange('volume_solution','price_solution','volume_deployment','price_deployment','volume_operation_maintenance','price_operation_maintenance')
	def get_revenue_year_value(self):
		
		self.revenue_year = (self.volume_solution * self.price_solution) + (self.volume_deployment * self.price_deployment) + (self.volume_operation_maintenance * self.price_operation_maintenance)

	'''
	@api.model
	def write(self,vals):

		if(len(vals['product_templete_line_ids'])<=0):
			raise ValidationError(_('Service cannot be empty.'))
		else:
			for out in vals['product_templete_line_ids']:
				if(len(out[2]['product_service_line_ids'])<=0):
					raise ValidationError(_('Item service detail cannot be empty.'))
				else:
					for outIn in out[2]['product_service_line_ids']:
						if(len(outIn[2]['product_service_line_progress_ids'])<=0):
							raise ValidationError(_('Progress percentage cannot be empty.'))


		return super(TranshybridProductCatalogueModel, self).write(vals)  
	'''


	@api.model
	def create(self, values):

		if(len(values['product_templete_line_ids'])<=0):
			raise ValidationError(_('Service cannot be empty.'))
		else:
			for out in values['product_templete_line_ids']:
				if(len(out[2]['product_service_line_ids'])<=0):
					raise ValidationError(_('Item service detail cannot be empty.'))
				else:
					for outIn in out[2]['product_service_line_ids']:
						if(len(outIn[2]['product_service_line_progress_ids'])<=0):
							raise ValidationError(_('Progress percentage cannot be empty.'))



			

		productModel = self.env['product.product']
		values['product_code'] = self.generate_product_catalogue_number(values['code'])
		

		'''
		tmpListPrice = 0
		for outDataServiceItem in values['product_templete_line_ids']:
			for outDataSercviceItemPrice in outDataServiceItem[2]['product_service_line_ids']:
				tmpListPrice+=outDataSercviceItemPrice[2]['price']

		values['list_price'] = tmpListPrice
		'''

		idTemplate = super(TranshybridProductCatalogueModel,self).create(values)
		
		tmpId = ""
		tmpListPrice = 0
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


	'''
	@api.multi
	def write(self, vals):

		productModel = self.env['product.product']
		productTemplateModel = self.env['product.template']
		productThcServiceModel = self.env['product.thc.service']

		tmpPrice = 0
		tmpHargaBaru = 0
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

					#if('product_service_line_ids' in outData[2]):
					#	for outPrice in outData[2]['product_service_line_ids']:
					#		tmpPrice+=outPrice[2]['price']
					

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

					
					#if(outData[0]==1):
					#	if('product_service_line_ids' in outData[2]):
					#		for pricing in outData[2]['product_service_line_ids']:
					#			tmpHargaBaru+=pricing[2]['price']

					#print "KALO INI....!", outData
					
					listNewData.append(outData)
				
				
			vals['product_templete_line_ids'] = listNewData

		
		#for price in self:
		#	tmpPrice+=price.list_price
		
		#print "HARGA ::: ", tmpPrice - tmpHargaBaru
		#vals['list_price'] = tmpPrice - tmpHargaBaru
		

		return super(TranshybridProductCatalogueModel, self).write(vals)
	'''

class TranshybridProductServiceModel(models.Model):

	_name = 'product.thc.service'
	_description = "Product Thc Service Model"
	_order = "id asc"


	product_id 					= 	fields.Many2one('product.template',ondelete="cascade")
	
	#product_product			 	=	fields.Many2one('Product.product')
	product_product 			= 	fields.Many2one(compute='_product_product_id', comodel_name='product.product', string='Product', store=True)

	need_email_notif			=	fields.Selection([(1,'No'),
											(2,'Yes'),
											],'Type', required=True, default=1)


	service_code 				=	fields.Char('Service Code',required=True)
	name 						=  	fields.Char('Name',required=True)
	product_service_line_ids	=	fields.One2many('product.thc.service.detail','product_service_id')
	description					=  	fields.Text('Description')
	
	_sql_constraints = [('service_code_unique', 'unique(service_code)', 'Service Code Can Not Be Same.')]


	@api.multi
	def write(self, vals):

		irSequenceModel = self.env['ir.sequence']
		
		if('service_code' in vals):

			# ========= PENGECEKAN IR.SEQUENCE
			# ==== BEGIN BAS
			tmpBAS = 'bas.' + str(vals['service_code']).lower()

			poolData = irSequenceModel.search([('name','=',tmpBAS)])
			if(poolData.id!=False):
				raise ValidationError(_('There Is Same Service Code In Sequence Number Configuration.'))


			# === BEGIN BAA
			tmpBAA = 'baa.' + str(vals['service_code']).lower()
			poolData = irSequenceModel.search([('name','=',tmpBAA)])
			if(poolData.id!=False):
				raise ValidationError(_('There Is Same Service Code In Sequence Number Configuration.'))


			# === BEGIN BAT
			tmpBAT = 'bat.' + str(vals['service_code']).lower()
			poolData = irSequenceModel.search([('name','=',tmpBAT)])
			if(poolData.id!=False):
				raise ValidationError(_('There Is Same Service Code In Sequence Number Configuration.'))


			# === BEGIN BAI
			tmpBAI = 'bai.' + str(vals['service_code']).lower()
			poolData = irSequenceModel.search([('name','=',tmpBAI)])
			if(poolData.id!=False):
				raise ValidationError(_('There Is Same Service Code In Sequence Number Configuration.'))



			# === BEGIN BALAP
			tmpBALAP = 'balap.' + str(vals['service_code']).lower()
			poolData = irSequenceModel.search([('name','=',tmpBALAP)])
			if(poolData.id!=False):
				raise ValidationError(_('There Is Same Service Code In Sequence Number Configuration.'))




			# =========== INPUT IR.SEQUENCE
			# ==== BEGIN BAS
			tmpBAS = 'bas.' + str(vals['service_code']).lower()
			valueSequence = {
				'name' : tmpBAS,
				'code' : tmpBAS,
			}
			irSequenceModel.create(valueSequence)


			# === BEGIN BAA
			tmpBAA = 'baa.' + str(vals['service_code']).lower()
			valueSequence = {
				'name' : tmpBAA,
				'code' : tmpBAA,
			}		
			irSequenceModel.create(valueSequence)


			# === BEGIN BAT
			tmpBAT = 'bat.' + str(vals['service_code']).lower()
			valueSequence = {
				'name' : tmpBAT,
				'code' : tmpBAT,
			}		
			irSequenceModel.create(valueSequence)


			# === BEGIN BAI
			tmpBAI = 'bai.' + str(vals['service_code']).lower()
			valueSequence = {
				'name' : tmpBAI,
				'code' : tmpBAI,
			}		
			irSequenceModel.create(valueSequence)


			# === BEGIN BALAP
			tmpBALAP = 'balap.' + str(vals['service_code']).lower()
			valueSequence = {
				'name' : tmpBALAP,
				'code' : tmpBALAP,
			}		
			irSequenceModel.create(valueSequence)



		return super(TranshybridProductServiceModel, self).write(vals)



	@api.model
	def create(self, values):

		irSequenceModel = self.env['ir.sequence']

		# ==== BEGIN BAS
		tmpBAS = 'bas.' + str(values['service_code']).lower()
		valueSequence = {
			'name' : tmpBAS,
			'code' : tmpBAS,
		}
		irSequenceModel.create(valueSequence)


		# === BEGIN BAA
		tmpBAA = 'baa.' + str(values['service_code']).lower()
		valueSequence = {
			'name' : tmpBAA,
			'code' : tmpBAA,
		}		
		irSequenceModel.create(valueSequence)


		# === BEGIN BAT
		tmpBAT = 'bat.' + str(values['service_code']).lower()
		valueSequence = {
			'name' : tmpBAT,
			'code' : tmpBAT,
		}		
		irSequenceModel.create(valueSequence)


		# === BEGIN BAI
		tmpBAI = 'bai.' + str(values['service_code']).lower()
		valueSequence = {
			'name' : tmpBAI,
			'code' : tmpBAI,
		}		
		irSequenceModel.create(valueSequence)


		# === BEGIN BALAP
		tmpBALAP = 'balap.' + str(values['service_code']).lower()
		valueSequence = {
			'name' : tmpBALAP,
			'code' : tmpBALAP,
		}		
		irSequenceModel.create(valueSequence)


		return super(TranshybridProductServiceModel,self).create(values)


	@api.depends('product_id')
	def _product_product_id(self):

		productModel = self.env['product.product']		
		tmpId = ""

		for row in self:

			dataProductPool = productModel.search([('product_tmpl_id','=',row.product_id.id)],limit=1)
			for outData in dataProductPool:
				tmpId = outData.id

			row.product_product = tmpId

			


class TranshybridProductServiceDetailModel(models.Model):	

	_name = 'product.thc.service.detail'
	_description = "Product Thc Service Detail Model"
	_order = "id asc"

	product_service_id 		=	fields.Many2one('product.thc.service',ondelete="cascade")
	service_item_code		=	fields.Char('Service Item Code')
	name 					=	fields.Char('Name',required=True)
	price 					=	fields.Float('Price',required=True)
	product_service_line_progress_ids = fields.One2many('product.thc.service.detail.progress','item_service_detail_id')
	description 			=	fields.Text('Description')


class TranshybridProductServiceDetailProgressModel(models.Model):
	
	_name = 'product.thc.service.detail.progress'
	_description = "Product Thc Service Detail Progress Model"
	_order = "id asc"

	item_service_detail_id = fields.Many2one('product.thc.service.detail',ondelete="cascade")
	name 	=	fields.Char('Name',required=True)
	progress_percentage = fields.Integer('Progress Percentage',required=True)
	description 	=	fields.Text('Description')