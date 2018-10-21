from odoo import models, fields, api,  _
from odoo.tools.safe_eval import safe_eval
from datetime import datetime, date, timedelta
from odoo.exceptions import ValidationError
from odoo.tools import DEFAULT_SERVER_DATETIME_FORMAT
import time
import dateutil.parser
import os

class TranshybridBalapNews(models.Model):

	_name     = "transhybrid.balap.news"

	name 					=	fields.Char('BAA Number')
	sale_order 				=	fields.Many2one('sale.order',required=True,domain=[('state_new','=',4)])
	sale_order_line			=	fields.Many2one('sale.order.line',string='Order Products',
									required=True)
	sale_order_line_service =	fields.Many2one('sale.order.line.service.model',required=True)

	customer_email 			=	fields.Char('Customer Email')
	customer_phone			=	fields.Char('Customer Phone')
	hari 					=	fields.Char('Days')

	customer_address		=	fields.Text('Customer Address')
	service_name 			=	fields.Char('Service Name')
	user_phone				=	fields.Char('User Phone')

	destination				=	fields.Char('Destination')
	customer_pic			=	fields.Char('Customer PC')
	bulan					=	fields.Char('Month')

	tanggal					=	fields.Char('Days Date')
	item_service_name		=	fields.Char('Item Service Name')
	customer_position 		=	fields.Char('Customer Position')
	
	tahun					=	fields.Char('Year')
	customer_fax			=	fields.Char('Customer Fax')
	customer_id 			=	fields.Char('Customer_id')
	user_name				=	fields.Char('User Name')
	
	product_name 			=	fields.Char('Product Name')
	longitude				=	fields.Float('Longitude',digits=(0,6),required=True,default=0.0)
	latitude 				=	fields.Float('Latitude',digits=(0,6),required=True,default=0.0)





	def get_month_converter(self, paramMonth):

		tmpOut = ""
		if(int(paramMonth)==1):
			tmpOut = "I"
		elif(int(paramMonth)==2):
			tmpOut = "II"
		elif(int(paramMonth)==3):
			tmpOut = "III"
		elif(int(paramMonth)==4):
			tmpOut = "IV"
		elif(int(paramMonth)==5):
			tmpOut = "V"
		elif(int(paramMonth)==6):
			tmpOut = "VI"
		elif(int(paramMonth)==7):
			tmpOut = "VII"
		elif(int(paramMonth)==8):
			tmpOut = "VIII"
		elif(int(paramMonth)==9):
			tmpOut = "IX"
		elif(int(paramMonth)==10):
			tmpOut = "X"
		elif(int(paramMonth)==11):
			tmpOut = "XI"
		else:
			tmpOut = "XII"

		return tmpOut



	@api.onchange('sale_order_line_service')
	def get_baa_number(self):

		tmpLoanNumber = []
		val = {}

		now = datetime.now()
		tmpYear = now.year
		tmpYear = str(tmpYear)

		tmpMonth = now.month
		tmpMonth = self.get_month_converter(tmpMonth)


		if(self.sale_order_line_service):
			serviceCode = self.sale_order_line_service.service_id.service_code
			serviceCode = str(serviceCode).lower()
			serviceCode = 'balap.'+ serviceCode

			nextNumber = self.env['ir.sequence'].get(str(serviceCode))
			nextNumber = str(nextNumber)

			tmpOutNumber = ""
			if(len(nextNumber)<=3):
				tmpOutNumber = str(nextNumber).zfill(3)
				tmpLoanNumber.append(tmpOutNumber)
			else:
				tmpOutNumber = str(nextNumber)
				tmpLoanNumber.append(tmpOutNumber)


			tmpLoanNumber.append("/BALAP-PROJECT/")
			tmpLoanNumber.append(str(self.sale_order_line_service.service_id.product_id.code))
			tmpLoanNumber.append("/")
			tmpLoanNumber.append(tmpMonth)
			tmpLoanNumber.append("/")
			tmpLoanNumber.append(tmpYear)

			outNumber = ''.join(tmpLoanNumber)
						
			val = {
				'name' : outNumber,
				'name_show' : outNumber,
			}
			

		return {
			'value' : val,
		}