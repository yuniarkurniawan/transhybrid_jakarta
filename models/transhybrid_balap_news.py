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
	product_name 			=	fields.Char('Product Name')
	hari 					=	fields.Char('Days')
	bulan					=	fields.Char('Month')
	tanggal					=	fields.Char('Days Date')
	tahun					=	fields.Char('Year')


	sale_order 				=	fields.Many2one('sale.order',required=True,domain=[('state_new','=',4)])
	sale_order_line			=	fields.Many2one('sale.order.line',string='Order Products',
									required=True)
	sale_order_line_service =	fields.Many2one('sale.order.line.service.model',required=True)


	# PELAKSANA
	user_name				=	fields.Char('User Name')
	user_phone				=	fields.Char('User Phone')
	user_email				=	fields.Char('User Email')
	user_jabatan			=	fields.Char('User Jabatan')

	# JASA
	customer_id 			=	fields.Char('Customer_id')
	service_name 			=	fields.Char('Service Name')
	item_service_name		=	fields.Char('Item Service Name')
	destination				=	fields.Char('Destination')

	# LOKASI PELANGGAN
	customer_name 			=	fields.Char('Customer_name')
	customer_address		=	fields.Text('Customer Address')
	customer_pic			=	fields.Char('Customer PIC')
	jabatan_customer_pic 	=   fields.Char('Jabatan PIC')
	customer_phone			=	fields.Char('Customer Phone')
	customer_fax			=	fields.Char('Customer Fax')
	customer_email 			=	fields.Char('Customer Email')
	


	longitude				=	fields.Float('Longitude',digits=(0,6),required=True,default=0.0)
	latitude 				=	fields.Float('Latitude',digits=(0,6),required=True,default=0.0)
	google_map 				=	fields.Char('Google Map')
	customer_position 		=	fields.Char('Customer Position')
	
	
	
	
	
	
	

	
