from odoo import http
from odoo.http import request, Response
import dateutil.parser
import hashlib

import datetime
import time
import dateutil.parser
import pytz
import json
import os
import base64
import shutil

class TranshybridPurchaseOrderModelApi(http.Controller):

	def getDateTimeFromISO8601String(self,s):
		
		d = dateutil.parser.parse(s)
		
		return d


	def get_converting_to_iso(self,paramDate):

		userModel = request.env['res.users']
		dataUser = userModel.sudo().search([],limit = 1)
		tz = pytz.timezone(dataUser.partner_id.tz) or pytz.utc	
		date_from = pytz.utc.localize(datetime.datetime.strptime(paramDate, "%Y-%m-%d %H:%M:%S")).astimezone(tz)

		tmpOut = str(date_from)
		tmpDate = self.getDateTimeFromISO8601String(tmpOut)
		tmpDate = tmpDate.isoformat()

		return tmpDate


	def date_to_string(self,paramDate):

		tmpDate = ""

		tmpOutMe = datetime.datetime.strptime(paramDate,'%Y-%m-%d %H:%M:%S')
		tmpDate = datetime.datetime.strftime(tmpOutMe,'%d-%B-%Y')		

		return tmpDate


	def date_to_string_other(self,paramDate):

		tmpOutMe = datetime.datetime.strptime(paramDate,'%Y-%m-%d')
		tmpDate = datetime.datetime.strftime(tmpOutMe,'%d-%B-%Y')		

		return tmpDate



	@http.route("/po/<poId>/product",auth="none",csrf=False,type='http')
	def get_purchase_order_by_productId(self,poId,**values):

		headers = {'Content-Type': 'application/json'}
		saleOrderModel = request.env['sale.order']

		listSaleOrderLine = []
		totalCountProduct = 0

		try:

			saleOrderData = saleOrderModel.sudo().search([('state_new','in',(1,2,3)),('id','=',int(poId))])
			for outData in saleOrderData:

				for outDataLine in outData.order_line:

					totalCountProduct+=1

					new_dict_in = {}	
					new_dict_in['product_id'] = outDataLine.id
					new_dict_in['product_name'] = outDataLine.product_id.name
					new_dict_in['description'] = outDataLine.product_id.description
					
					new_dict_in['order_qty'] = outDataLine.product_uom_qty
					new_dict_in['unit_price'] = outDataLine.price_unit
					new_dict_in['taxes'] = outDataLine.tax_id.amount

					new_dict_in['subtotal'] = outDataLine.price_subtotal


					listProductService = []
					for outDataService in outDataLine.sale_order_line_service_ids:

						new_dict_service = {}

						new_dict_service['product_id'] = outDataService.id
						new_dict_service['service_name'] = outDataService.service_id.name
						new_dict_service['total_service'] = outDataService.total_item_service
						
						new_dict_service['person_charge'] = outDataService.pic
						new_dict_service['Address'] = outDataService.address

						listProductService.append(new_dict_service)


					new_dict_in['product_detail'] = listProductService
					listSaleOrderLine.append(new_dict_in)


			output = {
				'result':listSaleOrderLine,
				'code':200,
				'message':'OK',
				'meta':{
					'limit':10,
					'offset':5,
					'count':totalCountProduct
				}
			}


		except:
			output = {
				'result':listSaleOrderLine,
				'code':400,
				'message':'Data Not Found',
				'meta':{
					'limit':0,
					'offset':0,
					'count':totalCountProduct
				}
			}
		


		return Response(json.dumps(output),headers=headers)


	@http.route("/list/purchase_order",auth="none",csrf=False,type='http',method='GET')
	def get_purchase_order_by_user(self,**values):


		headers = {'Content-Type': 'application/json'}
		saleOrderModel = request.env['sale.order']

		headerData = request.httprequest.headers		
		headerToken =  headerData.get('Apptoken')
		headerTokenUser = headerData.get('token')

		listSaleOrder = []
		totalCountPo = 0

		'''
		try:


			if(self.check_app_token(headerToken)==False):
			
				output = {
					'result':{
						'code':401,
						'message':'API Key Is Not same'
					}
				}
				
				return Response(json.dumps(output),headers=headers)

		
			resUserTokenModel = request.env['res.users.token']
			dataUserToken = resUserTokenModel.sudo().search([('token_data','=',str(headerTokenUser))])
			
			if(len(dataUserToken)==0):
				
				output = {
					'result':{
						'code':401,
						'message':'Token Is Expired'
					}
				}
				
				return Response(json.dumps(output),headers=headers)

		except:
			
			output = {
				'result':listSaleOrder,
				'code': 400,
				'message':'Data Not Found',
				'meta':{
					'limit':0,
					'offset':0,
					'count':0
				}
			}
		
		'''


		try:
			
			saleOrderData = saleOrderModel.sudo().search([('state_new','in',(2,3))])
			for outData in saleOrderData:

					totalCountPo+=1

					new_dict_in = {}	
					new_dict_in['po_id'] = outData.id
					new_dict_in['po_number'] = outData.name
					new_dict_in['company_name'] = outData.partner_id.name

					new_dict_in['order_date'] = self.date_to_string(outData.date_order)
					new_dict_in['rfs_date'] = self.date_to_string(outData.rfs_date)

					tmpTotalOrderProduct = 0
					for outDataDetailProduct in outData.order_line:
						tmpTotalOrderProduct+=1

					new_dict_in['order_product'] = tmpTotalOrderProduct

					listSaleOrder.append(new_dict_in)


			output = {
				'result':listSaleOrder,
				'code':200,
				'message':'OK',
				'meta':{
					'limit':5,
					'offset':5,
					'count':totalCountPo
				}
			}
		
		
		except:

			output = {
				'result':listSaleOrder,
				'code': 400,
				'message':'Data Not Found',
				'meta':{
					'limit':0,
					'offset':0,
					'count':0
				}
			}
		

		return Response(json.dumps(output),headers=headers)


	'''
	@http.route("/prepare_upload_image/<itemServiceId>",auth="none",csrf=False,type='http')
	def get_prepare_upload_image(self,itemServiceId,**values):

		headers = {'Content-Type': 'application/json'}
		productServiceDetailPorgressModel = request.env['product.thc.service.detail.progress']


		listOutData = []
		new_dict_up = {}

		listProgressData = productServiceDetailPorgressModel.sudo().search([('item_service_detail_id','=',int(itemServiceId))])
		for outData in listProgressData:

			new_dict = {}
			new_dict['id'] = outData.id
			new_dict['progress_name'] = outData.name

			listOutData.append(new_dict)

		
		new_dict_up['list_progress'] = listOutData
		new_dict_up['item_service_detail_id'] = int(itemServiceId)

		output = {
			'result':new_dict_up,
			'code': 200,
			'message':'OK',
			'meta':{
				'limit':0,
				'offset':0,
				'count':0
			}
		}


		return Response(json.dumps(output),headers=headers)
	'''


	@http.route("/prepare_upload_image/<serviceId>",auth="none",csrf=False,type='http')
	def get_prepare_upload_image(self,serviceId,**values):

		headers = {'Content-Type': 'application/json'}

		saleOrderLineServiceModel  = request.env['sale.order.line.service.model']
		productServiceDetailPorgressModel = request.env['product.thc.service.detail.progress']
		productThcServicedetailModel = request.env['product.thc.service.detail']

		listOutData = []
		new_dict_up = {}

		output = {}
		tmpItemServiceId = ""
		tmpServiceId = ""


		try:
			outDataPool = saleOrderLineServiceModel.sudo().search([('id','=',int(serviceId))])
			for outSaleLineService in outDataPool:
				tmpItemServiceId = outSaleLineService.item_service_id.id
				tmpServiceId = outSaleLineService.service_id.id


			listProgressData = productServiceDetailPorgressModel.sudo().search([('item_service_detail_id','=',int(tmpItemServiceId))])
			for outData in listProgressData:

				new_dict = {}
				new_dict['id'] = outData.id
				new_dict['progress_name'] = outData.name + " (" + str(outData.progress_percentage) + ") %"

				listOutData.append(new_dict)



			new_dict_up['service_id'] = serviceId
			new_dict_up['service_ct_id'] = tmpServiceId
			new_dict_up['list_progress'] = listOutData
			new_dict_up['item_service_detail_id'] = int(tmpItemServiceId)

			output = {
				'result':new_dict_up,
				'code': 200,
				'message':'OK',
				'meta':{
					'limit':0,
					'offset':0,
					'count':0
				}
			}

		except:

			output = {
				'result':new_dict_up,
				'code': 200,
				'message':'OK',
				'meta':{
					'limit':0,
					'offset':0,
					'count':0
				}
			}


		return Response(json.dumps(output),headers=headers)



	'''
	@http.route("/prepare_upload_image/<itemServiceId>",auth="none",csrf=False,type='http')
	def get_prepare_upload_image(self,itemServiceId,**values):

		headers = {'Content-Type': 'application/json'}
		productServiceDetailPorgressModel = request.env['product.thc.service.detail.progress']
		productThcServicedetailModel = request.env['product.thc.service.detail']

		listOutData = []
		new_dict_up = {}

		listProgressData = productServiceDetailPorgressModel.sudo().search([('item_service_detail_id','=',int(itemServiceId))])
		for outData in listProgressData:

			new_dict = {}
			new_dict['id'] = outData.id
			new_dict['progress_name'] = outData.name

			listOutData.append(new_dict)

		tmpServiceId = ""
		dataPool = productThcServicedetailModel.sudo().search([('id','=',int(itemServiceId))])
		for outPool in dataPool:
			tmpServiceId = outPool.product_service_id.id


		new_dict_up['service_id'] = tmpServiceId
		new_dict_up['list_progress'] = listOutData
		new_dict_up['item_service_detail_id'] = int(itemServiceId)

		output = {
			'result':new_dict_up,
			'code': 200,
			'message':'OK',
			'meta':{
				'limit':0,
				'offset':0,
				'count':0
			}
		}


		return Response(json.dumps(output),headers=headers)
	'''



	@http.route("/detail_service/<serviceId>",auth="none",csrf=False,type='http')
	def get_detail_service(self,serviceId,**values):

		headers = {'Content-Type': 'application/json'}
		saleOrderLineServiceModel = request.env['sale.order.line.service.model']
		productServiceDetailPorgressModel = request.env['product.thc.service.detail.progress']

		listOutData = []

		saleOrderLineServiceData = saleOrderLineServiceModel.sudo().search([('id','=',int(serviceId))])
		for outData in saleOrderLineServiceData:
			
			new_dict = {}
			
			new_dict['company_name'] = outData.sale_order_line_id.order_id.partner_id.name
			new_dict['service_name'] = outData.service_id.name
			new_dict['item_service_name'] = outData.item_service_id.name

			new_dict['service_id'] = outData.id
			new_dict['service_ct_id'] = outData.service_id.id
			new_dict['item_service_id'] = outData.item_service_id.id

			new_dict['rfs_date'] = self.date_to_string(outData.sale_order_line_id.order_id.rfs_date)

			listOutdataServiceDetail = []
			for outDataServiceDetail in outData.sale_order_line_service_detail_ids:
				
				new_dict_in = {}
				new_dict_in['upload_date'] = self.date_to_string_other(outDataServiceDetail.upload_date)
				new_dict_in['description'] = outDataServiceDetail.description
				new_dict_in['progress'] = str(outDataServiceDetail.progress.progress_percentage) + " %"



				'''
				# ==== BEGIN GETTING PROGRESS BAR
				listProgress = []
				progressData = productServiceDetailPorgressModel.sudo().search([('item_service_detail_id','=',outData.item_service_id.id)])
				for outProgress in progressData:

					new_dict_progress = {}
					new_dict_progress['progres_id'] = outProgress.id
					new_dict_progress['progress_name'] = outProgress.name
					new_dict_progress['progress_percentage'] = outProgress.progress_percentage

					listProgress.append(new_dict_progress)
				
				new_dict_in['list_progress'] = listProgress
				# ==== END GETTING PROGRESS BAR
				'''


				listOutDataImage = []
				for outDataImage in outDataServiceDetail.sale_order_line_serive_image_ids:

					new_dict_in_image = {}
					
					if(outDataImage.address_image_name):
						#new_dict_in_image['address_image'] = self.get_base_path_image_data() + str(outDataImage.address_image_name)
						new_dict_in_image['address_image'] = self.get_address_base_progress_image() + str(outDataImage.address_image_name)
					else:
						new_dict_in_image['address_image'] = ""

					listOutDataImage.append(new_dict_in_image)

				
				new_dict_in['images'] = listOutDataImage
				listOutdataServiceDetail.append(new_dict_in)


			new_dict['list_detail_images'] = listOutdataServiceDetail
			listOutData.append(new_dict)



		output = {
				'result':listOutData,
				'code':200,
				'message':'OK',
				'meta':{
					'limit':5,
					'offset':5,
					'count':1
				}
			}


		return Response(json.dumps(output),headers=headers)


	def get_address_base_progress_image(self):
		
		path = os.path.join(os.path.dirname(os.path.abspath(__file__)))
		path = path.split('/')
		panjang = len(path)

		listAddres = []
		base_url = request.env['ir.config_parameter'].sudo().get_param('web.base.url')
		
		listAddres.append(str(base_url))
		listAddres.append("/")
		listAddres.append(str(path[panjang-2]))
		listAddres.append("/static/upload_progress_image/")

		return ''.join(listAddres)


	def get_base_path_image_data(self):

		path = os.path.join(os.path.dirname(os.path.abspath(__file__)))
		path = path.split('/')
		panjang = len(path)


		listAddres = []     
		for out in path:
	
			if(str(out) == path[-1]):
				break

			listAddres.append(str(out))
			listAddres.append("/")


		listAddres.append("static/upload_progress_image/")

		return ''.join(listAddres)


	@http.route("/detail_service_upload_image",auth='none',csrf=False,type='http')
	def upload_service_image(self,**post):

		headerData = request.httprequest.headers		
		headers = {'Content-Type': 'application/json'}

		saleOrderLineServiceModel = request.env['sale.order.line.service.model']
		saleOrderLineServiceImageModel = request.env['sale.order.line.service.image.model']
		saleOrderLineServiceDetailModel = request.env['sale.order.line.service.detail.model']

		generatedNumberModel = request.env['transhybrid.generated.number']

		now = datetime.datetime.now()

		piss = datetime.datetime.strftime(now,'%Y-%m-%d %H:%M:%S')
		uploadDate = datetime.datetime.strftime(now,'%Y-%m-%d')
		

		'''
		date_1 = datetime.datetime.strptime(uploadDate, "%Y-%m-%d")
		end_date = date_1 + datetime.timedelta(days=10)
		print "END DATE : ", end_date
		uploadDate = end_date
		'''


		tmpYear = now.year
		tmpYear = str(tmpYear)
		tmpYear = tmpYear[2:4]
		tmpMonth = now.month
		listPoNumber = []

		description = post.get('description')
		progressId = post.get('progress_id')
		serviceId = post.get('service_id')
		
		output = {}


		dataPool = generatedNumberModel.sudo().search([('is_image','=',True),('year','=',int(tmpYear)),('month','=',int(tmpMonth))])
		tmpGenerateNumber = ""

		if(len(dataPool)==0):

			# data kosong
			dataGenerateValue = {
				'is_image' : True,
				'year' : int(tmpYear),
				'month' : int(tmpMonth),
				'last_number' : 1
			}

			listPoNumber.append(str(1).zfill(5))
			generatedNumberModel.sudo().create(dataGenerateValue)

		else:

			# data tidak kosong
			tmpOutNumber = 0
			for outData in dataPool:
				
				tmpOutNumber = outData.last_number
				tmpOutNumber+=1
				listPoNumber.append(str(tmpOutNumber).zfill(5))
				outData.sudo().last_number = tmpOutNumber

		tmpGenerateNumber = ''.join(listPoNumber)

            
		post_file = []
		for field_name, field_value in post.items():
			
			tmpString = field_name.strip().lower()
			if("image" in tmpString):
				post_file.append(field_value)



		now = datetime.datetime.now()
			
		tmpTahun = str(now.year)
		tmpBulan = str(now.month)
		tmpHari = str(now.day)


		# YANG MEMBEDAKAN ADALAH TANGGAL DAN SERVICE IDNYA UNTUK BISA ONE2MANY KE IMAGE
		dataPoolService = saleOrderLineServiceDetailModel.sudo().search([('sale_order_line_service_id','=',serviceId),('upload_date','=',uploadDate)])
		
		if(len(dataPoolService)<=0):

			# INPUT IMAGE BARU DENGAN TANGGAL YANG BARU			

			dataServiceDetailValue = {
				'sale_order_line_service_id' : serviceId,
				'progress' : progressId,
				'upload_date': uploadDate,
				'description' : description
			}

			dataServiceDetail = saleOrderLineServiceDetailModel.sudo().create(dataServiceDetailValue)
			
			# UPDATE PROGRESS BAR
			modelPool = saleOrderLineServiceModel.sudo().search([('id','=',int(serviceId))])
			for serviceData in modelPool:
				serviceData.item_service_progress = progressId



			filename = ""
			listDataImageInputData = []

			for field_value_upload_files in post_file:
				
				listFileName = []
				
				listFileName.append(tmpTahun)
				listFileName.append("_")
				listFileName.append(tmpBulan)
				listFileName.append("_")
				listFileName.append(tmpHari)
				listFileName.append("_")
				listFileName.append(tmpGenerateNumber)
				listFileName.append(".png")

				filename = ''.join(listFileName)

				listDataImageInputData.append((0,0,{
						'sale_order_line_service_detail_id' : dataServiceDetail.id,
						'name'				 : field_value_upload_files.filename,
						'image'				 : base64.encodestring(field_value_upload_files.read()),
						'filename'			 : field_value_upload_files.filename,	
						'address_image_name' : filename,	
					}))

			dataServiceDetail.sudo().sale_order_line_serive_image_ids = listDataImageInputData	
			
			dataImagePool = saleOrderLineServiceImageModel.sudo().search([('sale_order_line_service_detail_id','=',dataServiceDetail.id)])
			for outPool in dataImagePool:

				imgdata = base64.decodestring(outPool.image)
				
				with open(filename, 'wb') as f:
				    f.write(imgdata)


				dst = str(self.get_base_path_image_data())
				shutil.move(filename, dst)

				listFileName[:] = []


		else:

			
			# UPDATE IMAGE BARU
			for outMe in dataPoolService:

				# UPDATE PROGRESS BAR
				modelPool = saleOrderLineServiceModel.sudo().search([('id','=',int(serviceId))])
				for serviceData in modelPool:
					serviceData.item_service_progress = progressId


				filename = ""
				listDataImageInputData = []

				for field_value_upload_files in post_file:
					
					listFileName = []
					
					listFileName.append(tmpTahun)
					listFileName.append("_")
					listFileName.append(tmpBulan)
					listFileName.append("_")
					listFileName.append(tmpHari)
					listFileName.append("_")
					listFileName.append(tmpGenerateNumber)
					listFileName.append(".png")

					filename = ''.join(listFileName)

					listDataImageInputData.append((0,0,{
							'sale_order_line_service_detail_id' : outMe.id,
							'name'				 : field_value_upload_files.filename,
							'image'				 : base64.encodestring(field_value_upload_files.read()),
							'filename'			 : field_value_upload_files.filename,	
							'address_image_name' : filename,	
						}))

				outMe.sudo().sale_order_line_serive_image_ids = listDataImageInputData	
				
				
				dataImagePool = saleOrderLineServiceImageModel.sudo().search([('sale_order_line_service_detail_id','=',outMe.id)],limit=1,order="id desc")
				for outPool in dataImagePool:

					imgdata = base64.decodestring(outPool.image)
					
					with open(filename, 'wb') as f:
					    f.write(imgdata)


					dst = str(self.get_base_path_image_data())
					shutil.move(filename, dst)

					listFileName[:] = []
				

		output = {
			'code': 200,
			'message':'Upload Image Succes',
		}
		

		return Response(json.dumps(output),headers=headers)




	'''

	@http.route("/detail_service_upload_image",auth='none',csrf=False,type='http')
	def upload_service_image_original(self,**post):

		headerData = request.httprequest.headers		
		headers = {'Content-Type': 'application/json'}

		saleOrderLineServiceModel = request.env['sale.order.line.service.model']
		saleOrderLineServiceImageModel = request.env['sale.order.line.service.image.model']
		saleOrderLineServiceDetailModel = request.env['sale.order.line.service.detail.model']

		generatedNumberModel = request.env['transhybrid.generated.number']

		now = datetime.datetime.now()
		tmpYear = now.year
		tmpYear = str(tmpYear)
		tmpYear = tmpYear[2:4]
		tmpMonth = now.month
		listPoNumber = []

		description = post.get('description')
		progressId = post.get('progress_id')
		serviceId = post.get('service_id')
		
		dataPool = generatedNumberModel.sudo().search([('is_image','=',True),('year','=',int(tmpYear)),('month','=',int(tmpMonth))])
		tmpGenerateNumber = ""

		if(len(dataPool)==0):

			# data kosong
			dataGenerateValue = {
				'is_image' : True,
				'year' : int(tmpYear),
				'month' : int(tmpMonth),
				'last_number' : 1
			}

			listPoNumber.append(str(1).zfill(5))
			generatedNumberModel.sudo().create(dataGenerateValue)

		else:

			# data tidak kosong
			tmpOutNumber = 0
			for outData in dataPool:
				
				tmpOutNumber = outData.last_number
				tmpOutNumber+=1
				listPoNumber.append(str(tmpOutNumber).zfill(5))
				outData.sudo().last_number = tmpOutNumber

		tmpGenerateNumber = ''.join(listPoNumber)

            
		post_file = []
		for field_name, field_value in post.items():
			
			tmpString = field_name.strip().lower()
			if("image" in tmpString):
				post_file.append(field_value)					
			

		now = datetime.datetime.now()
		
		tmpTahun = str(now.year)
		tmpBulan = str(now.month)
		tmpHari = str(now.day)

		dataServiceDetailValue = {
			'sale_order_line_service_id' : serviceId,
			'progress' : progressId,
			'description' : description
		}

		dataServiceDetail = saleOrderLineServiceDetailModel.sudo().create(dataServiceDetailValue)
		
		# UPDATE PROGRESS BAR
		modelPool = saleOrderLineServiceModel.sudo().search([('id','=',int(serviceId))])
		for serviceData in modelPool:
			serviceData.item_service_progress = progressId



		filename = ""
		listDataImageInputData = []

		for field_value_upload_files in post_file:
			
			listFileName = []
			
			listFileName.append(tmpTahun)
			listFileName.append("_")
			listFileName.append(tmpBulan)
			listFileName.append("_")
			listFileName.append(tmpHari)
			listFileName.append("_")
			listFileName.append(tmpGenerateNumber)
			listFileName.append(".png")

			filename = ''.join(listFileName)

			listDataImageInputData.append((0,0,{
					'sale_order_line_service_detail_id' : dataServiceDetail.id,
					'name'				 : field_value_upload_files.filename,
					'image'				 : base64.encodestring(field_value_upload_files.read()),
					'filename'			 : field_value_upload_files.filename,	
					'address_image_name' : filename,	
				}))

			
		dataServiceDetail.sudo().sale_order_line_serive_image_ids = listDataImageInputData	
		
		dataImagePool = saleOrderLineServiceImageModel.sudo().search([('sale_order_line_service_detail_id','=',dataServiceDetail.id)])
		for outPool in dataImagePool:

			imgdata = base64.decodestring(outPool.image)
			
			with open(filename, 'wb') as f:
			    f.write(imgdata)


			dst = str(self.get_base_path_image_data())
			shutil.move(filename, dst)

			listFileName[:] = []
		

		output = {
			'code': 200,
			'message':'Upload Image Succes',
		}

		return Response(json.dumps(output),headers=headers)

	@http.route("/detail_service_upload_image",auth='none',csrf=False,type='http')
	def upload_service_image(self,**post):

		headerData = request.httprequest.headers		
		headers = {'Content-Type': 'application/json'}

		saleOrderLineServiceImageModel = request.env['sale.order.line.service.image.model']
		generatedNumberModel = request.env['transhybrid.generated.number']

		now = datetime.datetime.now()
		tmpYear = now.year
		tmpYear = str(tmpYear)
		tmpYear = tmpYear[2:4]
		tmpMonth = now.month
		listPoNumber = []

		description = post.get('description')
		progressId = post.get('progress_id')
		serviceId = post.get('service_id')
		
		dataPool = generatedNumberModel.sudo().search([('is_image','=',True),('year','=',int(tmpYear)),('month','=',int(tmpMonth))])
		tmpGenerateNumber = ""

		if(len(dataPool)==0):

			# data kosong
			dataGenerateValue = {
				'is_image' : True,
				'year' : int(tmpYear),
				'month' : int(tmpMonth),
				'last_number' : 1
			}

			listPoNumber.append(str(1).zfill(5))
			generatedNumberModel.sudo().create(dataGenerateValue)

		else:

			# data tidak kosong
			tmpOutNumber = 0
			for outData in dataPool:
				
				tmpOutNumber = outData.last_number
				tmpOutNumber+=1
				listPoNumber.append(str(tmpOutNumber).zfill(5))
				outData.sudo().last_number = tmpOutNumber

		tmpGenerateNumber = ''.join(listPoNumber)

            
		post_file = []
		for field_name, field_value in post.items():
			
			tmpString = field_name.strip().lower()
			if("image" in tmpString):
				post_file.append(field_value)					
			

		now = datetime.datetime.now()
		
		tmpTahun = str(now.year)
		tmpBulan = str(now.month)
		tmpHari = str(now.day)

		filename = ""

		for field_value_upload_files in post_file:
			
			listFileName = []
			
			listFileName.append(tmpTahun)
			listFileName.append("_")
			listFileName.append(tmpBulan)
			listFileName.append("_")
			listFileName.append(tmpHari)
			listFileName.append("_")
			listFileName.append(tmpGenerateNumber)
			listFileName.append(".png")

			filename = ''.join(listFileName)

			add_photo_value = {
					#'sale_order_line_service_detail_id' : int(serviceId),
					#'name'				 : filename,
					'name'				 : field_value_upload_files.filename,
					'image'				 : base64.encodestring(field_value_upload_files.read()),
					'filename'			 : field_value_upload_files.filename,	
					'address_image_name' : filename,				
				}
			
			
		idImage = saleOrderLineServiceImageModel.sudo().create(add_photo_value)
		dataImagePool = saleOrderLineServiceImageModel.sudo().search([('id','=',int(idImage))])
		for outPool in dataImagePool:

			print " ==== ", outPool
			#outPool.sudo().sale_order_line_service_detail_id.description = description
			#outPool.sudo().sale_order_line_service_detail_id.progress = progressId
			
			imgdata = base64.decodestring(outPool.image)
			
			with open(filename, 'wb') as f:
			    f.write(imgdata)


			dst = str(self.get_base_path_image_data())
			shutil.move(filename, dst)

			listFileName[:] = []



		output = {
			'code': 200,
			'message':'Upload Image Succes',
		}

		return Response(json.dumps(output),headers=headers)




	@http.route("/detail_purchase_order/<purchaseOrderId>",auth="none",csrf=False,type='http')
	def get_detail_purchase_order(self,purchaseOrderId,**values):

		headers = {'Content-Type': 'application/json'}
		saleOrderModel = request.env['sale.order']
		listOutData = []
		totalCountPo = 1
		
		try:
			
			saleOrderData = saleOrderModel.sudo().search([('id','=',int(purchaseOrderId))])
			for outData in saleOrderData:
				
				new_dict = {}

				new_dict['po_number'] = outData.name
				new_dict['company_name'] = outData.partner_id.name
				new_dict['order_date'] = self.date_to_string(outData.date_order)	
				new_dict['rfs_date'] = self.date_to_string(outData.rfs_date)


				for outDataDetailProduct in outData.order_line:

					listHasilKoleksiData = []
					
					
					new_dict_in = {}
					new_dict_in['product_id'] = outDataDetailProduct.id
					new_dict_in['product_name'] = outDataDetailProduct.name


					listService = []
					
					for outDataDetailProductService in outDataDetailProduct.sale_order_line_service_ids:

						new_dict_in_service = {}
						new_dict_in_service['service_id'] = outDataDetailProductService.id
						new_dict_in_service['service_name'] = outDataDetailProductService.service_id.name
						new_dict_in_service['item_service_name'] = outDataDetailProductService.item_service_id.name

						new_dict_in_service['address'] = outDataDetailProductService.address
						new_dict_in_service['progress'] = str(outDataDetailProductService.percentage) + " %"

						listService.append(new_dict_in_service)
					

					new_dict_in['detail_service'] = listService
					listHasilKoleksiData.append(new_dict_in)


					

					listNamaProduct = []
					listNamaProduct.append('product_detail_')
					
					tmpSentence = str(outDataDetailProduct.name)
					tmpSentence = tmpSentence.replace(" ","")
					tmpSentence = tmpSentence.lower()

					listNamaProduct.append(tmpSentence)
					outName = ''.join(listNamaProduct)

					new_dict[outName] = listHasilKoleksiData
					listNamaProduct[:]=[]


				listOutData.append(new_dict)

			output = {
				'result':listOutData,
				'code':200,
				'message':'OK',
				'meta':{
					'limit':5,
					'offset':5,
					'count':totalCountPo
				}
			}

		
		except:
			
			output = {
				'result':listOutData,
				'code': 400,
				'message':'Data Not Found',
				'meta':{
					'limit':0,
					'offset':0,
					'count':0
				}
			}

		

		return Response(json.dumps(output),headers=headers)
	'''



	
	@http.route("/detail_purchase_order/<purchaseOrderId>",auth="none",csrf=False,type='http')
	def get_detail_purchase_order(self,purchaseOrderId,**values):

		headers = {'Content-Type': 'application/json'}
		saleOrderModel = request.env['sale.order']
		listOutData = []
		totalCountPo = 1
		
		try:
			
			saleOrderData = saleOrderModel.sudo().search([('id','=',int(purchaseOrderId))])
			for outData in saleOrderData:
				
				new_dict = {}

				new_dict['po_number'] = outData.name
				new_dict['company_name'] = outData.partner_id.name
				new_dict['order_date'] = self.date_to_string(outData.date_order)
					
				new_dict['rfs_date'] = self.date_to_string(outData.rfs_date)

				listProdcutDetailPurchaseOrder = []
				for outDataDetailProduct in outData.order_line:

					new_dict_in = {}
					new_dict_in['product_id'] = outDataDetailProduct.id
					new_dict_in['product_name'] = outDataDetailProduct.name


					listService = []
					for outDataDetailProductService in outDataDetailProduct.sale_order_line_service_ids:

						new_dict_in_service = {}
						new_dict_in_service['service_id'] = outDataDetailProductService.id
						new_dict_in_service['service_name'] = outDataDetailProductService.service_id.name
						new_dict_in_service['item_service_name'] = outDataDetailProductService.item_service_id.name

						new_dict_in_service['address'] = outDataDetailProductService.address
						new_dict_in_service['progress'] = str(outDataDetailProductService.percentage) + " %"

						listService.append(new_dict_in_service)

					new_dict_in['detail_service'] = listService

					listProdcutDetailPurchaseOrder.append(new_dict_in)


				new_dict['product_detail'] = listProdcutDetailPurchaseOrder
				listOutData.append(new_dict)


			output = {
				'result':listOutData,
				'code':200,
				'message':'OK',
				'meta':{
					'limit':5,
					'offset':5,
					'count':totalCountPo
				}
			}

		
		except:
			
			output = {
				'result':listOutData,
				'code': 400,
				'message':'Data Not Found',
				'meta':{
					'limit':0,
					'offset':0,
					'count':0
				}
			}

		

		return Response(json.dumps(output),headers=headers)
		
	




































	@http.route("/product/<orderLineId>",auth="none",csrf=False,type='http')
	def get_purchase_order_service_by_product_id(self,orderLineId,**values):

		headers = {'Content-Type': 'application/json'}
		saleOrderLineModel = request.env['sale.order.line']

		output = {}
		listSaleOrderLineService = []
		totalCountOrderLineService = 0	

		try:
			
			saleOrderLineData = saleOrderLineModel.sudo().search([('id','=',int(orderLineId))])
			for outData in saleOrderLineData:

				for outDataService in outData.sale_order_line_service_ids:

					totalCountOrderLineService+=1

					new_dict_in = {}

					new_dict_in['product_id'] = outDataService.service_id.id
					new_dict_in['service_name'] = outDataService.service_id.name
					new_dict_in['total_service'] = outDataService.total_item_service
					
					new_dict_in['person_charge'] = outDataService.pic
					new_dict_in['Address'] = outDataService.address
					
					listSaleOrderLineService.append(new_dict_in)


			output = {
				'result':listSaleOrderLineService,
				'code':200,
				'message':'OK',
				'meta':{
					'limit':5,
					'offset':5,
					'count':totalCountOrderLineService
				}
			}

		except:

			output = {
				'result':listSaleOrderLineService,
				'code': 400,
				'message':'Data Not Found',
				'meta':{
					'limit':0,
					'offset':0,
					'count':0
				}
			}
		

		return Response(json.dumps(output),headers=headers)




	@http.route("/order/add-photo",auth='none',csrf=False,type='http')
	def addPhotoPurchaseOrder(self,**post):

		headerData = request.httprequest.headers		
		headers = {'Content-Type': 'application/json'}

		saleOrderLineImageModel = request.env['sale.order.line.image.model']
		saleOrderLineServiceModel = request.env['sale.order.line.service.model']

		poId = post.get('po_id')
		serviceId = post.get('service_id')
		step = post.get('step')

		todays = datetime.datetime.today()
		
		post_file = []
		for field_name, field_value in post.items():
			
			tmpString = field_name.strip().lower()
			if("image" in tmpString):
				post_file.append(field_value)					
			

		out = {}
		
		#try:
			

		tmpPercentage = 0

		if(step==1):
			tmpPercentage = 0
		elif(step==2):
			tmpPercentage = 10
		elif(step==3):
			tmpPercentage = 20
		elif(step==4):
			tmpPercentage = 25
		elif(step==5):
			tmpPercentage = 30
		elif(step==6):
			tmpPercentage = 45
		elif(step==7):
			tmpPercentage = 60
		elif(step==8):
			tmpPercentage = 80
		elif(step==9):
			tmpPercentage = 90
		else:
			tmpPercentage = 100


		listNamaImage = []
		listDescription = []

		listDescription.append(datetime.datetime.strftime(todays, "%Y-%m-%d %H:%M:%S"))
		listDescription.append("\n\n\n")
		listDescription.append("\r\r\r")
		listDescription.append("TEST")

		dataService = saleOrderLineServiceModel.sudo().search([('id','=',int(serviceId))])
		for outData in dataService:
			

			outData.sudo().state = int(step)
			outData.sudo().percentage = tmpPercentage
			outData.sudo().progress_bar = tmpPercentage


		for field_value_upload_files in post_file:
			
			add_photo_value = {
					'sale_order_line_id' : int(poId),
					'address'			 : outData.address,
					'name'				 : outData.service_id.name,
					'image'				 : base64.encodestring(field_value_upload_files.read()),
					'filename'			 : field_value_upload_files.filename,
					'description'		 : '\n'.join(listDescription),
					'order_line_service' : serviceId,					
				}
			

			saleOrderLineImageModel.sudo().create(add_photo_value)
			

		output = {
			'code': 200,
			'message':'Upload Image Succes',
		}

		'''
		except:

			output = {
				'code': 400,
				'message':'Upload Image Is Fail',
			}
		'''

		return Response(json.dumps(output),headers=headers)


	'''
	@http.route("/coba/firebase",auth='none',csrf=False,type='http')
	def addPhotoPurchaseOrder(self,**post):

		pass
	'''
