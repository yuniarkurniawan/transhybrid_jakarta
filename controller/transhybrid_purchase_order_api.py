from odoo import http
from odoo.http import request, Response
import dateutil.parser
import hashlib

import datetime
import dateutil.parser
import pytz
import json
import os
import base64

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


	@http.route("/po/<poId>/product",auth="none",csrf=False,type='http')
	def get_purchase_order_by_productId(self,poId,**values):


		print "aaaaaaaaaaaaaaaaaaaaaa"
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


	@http.route("/po/",auth="none",csrf=False,type='http')
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


			saleOrderData = saleOrderModel.sudo().search([('assign_to','=',dataUserToken.res_id.id),('state_new','in',(1,2,3))])
			for outData in saleOrderData:

				totalCountPo+=1

				new_dict_in = {}	
				new_dict_in['id'] = outData.id
				new_dict_in['name'] = outData.partner_id.name
				new_dict_in['date'] = self.get_converting_to_iso(outData.create_date)
				new_dict_in['total'] = outData.amount_total
				new_dict_in['confirmation_date'] = self.get_converting_to_iso(outData.confirmation_date)
				new_dict_in['assign_to'] = outData.assign_to.name

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
		
		'''


		saleOrderData = saleOrderModel.sudo().search([('state_new','in',(1,2,3))])
		for outData in saleOrderData:

				totalCountPo+=1

				new_dict_in = {}	
				new_dict_in['id'] = outData.id
				new_dict_in['name'] = outData.partner_id.name
				#new_dict_in['date'] = self.get_converting_to_iso(outData.create_date)
				new_dict_in['total'] = outData.amount_total
				#new_dict_in['confirmation_date'] = self.get_converting_to_iso(outData.confirmation_date)
				new_dict_in['assign_to'] = outData.assign_to.name

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



		return Response(json.dumps(output),headers=headers)


	@http.route("/product/<orderLineId>",auth="none",csrf=False,type='http')
	def get_purchase_order_service_by_product_id(self,orderLineId,**values):

		headers = {'Content-Type': 'application/json'}
		saleOrderLineModel = request.env['sale.order.line']


		print "bbbbbbbbbbbbbbbbbbbbbb"
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

		print " ======= ::: MASUK SINI...!"
		headerData = request.httprequest.headers		
		headers = {'Content-Type': 'application/json'}

		saleOrderLineImageModel = request.env['sale.order.line.image.model']
		saleOrderLineServiceModel = request.env['sale.order.line.service.model']

		poId = post.get('po_id')
		serviceId = post.get('service_id')
		step = post.get('step')

		print "POID : ", poId
		print "Service id :", serviceId
		print "STEP : ", step

		post_file = []
		for field_name, field_value in post.items():
			
			tmpString = field_name.strip().lower()
			if("image" in tmpString):
				print "ADA TEU"
				post_file.append(field_value)					
			


		out = {}
		
		try:
			

			tmpPercentage = 0

			if(step==1):
				tmpPercentage = 0
			elif(step==2):
				tmpPercentage = 25
			elif(step==3):
				tmpPercentage = 50
			elif(step==4):
				tmpPercentage = 75
			else:
				tmpPercentage = 100


			listNamaImage = []
			dataService = saleOrderLineServiceModel.sudo().search([('id','=',int(serviceId))])
			for outData in dataService:
				listNamaImage.append(str(outData.service_id.name))
				listNamaImage.append(" Product : ")
				listNamaImage.append(str(outData.sale_order_line_id.product_id.name))
				listNamaImage.append(" Di ")
				listNamaImage.append(str(outData.address))

				outData.sudo().state = int(step)
				outData.sudo().percentage = tmpPercentage
				outData.sudo().progress_bar = tmpPercentage


			for field_value_upload_files in post_file:
				
				add_photo_value = {
						'sale_order_line_id' : int(poId),
						'name'				 : ''.join(listNamaImage),
						'image'				 : base64.encodestring(field_value_upload_files.read()),
						'filename'			 : field_value_upload_files.filename,
						'order_line_service' : serviceId,					
					}
				

				saleOrderLineImageModel.sudo().create(add_photo_value)
				

			output = {
				'code': 200,
				'message':'Upload Image Succes',
			}

		except:

			output = {
				'code': 400,
				'message':'Upload Image Is Fail',
			}
		

		return Response(json.dumps(output),headers=headers)
